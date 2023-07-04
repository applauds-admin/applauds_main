import requests
from django.conf import settings
from rest_framework import serializers

from poap.users.models import WalletUser, WalletGithub


class WalletGithubSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = WalletGithub
        fields = (
            "username", "nickname", "avatar",
        )

    def get_avatar(self, instance):
        return f"https://avatars.githubusercontent.com/u/{instance.rid}?v=4"


class WallerUserSerializer(serializers.ModelSerializer):
    github = WalletGithubSerializer(read_only=True)

    class Meta:
        model = WalletUser
        fields = (
            "address",
            "nickname",
            "description",
            "avatar",
            "github",
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


class AuthGithubSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_null=False, max_length=20, min_length=20)
    token = serializers.DictField(read_only=True)

    def validate(self, attrs):
        resp: dict = requests.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            json={
                "client_id": settings.GITHUB_APP["client_id"],
                "client_secret": settings.GITHUB_APP["secret"],
                "code": attrs["code"],
            }
        ).json()
        if resp.get("error") is not None:
            raise serializers.ValidationError({"code": resp.get("error_description")})

        attrs["token"] = resp
        return attrs
