from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from poap.tasks.models import Task, TaskClass, TaskTag, TaskUser
from poap.users.api.serializers import WallerUserSimpleSerializer


class TaskTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTag
        fields = ("name", "slug")


class VerificationClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskClass
        fields = ("id", "name", "logo", "description")


class VerificationClassSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskClass
        fields = ("id", "name", "logo",)


class TasksSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False, allow_null=False, allow_empty=False)
    verification_class = VerificationClassSimpleSerializer()
    created_by = WallerUserSimpleSerializer()

    is_joined = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "logo",
            "mode",
            "description",
            "joined_count",
            "owned_count",
            "tags",
            "verification_class",
            "email",
            "is_active",
            "is_joined",
            "created_by",
            "created_at",
        )

    def get_is_joined(self, instance: Task):
        user = self.context["user"]
        if not user:
            return None

        if TaskUser.objects.filter(task_id=instance.id, user_id=user.id).exists():
            return True
        return False


class TasksCreateSerializer(TaggitSerializer, serializers.ModelSerializer):
    # verification_class = serializers.PrimaryKeyRelatedField(
    #     many=False, allow_null=False, queryset=TaskClass.objects.all(),
    # )
    tags = TagListSerializerField(required=False, allow_null=False, allow_empty=False)

    class Meta:
        model = Task
        fields = (
            "name",
            "logo",
            "mode",
            "description",
            "tags",
            "verification_url",
            # "verification_class",
            "email",
            "is_active",
        )


class TaskUserSerializer(serializers.ModelSerializer):
    user = WallerUserSimpleSerializer()

    class Meta:
        model = TaskUser
        fields = (
            "user",
            "verify_address",
            "task",
            "owned",
            "created_at",
        )
