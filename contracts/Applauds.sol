// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";

contract Applauds is ERC1155, Ownable, ERC1155Burnable, ERC1155Supply {
    string private _baseURI;

    mapping(uint256 => string) _tokenURI;
    mapping(uint256 => bool) _tokenTransferable;

    constructor() ERC1155("Applauds") {}

    function setURI(uint256 _tokenId, string memory _uri) public onlyOwner {
        // Set different URI for different token
        _tokenURI[_tokenId] = _uri;
    }

    function setBaseURI(string memory _uri) public onlyOwner {
        _baseURI = _uri;
    }

    function stringCompare(
        string memory str1,
        string memory str2
    ) public pure returns (bool) {
        if (bytes(str1).length != bytes(str2).length) {
            return false;
        }
        return
            keccak256(abi.encodePacked(str1)) ==
            keccak256(abi.encodePacked(str2));
    }

    function uri(
        uint256 _tokenId
    ) public view override returns (string memory) {
        if (stringCompare(_tokenURI[_tokenId], "")) {
            return
                string(
                    abi.encodePacked(
                        _baseURI,
                        Strings.toString(_tokenId),
                        ".json"
                    )
                );
        }
        return _tokenURI[_tokenId];
    }

    function setTransferable(
        uint256 _tokenId,
        bool _transferable
    ) public onlyOwner {
        _tokenTransferable[_tokenId] = _transferable;
    }

    function transferable(uint256 _tokenId) public view returns (bool) {
        return _tokenTransferable[_tokenId];
    }

    function mint(
        address account,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) public onlyOwner {
        _mint(account, id, amount, data);
    }

    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) public onlyOwner {
        _mintBatch(to, ids, amounts, data);
    }

    // The following functions are overrides required by Solidity.

    function _beforeTokenTransfer(
        address operator,
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) internal override(ERC1155, ERC1155Supply) {
        // Check token allow transfer
        if (to != address(0) && from != address(0)) {
            for (uint256 i = 0; i < ids.length; ++i) {
                uint256 id = ids[i];
                require(
                    _tokenTransferable[id],
                    "ERC1155: token not allow to transfer"
                );
            }
        }
        super._beforeTokenTransfer(operator, from, to, ids, amounts, data);
    }
}
