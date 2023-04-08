from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericUUIDTaggedItemBase

from poap.core.models import TimestampedModel
from poap.users.models import WalletUser


class TaskClass(TimestampedModel):
    SITE_GITHUB = 0
    SITE_CHOICE = [
        (SITE_GITHUB, "Github"),
    ]

    name = models.CharField("Name", null=False, blank=False, max_length=64)
    logo = models.FileField("Logo", upload_to="task-classes-logo", null=False, blank=False)
    description = models.TextField("Description", null=True, blank=True)
    verification_method = models.CharField("Verification Method", null=False, blank=False, max_length=1024)
    site = models.IntegerField(
        "Site", choices=SITE_CHOICE, default=SITE_GITHUB,
        null=False, blank=False, db_index=True,
    )

    class Meta:
        db_table = "task_class"
        verbose_name = _("Task Class")
        verbose_name_plural = _("Task Classes")

    def __str__(self):
        return f"Class <{self.name}> ({self.id})"


class TaskTag(TagBase):
    class Meta:
        db_table = "task_tag"
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TaggedTask(GenericUUIDTaggedItemBase):
    tag = models.ForeignKey(
        TaskTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )


class Task(TimestampedModel):
    # Use Int field also use as ERC1155 Token ID
    id = models.BigAutoField(primary_key=True, editable=False)
    name = models.CharField("Name", null=False, blank=False, max_length=1024)
    logo = models.FileField("Logo", upload_to="tasks-logo", null=False, blank=False)
    description = models.TextField("Description", null=True, blank=True)
    email = models.EmailField("Notify Email", null=True, blank=True)
    verification_class = models.ForeignKey(TaskClass, null=True, blank=True, on_delete=models.CASCADE)
    verification_url = models.URLField("Verification Url", null=True, blank=True, max_length=1024)

    joined_count = models.BigIntegerField("Joined Count", default=0, null=False, blank=False, editable=False)
    owned_count = models.BigIntegerField("Owned Count", default=0, null=False, blank=False, editable=False)
    is_active = models.BooleanField("Is Active", default=True, null=False, blank=False)

    users = models.ManyToManyField(
        WalletUser, through="TaskUser", related_name="joined_tasks",
        blank=False,
    )
    created_by = models.ForeignKey(
        WalletUser, on_delete=models.SET_NULL, related_name="created_tasks",
        null=True, blank=False
    )

    tags = TaggableManager(through=TaggedTask)

    class Meta:
        db_table = "task"
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ["-created_at", "name"]


class TaskUser(TimestampedModel):
    user = models.ForeignKey(
        WalletUser, on_delete=models.CASCADE,
        null=False, blank=False,
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        null=False, blank=False,
    )

    owned = models.BooleanField("Owned", default=False, null=False, blank=False)

    class Meta:
        db_table = "task_user"
        verbose_name = _("Task User")
        verbose_name_plural = _("Task Users")
        unique_together = ("user", "task")
        ordering = ["-created_at", "owned"]
