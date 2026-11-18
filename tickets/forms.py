from django import forms

from tickets.models import Category, Ticket, TicketComment, TicketPriority, TicketStatus

INPUT_CLASSES = (
    "w-full rounded-md border border-slate-300 px-3 py-2 text-sm "
    "focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
)
SELECT_CLASSES = f"{INPUT_CLASSES} bg-white"


class StyledFormMixin:
    """Apply consistent Tailwind classes to every field widget (Tailwind's
    preflight strips native input/select/textarea styling)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = SELECT_CLASSES if isinstance(field.widget, forms.Select) else INPUT_CLASSES
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()


class TicketForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "priority", "category", "reporter_name"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class TicketCommentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ["author_name", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class TicketFilterForm(StyledFormMixin, forms.Form):
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
