from django.db import models

class Todo(models.Model):
    title = models.CharField(max_length=200)  # short task name
    description = models.TextField(blank=True)  # details (optional)

    # If you want only date (no time), use DateField; for date+time, use DateTimeField
    due_date = models.DateField(null=True, blank=True)

    is_resolved = models.BooleanField(default=False)  # mark as done / not done

    created_at = models.DateTimeField(auto_now_add=True)  # set once when created
    updated_at = models.DateTimeField(auto_now=True)      # updated every save

    def __str__(self):
        return f"{self.title} ({'Done' if self.is_resolved else 'Open'})"
