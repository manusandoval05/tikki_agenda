from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create", views.TaskCreateView.as_view(), name="task_create"),
    path("update/<int:pk>", views.TaskUpdateView.as_view(), name="task_update"),
    path("delete/<int:pk>", views.task_delete, name="task_delete"),
    path(
        "complete/<int:pk>", views.task_toggle_completed, name="task_toggle_completed"
    ),
]
