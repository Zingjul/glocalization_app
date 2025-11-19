from django.core.management.base import BaseCommand
from django.db import transaction
from subscription.models import SubscriptionPlan


class Command(BaseCommand):
    help = "Seed the database with default subscription plans"

    @transaction.atomic
    def handle(self, *args, **options):
        plans = [
            {
                "level": "basic",
                "price": 2000.00,
                "duration_days": 30,
                "description": "Basic plan with limited access and short duration."
            },
            {
                "level": "premium",
                "price": 5000.00,
                "duration_days": 90,
                "description": "Premium plan with full access and extended duration."
            },
        ]

        for plan in plans:
            obj, created = SubscriptionPlan.objects.get_or_create(
                level=plan["level"], defaults=plan
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {obj}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Already exists: {obj}"))

        self.stdout.write(self.style.SUCCESS("🎯 Subscription plans seeding complete!"))
