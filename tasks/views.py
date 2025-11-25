from django.shortcuts import render
from .models import Task


def index(request):
    tasks = Task.objects.all()
    context = {"tasks": tasks}
    return render(request, "index.html", context)


def create_task(request):
    # Placeholder for task creation logic
    return render(request, "create_task.html")
