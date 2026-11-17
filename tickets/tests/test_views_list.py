import pytest
from django.urls import reverse

from tickets.models import Category, Ticket, TicketPriority, TicketStatus


@pytest.fixture
def tickets(db):
    bug = Category.objects.create(name="Bug")
    feature = Category.objects.create(name="Feature Request")
    return [
        Ticket.objects.create(
            title="Open bug",
            description="...",
            category=bug,
            status=TicketStatus.OPEN,
            priority=TicketPriority.HIGH,
            reporter_name="Alice",
        ),
        Ticket.objects.create(
            title="Resolved feature",
            description="...",
            category=feature,
            status=TicketStatus.RESOLVED,
            priority=TicketPriority.LOW,
            reporter_name="Bob",
        ),
    ]


@pytest.mark.django_db
def test_full_page_contains_layout(client, tickets):
    response = client.get(reverse("tickets:ticket_list"))

    assert response.status_code == 200
    assert b"<html" in response.content
    assert b"Open bug" in response.content


@pytest.mark.django_db
def test_htmx_request_returns_partial_only(client, tickets):
    response = client.get(reverse("tickets:ticket_list"), HTTP_HX_REQUEST="true")

    assert response.status_code == 200
    assert b"<html" not in response.content
    assert b"Open bug" in response.content


@pytest.mark.django_db
def test_filter_by_status(client, tickets):
    response = client.get(reverse("tickets:ticket_list"), {"status": TicketStatus.RESOLVED})

    assert b"Resolved feature" in response.content
    assert b"Open bug" not in response.content


@pytest.mark.django_db
def test_combined_filters(client, tickets):
    bug_category = Category.objects.get(name="Bug")
    response = client.get(
        reverse("tickets:ticket_list"),
        {"status": TicketStatus.OPEN, "priority": TicketPriority.HIGH, "category": bug_category.id},
    )

    assert b"Open bug" in response.content
    assert b"Resolved feature" not in response.content
