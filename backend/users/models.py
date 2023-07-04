from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from poap.core.models import TimestampedModel


class User(AbstractUser):
    """
    Default custom user model for backend.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    def get_absolute_url(self):
        """Get url for user"s detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


class WalletUser(TimestampedModel):
    address = models.CharField("Wallet Address", db_index=True, max_length=42, unique=True)
    message = models.JSONField("Signed Message", null=True, blank=True, editable=False)
    nickname = models.CharField("Nickname", null=True, blank=True, max_length=42)
    description = models.TextField("Description", null=True, blank=True)
    avatar = models.FileField("Avatar", upload_to="wallet-avatar", null=True, blank=True)

    joined_count = models.BigIntegerField("Joined Count", default=0, null=False, blank=False, editable=False)
    owned_count = models.BigIntegerField("Owned Count", default=0, null=False, blank=False, editable=False)

    is_active = models.BooleanField("Is Active", null=False, blank=False, default=True)

    class Meta:
        db_table = "wallet_user"
        ordering = ["-created_at", "-updated_at"]

    @property
    def is_authenticated(self):
        return self.is_active

    def __str__(self):
        return f"Wallet: {self.address}"


class WalletGithub(TimestampedModel):
    rid = models.IntegerField("Github ID", null=False, blank=False)
    username = models.CharField("Username", null=False, blank=False, max_length=128, db_index=True)
    nickname = models.CharField("Nickname", null=False, blank=False, max_length=128, db_index=False)
    user = models.OneToOneField(
        WalletUser, on_delete=models.CASCADE,
        null=False, blank=False, related_name="github",
    )

    class Meta:
        db_table = "wallet_github"


class WalletNonce(TimestampedModel):
    nonce = models.CharField("Nonce", max_length=11)
    address = models.CharField("Wallet Address", db_index=True, max_length=42, unique=True)

    class Meta:
        db_table = "wallet_nonce"
