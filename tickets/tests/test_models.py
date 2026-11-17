import pytest

from tickets.models import Category, Ticket, TicketStatus, TicketStatusHistory


@pytest.fixture
def ticket(db):
    category = Category.objects.create(name="Bug")
    return Ticket.objects.create(
        title="Something is broken",
        description="Steps to reproduce...",
        category=category,
        reporter_name="Alice",
    )


@pytest.mark.django_db
def test_change_status_creates_history_entry(ticket):
    ticket.change_status(TicketStatus.IN_PROGRESS)

    assert ticket.status == TicketStatus.IN_PROGRESS
    history = TicketStatusHistory.objects.filter(ticket=ticket)
    assert history.count() == 1
    assert history.first().old_status == TicketStatus.OPEN
    assert history.first().new_status == TicketStatus.IN_PROGRESS


@pytest.mark.django_db
def test_change_status_is_noop_when_unchanged(ticket):
    ticket.change_status(TicketStatus.OPEN)

    assert TicketStatusHistory.objects.filter(ticket=ticket).count() == 0


@pytest.mark.django_db
def test_change_status_twice_creates_two_history_entries(ticket):
    ticket.change_status(TicketStatus.IN_PROGRESS)
    ticket.change_status(TicketStatus.RESOLVED)

    assert TicketStatusHistory.objects.filter(ticket=ticket).count() == 2
