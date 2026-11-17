from django.db import models


class TicketManager(models.Manager):
    def with_comment_count(self):
        return self.annotate(comment_count=models.Count("comments"))

    def filtered(self, status=None, priority=None, category_id=None):
        queryset = self.with_comment_count()
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.order_by("-created_date")
