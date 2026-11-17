from django import forms

from tickets.models import Category, Ticket, TicketComment, TicketPriority, TicketStatus


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "priority", "category", "reporter_name"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ["author_name", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class TicketFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("", "All statuses")] + TicketStatus.choices,
        required=False,
    )
    priority = forms.ChoiceField(
        choices=[("", "All priorities")] + TicketPriority.choices,
        required=False,
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All categories",
    )
