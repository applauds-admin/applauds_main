// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

error BalanceNotEnoughError(address tokenId);
error PayeeAddressError();
error PayeeConversionFullError();
error PayerRequestFullError();
error ConversionExistError(uint256 cId);
error ConversionNotExistError(uint256 cId);
error ConversionApprovedError(uint256 cId);
error ConversionNotApprovedError(uint256 cId);

contract ChatApprove is Ownable {
    uint256 public MAX_CONVERSATIONS = 10;
    uint256 public MAX_REQUESTS = 10;
    uint256 public REWARDS_FEE = 20;

    enum Status {
        Pending,
        Chatting
    }

    struct PayerConversation {
        address payer;
        address payee;
        address token;
        uint256 amount;
        uint256 createdAt;
        Status status;
        uint256[] relatedTasks;
    }

    struct Conversation {
        address payer;
        address token;
        uint256 amount;
        uint256 createdAt;
        Status status;
        uint256[] relatedTasks;
    }

    struct ConversationDetail {
        // conversationId => conversationDetail
        mapping(uint256 => Conversation) conversions;
        uint256 count;
    }

    struct Request {
        address payee;
        uint256 index;
    }

    struct RequestDetail {
        mapping(uint256 => Request) requests;
        uint256 count;
    }

    // user => conversationDetail
    mapping(address => ConversationDetail) public userConversations;
    // request list
    mapping(address => RequestDetail) public userRequests;

    function payeeConversions(
        address _payee
    ) public view returns (uint256, Conversation[] memory) {
        Conversation[] memory conversions = new Conversation[](
            userConversations[_payee].count
        );
        for (uint256 i = 0; i < userConversations[_payee].count; i++) {
            if (userConversations[_payee].conversions[i].payer != address(0)) {
                conversions[i] = userConversations[_payee].conversions[i];
            }
        }
        return (userConversations[_payee].count, conversions);
    }

    function payerRequests(
        address _payer
    ) public view returns (uint256, PayerConversation[] memory) {
        PayerConversation[] memory conversions = new PayerConversation[](
            userRequests[_payer].count
        );
        Conversation memory temp;
        for (uint256 i = 0; i < userRequests[_payer].count; i++) {
            address _payee = userRequests[_payer].requests[i].payee;
            uint256 _index = userRequests[_payer].requests[i].index;
            temp = userConversations[_payee].conversions[_index];
            conversions[i] = PayerConversation({
                payer: temp.payer,
                payee: _payee,
                token: temp.token,
                amount: temp.amount,
                createdAt: temp.createdAt,
                status: temp.status,
                relatedTasks: temp.relatedTasks
            });
        }
        return (userRequests[_payer].count, conversions);
    }

    function _conversationExist(
        address _payer,
        address _payee
    ) internal view returns (bool, uint256) {
        for (uint256 i = 0; i < MAX_CONVERSATIONS; i++) {
            if (userConversations[_payee].conversions[i].payer == _payer) {
                return (true, i);
            }
        }
        return (false, 0);
    }

    function _conversationSlotExist(
        address _payee
    ) internal view returns (bool, uint256) {
        for (uint256 i = 0; i < MAX_CONVERSATIONS; i++) {
            if (userConversations[_payee].conversions[i].payer == address(0)) {
                return (true, i);
            }
        }
        return (false, 0);
    }

    function _requestSlotExist(
        address _payer
    ) internal view returns (bool, uint256) {
        for (uint256 i = 0; i < MAX_REQUESTS; i++) {
            if (userRequests[_payer].requests[i].payee == address(0)) {
                return (true, i);
            }
        }
        return (false, 0);
    }

    function requestNewConversation(
        address _payee,
        address _token,
        uint256 _amount,
        uint256[] calldata _relatedTasks
    ) public {
        address _payer = msg.sender;
        if (_payee == _payer || _payee == address(0)) {
            revert PayeeAddressError();
        }

        (bool _exist, uint256 _cId) = _conversationExist(_payer, _payee);
        if (_exist == true) {
            revert ConversionExistError({cId: _cId});
        }

        IERC20 token = IERC20(_token);
        if (token.balanceOf(_payer) < _amount) {
            revert BalanceNotEnoughError({tokenId: _token});
        }

        (
            bool _cSlotExist,
            uint256 _newConversationIndex
        ) = _conversationSlotExist(_payee);
        if (_cSlotExist == false) {
            revert PayeeConversionFullError();
        }

        (bool _rSlotExist, uint256 _newRequestIndex) = _requestSlotExist(
            _payer
        );
        if (_rSlotExist == false) {
            revert PayerRequestFullError();
        }

        // Add to payee conversation array
        userConversations[_payee].conversions[
            _newConversationIndex
        ] = Conversation({
            payer: _payer,
            token: _token,
            amount: _amount,
            createdAt: block.timestamp,
            status: Status.Pending,
            relatedTasks: _relatedTasks
        });
        ++userConversations[_payee].count;
        // Add to payer request array
        userRequests[_payer].requests[_newRequestIndex] = Request({
            payee: _payee,
            index: _newConversationIndex
        });
        ++userRequests[_payer].count;

        // Transfer rewards
        token.transferFrom(_payer, address(this), _amount);
    }

    function _deletePayerRequestDetail(
        address _payer,
        address _payee
    ) internal returns (bool) {
        for (uint256 i = 0; i < userRequests[_payer].count; i++) {
            if (userRequests[_payer].requests[i].payee == _payee) {
                delete userRequests[_payer].requests[i];
                --userRequests[_payer].count;
                return true;
            }
        }
        return false;
    }

    function approveConversation(uint256 _cId) public {
        address _payee = msg.sender;
        Conversation storage _conversation = userConversations[_payee]
            .conversions[_cId];
        if (_conversation.payer == address(0)) {
            revert ConversionNotExistError({cId: _cId});
        }
        if (_conversation.status == Status.Chatting) {
            revert ConversionApprovedError({cId: _cId});
        }

        _conversation.status = Status.Chatting;
        // Delete payer request
        _deletePayerRequestDetail(_conversation.payer, _payee);

        // Transfer rewards
        IERC20 token = IERC20(_conversation.token);
        uint256 _feeAmount = (_conversation.amount * REWARDS_FEE) / 100;
        // Rewards
        token.transfer(_payee, _conversation.amount - _feeAmount);
        // Fee
        token.transfer(owner(), _feeAmount);
    }

    function endConversationByPayee(uint256 _cId) public {
        address _payee = msg.sender;
        Conversation memory _conversation = userConversations[_payee]
            .conversions[_cId];
        if (_conversation.payer == address(0)) {
            revert ConversionNotExistError({cId: _cId});
        }

        if (_conversation.status == Status.Pending) {
            // Delete payer request
            _deletePayerRequestDetail(_conversation.payer, _payee);
        }

        --userConversations[_payee].count;
        delete userConversations[_payee].conversions[_cId];
        // TODO: Add to history
    }

    function endConversationByPayer(address _payee) public {
        address _payer = msg.sender;
        if (_payee == msg.sender || _payee == address(0)) {
            revert PayeeAddressError();
        }

        (bool _exist, uint256 _cId) = _conversationExist(msg.sender, _payee);
        if (_exist == false) {
            revert ConversionNotExistError({cId: _cId});
        }

        Conversation memory _conversation = userConversations[_payee]
            .conversions[_cId];
        if (_conversation.status == Status.Pending) {
            // Delete payer request
            _deletePayerRequestDetail(_payer, _payee);
        }

        --userConversations[_payee].count;
        delete userConversations[_payee].conversions[_cId];
        // TODO: Add to history
    }
}
