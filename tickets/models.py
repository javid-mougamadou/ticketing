from django.db import models

from tickets import managers


class TicketStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"


class TicketPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The name of the category",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return f"#{self.id} Category: {self.name}"


class Ticket(models.Model):
    title = models.CharField(
        max_length=255,
        help_text="The title of the ticket",
    )
    description = models.TextField(
        help_text="The description of the ticket",
    )
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN,
        db_index=True,
        help_text="The current status of the ticket",
    )
    priority = models.CharField(
        max_length=20,
        choices=TicketPriority.choices,
        default=TicketPriority.MEDIUM,
        db_index=True,
        help_text="The priority of the ticket",
    )
    category = models.ForeignKey(
        "tickets.Category",
        related_name="tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The related category of the ticket",
    )
    assigned_to = models.ForeignKey(
        "auth.User",
        related_name="assigned_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The agent assigned to the ticket",
    )
    reporter_name = models.CharField(
        max_length=100,
        help_text="The name of the person who reported the ticket (no auth on this demo)",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    objects = managers.TicketManager()

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return f"#{self.id} Ticket: {self.title}"

    def change_status(self, new_status):
        if new_status == self.status:
            return
        old_status = self.status
        self.status = new_status
        self.save(update_fields=["status", "updated_date"])
        TicketStatusHistory.objects.create(ticket=self, old_status=old_status, new_status=new_status)


class TicketComment(models.Model):
    ticket = models.ForeignKey(
        "tickets.Ticket",
        related_name="comments",
        on_delete=models.CASCADE,
        help_text="The related ticket of the comment",
    )
    author_name = models.CharField(
        max_length=100,
        help_text="The name of the comment author (no auth on this demo)",
    )
    comment = models.TextField(
        help_text="The content of the comment",
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_date"]

    def __str__(self):
        return f"#{self.id} TicketComment: {self.ticket_id}"


class TicketStatusHistory(models.Model):
    ticket = models.ForeignKey(
        "tickets.Ticket",
        related_name="status_history",
        on_delete=models.CASCADE,
        help_text="The related ticket of the status change",
    )
    old_status = models.CharField(max_length=20, choices=TicketStatus.choices)
    new_status = models.CharField(max_length=20, choices=TicketStatus.choices)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_date"]
        verbose_name_plural = "ticket status histories"

    def __str__(self):
        return f"#{self.id} TicketStatusHistory: {self.ticket_id} ({self.old_status} -> {self.new_status})"
