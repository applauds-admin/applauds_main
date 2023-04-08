from rest_framework import serializers

from poap.users.models import WalletUser


class WallerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletUser
        fields = (
            "address",
            "nickname",
            "description",
            "avatar",
            "joined_count",
            "owned_count",
            "created_at",
        )


class WallerUserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletUser
        fields = (
            "address",
            "nickname",
            "description",
            "avatar",
            "joined_count",
            "owned_count",
        )


class WalletVerifySerializer(serializers.Serializer):
    message = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    signature = serializers.CharField(required=True, allow_null=False, allow_blank=False)


class WalletUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletUser
        fields = (
            "nickname",
            "description",
            "avatar",
        )
