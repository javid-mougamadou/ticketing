from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from tickets.forms import TicketCommentForm, TicketFilterForm, TicketForm
from tickets.models import Ticket, TicketStatus


def ticket_list(request):
    filter_form = TicketFilterForm(request.GET or None)
    category_id = None
    status = ""
    priority = ""

    if filter_form.is_valid():
        status = filter_form.cleaned_data.get("status") or ""
        priority = filter_form.cleaned_data.get("priority") or ""
        category = filter_form.cleaned_data.get("category")
        category_id = category.id if category else None

    tickets = Ticket.objects.filtered(status=status, priority=priority, category_id=category_id)

    context = {"tickets": tickets, "filter_form": filter_form}

    if request.htmx:
        return render(request, "tickets/_ticket_table.html", context)
    return render(request, "tickets/list.html", context)


def ticket_create(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()
            return redirect("tickets:ticket_detail", pk=ticket.pk)
    else:
        form = TicketForm()

    return render(request, "tickets/create.html", {"form": form})


def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    comment_form = TicketCommentForm()
    context = {
        "ticket": ticket,
        "comment_form": comment_form,
        "status_choices": TicketStatus.choices,
    }
    return render(request, "tickets/detail.html", context)


def ticket_update_status(request, pk):
    if not request.htmx or request.method != "POST":
        return HttpResponseBadRequest("This endpoint only accepts HTMX POST requests")

    ticket = get_object_or_404(Ticket, pk=pk)
    new_status = request.POST.get("status")
    if new_status not in TicketStatus.values:
        return HttpResponseBadRequest("Invalid status")

    ticket.change_status(new_status)

    context = {"ticket": ticket, "status_choices": TicketStatus.choices}
    return render(request, "tickets/_status_panel.html", context)


def comment_create(request, pk):
    if not request.htmx or request.method != "POST":
        return HttpResponseBadRequest("This endpoint only accepts HTMX POST requests")

    ticket = get_object_or_404(Ticket, pk=pk)
    form = TicketCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.ticket = ticket
        comment.save()

    context = {"ticket": ticket, "comment_form": TicketCommentForm()}
    return render(request, "tickets/_comments.html", context)
