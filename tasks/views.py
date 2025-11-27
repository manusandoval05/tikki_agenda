from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django import forms
from .models import Task, Tag

class TaskMethods:
    template_name = "task_form.html"
    model = Task
    fields = ["title", "description", "priority", "date"] 
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["title"].widget = forms.TextInput(
            attrs={"class": "input", "placeholder": "Title"}
        )
        form.fields["description"].widget = forms.Textarea(
            attrs={"class": "textarea", "placeholder": "Description", "rows": 4}
        )
        form.fields["date"].widget = forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "input"},
        )
        form.fields["date"].input_formats = ["%Y-%m-%d"]

        return form

    def form_valid(self, form):
        self.object = form.save()
        tag_data = self.request.POST.get("tags_input", "")
        if tag_data:
            names = [t.strip() for t in tag_data.split(",") if t.strip()]
            for name in names:
                tag, _ = Tag.objects.get_or_create(name=name)
                self.object.tags.add(tag) 
        return redirect("index")

class TaskCreateView(TaskMethods, CreateView):
    model = Task


class TaskUpdateView(TaskMethods, UpdateView):
    model = Task
    fields = ["title", "description", "priority", "date", "completed"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_tags = self.object.tags.all()
        context['current_tags_string'] = ", ".join([t.name for t in current_tags])
        return context


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
