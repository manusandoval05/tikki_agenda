from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField("Tag", related_name="tasks", blank=True)
    priority = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=3
    )
    
    def priority_color(self):
        tag = "is-info"
        if self.priority >= 3:
            tag = (
                "is-warning" 
                if self.priority == 3 
                else "is-danger")
        return tag


class Tag(models.Model):
    name = models.CharField(max_length=50)
