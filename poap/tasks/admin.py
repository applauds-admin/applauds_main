from django.contrib import admin

from poap.tasks.models import Task, TaskTag, TaskClass, TaskUser


class TaskUserTabularInline(admin.TabularInline):
    fields = (
        "user",
        "owned",
    )
    readonly_fields = ("owned",)
    show_change_link = True
    extra = 0
    model = TaskUser


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "tag_list", "created_at"]
    readonly_fields = ("joined_count", "owned_count")

    inlines = [
        TaskUserTabularInline,
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())


@admin.register(TaskTag)
class TaskTagsAdmin(admin.ModelAdmin):
    list_display = ["slug", "name"]


@admin.register(TaskClass)
class TaskClassesAdmin(admin.ModelAdmin):
    list_display = ["name", "site", "verification_method"]
