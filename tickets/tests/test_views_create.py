import pytest
from django.urls import reverse

from tickets.models import Ticket


@pytest.mark.django_db
def test_create_ticket_valid_form_redirects_to_detail(client):
    response = client.post(
        reverse("tickets:ticket_create"),
        {
            "title": "New bug",
            "description": "It broke",
            "priority": "high",
            "reporter_name": "Alice",
        },
    )

    ticket = Ticket.objects.get(title="New bug")
    assert response.status_code == 302
    assert response.url == reverse("tickets:ticket_detail", kwargs={"pk": ticket.pk})


@pytest.mark.django_db
def test_create_ticket_invalid_form_rerenders_with_errors(client):
    response = client.post(
        reverse("tickets:ticket_create"),
        {"title": "", "description": ""},
    )

    assert response.status_code == 200
    assert Ticket.objects.count() == 0
    assert b"obligatoire" in response.content
