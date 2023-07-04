from django.urls import path

from poap.tasks.api import views

app_name = "tasks"
urlpatterns = [
    path("", view=views.TaskListView.as_view(), name="tasks"),
    path("eligibility/", view=views.EligibilityCheckView.as_view(), name="task-eligibility"),
    path("<int:task_id>/", view=views.TaskDetailView.as_view(), name="tasks"),
    path("<int:task_id>/users/", view=views.TaskUserJoinView.as_view(), name="task-users"),
    path("<int:task_id>/check/", view=views.FunctionsCheckView.as_view(), name="task-check"),
    path("<int:task_id>/claim/", view=views.TaskClaimView.as_view(), name="task-claim"),
    path("<int:task_id>/approve/", view=views.TaskUserApproveView.as_view(), name="task-approve"),

    path("tags/", view=views.TaskTagListView.as_view(), name="task-tags"),
    path("classes/", view=views.TaskClassListView.as_view(), name="task-classes"),
]
