from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TaskConfig(AppConfig):
    name = "poap.tasks"
    verbose_name = _("Tasks")

    def ready(self):
        try:
            import poap.tasks.signals  # noqa F401
        except ImportError:
            pass
