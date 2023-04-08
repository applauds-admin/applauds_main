import datetime
import secrets
import string

import eth_utils
from django.utils import timezone
from rest_framework import filters
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from siwe import SiweMessage

from .serializers import WalletVerifySerializer, WallerUserSerializer, WalletUserCreateSerializer
from ..models import WalletNonce, WalletUser
from ...core.api import CustomPagination

# SIGN_MESSAGE_PREFIX = "You are trying to login with nonce: "
ALPHANUMERICS = string.ascii_letters + string.digits


def generate_nonce() -> str:
    return "".join(secrets.choice(ALPHANUMERICS) for _ in range(11))


class UserRetrieveView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = WalletUser.objects.all()
    serializer_class = WallerUserSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["address", ]
    ordering_fields = ["created_at", "joined_count", "owned_count"]


class MeInfoView(APIView, UpdateModelMixin):
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated,)
    serializer_class = WallerUserSerializer

    def get(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data=self.serializer_class(request.user).data,
        )

    def put(self, request, *args, **kwargs):
        serializer = WalletUserCreateSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(status=status.HTTP_200_OK, data=self.serializer_class(user).data)


class Web3LoginNonce(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, address: str, *args, **kwargs):
        if not eth_utils.is_address(address):
            return Response(status=status.HTTP_404_NOT_FOUND)

        nonce, created = WalletNonce.objects.update_or_create(
            address=address,
            defaults={
                "nonce": generate_nonce(),
            },
        )
        return Response(
            status=status.HTTP_200_OK,
            data={"nonce": nonce.nonce},
        )


class Web3LoginVerify(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = WalletVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            message: SiweMessage = SiweMessage(serializer.validated_data["message"])
            nonce = WalletNonce.objects.get(
                address=message.address, nonce=message.nonce,
                # created_at__gte=timezone.now() - datetime.timedelta(minutes=15)
            )
            message.verify(signature=serializer.validated_data["signature"])
            wallet, created = WalletUser.objects.update_or_create(
                address=message.address,
                defaults={
                    "message": message.dict(),
                },
            )
            # delete old nonce records
            nonce.delete()
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # should verify within 15 minutes
        if not timezone.now() - datetime.timedelta(minutes=15) < message.issued_at.date:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # generate jwt token
        token = RefreshToken()
        token["wallet_id"] = str(wallet.id)

        return Response(
            status=status.HTTP_200_OK,
            data={
                "access": str(token.access_token),
                "refresh": str(token),
            },
        )
