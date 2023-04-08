from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from poap.users.models import WalletUser


class WalletUserJWTAuthentication(JWTAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = WalletUser

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            wallet_id = validated_token["wallet_id"]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            wallet = self.user_model.objects.get(id=wallet_id)
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        if not wallet.is_active:
            raise AuthenticationFailed(_("User is inactive"), code="user_inactive")

        return wallet
