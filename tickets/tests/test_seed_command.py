import pytest
from django.core.management import call_command

from tickets.models import Ticket


@pytest.mark.django_db
def test_seed_creates_tickets():
    call_command("seed_demo_data", count=10)

    assert Ticket.objects.count() == 10


@pytest.mark.django_db
def test_seed_is_idempotent_without_flush():
    call_command("seed_demo_data", count=10)
    call_command("seed_demo_data", count=10)

    assert Ticket.objects.count() == 10


@pytest.mark.django_db
def test_seed_flush_regenerates():
    call_command("seed_demo_data", count=10)
    call_command("seed_demo_data", count=5, flush=True)

    assert Ticket.objects.count() == 5
