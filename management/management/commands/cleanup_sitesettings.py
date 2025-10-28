from django.core.management.base import BaseCommand
from django.conf import settings as django_settings

from management.models import AdminGmailList


class Command(BaseCommand):
    help = (
        "Cleanup AdminGmailList duplicates: keeps the most recent non-empty row, "
        "deletes the others, and ensures exactly one record exists."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without modifying the database",
        )
        parser.add_argument(
            "--prefer-empty",
            action="store_true",
            help="Prefer the most recent row even if recipients are empty (fallback to settings.ADMIN_RECIPIENTS)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        prefer_empty = options["prefer_empty"]

        qs = AdminGmailList.objects.all().order_by("-updated_at", "-id")
        total = qs.count()
        self.stdout.write(self.style.NOTICE(f"Found {total} AdminGmailList rows"))

        keeper = None
        if total:
            if prefer_empty:
                keeper = qs.first()
            else:
                keeper = qs.exclude(admin_recipients__isnull=True).exclude(admin_recipients__exact="").first() or qs.first()
        else:
            keeper = None

        if keeper is None:
            # Create a default row (empty) and report fallback
            if dry_run:
                self.stdout.write(self.style.WARNING("[dry-run] Would create a new AdminGmailList row"))
                return
            keeper = AdminGmailList.objects.create()
            self.stdout.write(self.style.SUCCESS(f"Created new AdminGmailList row (id={keeper.id})"))

        # Determine rows to delete
        to_delete = AdminGmailList.objects.exclude(pk=keeper.pk)
        delete_count = to_delete.count()

        if delete_count:
            if dry_run:
                ids = list(to_delete.values_list("id", flat=True))
                self.stdout.write(self.style.WARNING(f"[dry-run] Would delete {delete_count} rows: {ids}"))
            else:
                ids = list(to_delete.values_list("id", flat=True))
                to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted {delete_count} duplicate rows: {ids}"))
        else:
            self.stdout.write("No duplicate rows to delete.")

        # Report current recipients
        recipients = [r.strip() for r in (keeper.admin_recipients or "").split(',') if r.strip()]
        if not recipients:
            fallback = getattr(django_settings, "ADMIN_RECIPIENTS", [])
            self.stdout.write(
                self.style.NOTICE(
                    f"Active recipients are empty; runtime will fallback to settings.ADMIN_RECIPIENTS={fallback}"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"Active recipients (keeper id={keeper.id}): {recipients}"))

        self.stdout.write(self.style.SUCCESS("Cleanup complete. Ensure only one AdminGmailList exists now."))
