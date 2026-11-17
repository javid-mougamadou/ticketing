import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from tickets.models import Category, Ticket, TicketComment, TicketPriority, TicketStatus

CATEGORY_NAMES = ["Bug", "Feature Request", "Technical Support", "Billing", "Account Access", "Other"]
AGENT_USERNAMES = ["agent_leslie", "agent_morgan", "agent_sam", "agent_casey", "agent_jordan"]


class Command(BaseCommand):
    help = "Seed the database with demo tickets (idempotent, use --flush to regenerate)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing categories/tickets before reseeding",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=40,
            help="Number of tickets to generate",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            Ticket.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write("Flushed existing tickets and categories.")
        elif Ticket.objects.exists():
            self.stdout.write("Tickets already exist, skipping seed (use --flush to regenerate).")
            return

        faker = Faker()

        categories = [Category.objects.get_or_create(name=name)[0] for name in CATEGORY_NAMES]
        agents = [User.objects.get_or_create(username=username)[0] for username in AGENT_USERNAMES]

        statuses = TicketStatus.values
        priorities = TicketPriority.values

        for _ in range(options["count"]):
            ticket = Ticket.objects.create(
                title=faker.sentence(nb_words=6).rstrip("."),
                description=faker.paragraph(nb_sentences=4),
                priority=random.choice(priorities),
                category=random.choice(categories),
                assigned_to=random.choice(agents + [None]),
                reporter_name=faker.name(),
            )

            final_status = random.choice(statuses)
            if final_status != TicketStatus.OPEN:
                ticket.change_status(final_status)

            for _ in range(random.randint(0, 3)):
                TicketComment.objects.create(
                    ticket=ticket,
                    author_name=faker.name(),
                    comment=faker.sentence(nb_words=12),
                )

        self.stdout.write(self.style.SUCCESS(f"Seeded {options['count']} demo tickets."))
