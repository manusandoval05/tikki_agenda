from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django import forms
from .models import Task, Tag


class TaskCreateView(CreateView):
    model = Task
    fields = ["title", "description", "priority", "date", "tags"]
    template_name = "task_form.html"
    success_url = "/"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # HTML5 date input with ISO format + Bulma class
        form.fields["date"].widget = forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "input"},
        )
        form.fields["date"].input_formats = ["%Y-%m-%d"]

        # Style tags as Bulma multiple select (even if later you hide it for chips)
        form.fields["tags"].widget = forms.SelectMultiple(
            attrs={"class": "select is-multiple", "size": 6}
        )

        return form

    def form_valid(self, form):
        # First save the Task (without yet handling new tags)
        response = super().form_valid(form)

        # Read comma-separated new tags from POST (chips JS will populate this)
        raw_new_tags = self.request.POST.get("new_tags", "")
        if raw_new_tags:
            names = [t.strip() for t in raw_new_tags.split(",") if t.strip()]
            for name in names:
                tag, _ = Tag.objects.get_or_create(name=name)
                self.object.tags.add(tag)  # self.object is the created Task

        return response


class TaskUpdateView(UpdateView):
    model = Task
    fields = ["title", "description", "priority", "date", "completed", "tags"]
    template_name = "task_form.html"
    success_url = "/"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # HTML5 date input with ISO format + Bulma class
        form.fields["date"].widget = forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "input"},
        )
        form.fields["date"].input_formats = ["%Y-%m-%d"]

        # Style tags as Bulma multiple select (even if later you hide it for chips)
        form.fields["tags"].widget = forms.SelectMultiple(
            attrs={"class": "select is-multiple", "size": 6}
        )

        return form

    def form_valid(self, form):
        # First save the Task (without yet handling new tags)
        response = super().form_valid(form)

        # Read comma-separated new tags from POST (chips JS will populate this)
        raw_new_tags = self.request.POST.get("new_tags", "")
        if raw_new_tags:
            names = [t.strip() for t in raw_new_tags.split(",") if t.strip()]
            for name in names:
                tag, _ = Tag.objects.get_or_create(name=name)
                self.object.tags.add(tag)  # self.object is the created Task

        return response


def index(request):
    tasks = Task.objects.all()
    total_tasks_num = tasks.count()
    completed_tasks_num = tasks.filter(completed=True).count()

    percentage = (
        int(100 * completed_tasks_num / total_tasks_num)
        if completed_tasks_num > 0
        else 0
    )

    search_query = request.GET.get("q")
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    status_filter = request.GET.get("status")
    if status_filter == "open":
        tasks = tasks.filter(completed=False)
    elif status_filter == "completed":
        tasks = tasks.filter(completed=True)
    min_priority = request.GET.get("min_priority")
    if min_priority:
        tasks = tasks.filter(priority__gte=min_priority)

    order = request.GET.get("order")
    match order:
        case "date":
            tasks = tasks.order_by("date")
        case "-date":
            tasks = tasks.order_by("-date")
        case "priority":
            tasks = tasks.order_by("priority")
        case "-priority":
            tasks = tasks.order_by("-priority")
        case _:
            tasks = tasks.order_by("-date")

    context = {
        "tasks": tasks,
        "percentage": percentage,
        "total_tasks": total_tasks_num,
        "completed_tasks": completed_tasks_num,
    }
    return render(request, "index.html", context)


@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect("index")


@require_POST
def task_toggle_completed(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.completed = not task.completed
    task.save()
    return redirect("index")
