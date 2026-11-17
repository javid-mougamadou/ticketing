import pytest
from django.urls import reverse

from tickets.models import Ticket, TicketComment, TicketStatus


@pytest.fixture
def ticket(db):
    return Ticket.objects.create(title="Something is broken", description="...", reporter_name="Alice")


@pytest.mark.django_db
def test_update_status_rejects_non_htmx(client, ticket):
    response = client.post(
        reverse("tickets:ticket_update_status", kwargs={"pk": ticket.pk}),
        {"status": TicketStatus.RESOLVED},
    )

    assert response.status_code == 400
    ticket.refresh_from_db()
    assert ticket.status == TicketStatus.OPEN


@pytest.mark.django_db
def test_update_status_via_htmx_returns_status_panel(client, ticket):
    response = client.post(
        reverse("tickets:ticket_update_status", kwargs={"pk": ticket.pk}),
        {"status": TicketStatus.RESOLVED},
        HTTP_HX_REQUEST="true",
    )

    ticket.refresh_from_db()
    assert response.status_code == 200
    assert ticket.status == TicketStatus.RESOLVED
    assert b'id="status-panel"' in response.content


@pytest.mark.django_db
def test_update_status_rejects_invalid_status(client, ticket):
    response = client.post(
        reverse("tickets:ticket_update_status", kwargs={"pk": ticket.pk}),
        {"status": "not-a-real-status"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_comment_create_rejects_non_htmx(client, ticket):
    response = client.post(
        reverse("tickets:comment_create", kwargs={"pk": ticket.pk}),
        {"author_name": "Bob", "comment": "Hello"},
    )

    assert response.status_code == 400
    assert TicketComment.objects.count() == 0


@pytest.mark.django_db
def test_comment_create_via_htmx_returns_comments_partial(client, ticket):
    response = client.post(
        reverse("tickets:comment_create", kwargs={"pk": ticket.pk}),
        {"author_name": "Bob", "comment": "Hello"},
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert b'id="comments-section"' in response.content
    assert b"Hello" in response.content
    assert TicketComment.objects.filter(ticket=ticket, author_name="Bob").exists()
