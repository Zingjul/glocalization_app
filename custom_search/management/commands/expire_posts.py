from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from seekers.models import SeekerPost
from posts.models import Post


class Command(BaseCommand):
    help = "Expire posts (Seekers + Posts) older than their lifespan and delete attached media"

    def handle(self, *args, **options):
        now = timezone.now()
        total_expired = 0

        # --- Expire Seeker Posts ---
        seeker_expired = SeekerPost.objects.filter(
            status="active", expires_at__lte=now
        )

        with transaction.atomic():
            for post in seeker_expired:
                # delete attached media
                for media in post.mediafile_set.all():
                    if media.file:
                        media.file.delete(save=False)  # delete from storage
                    media.delete()

                post.status = "expired"
                post.save(update_fields=["status"])

        total_expired += seeker_expired.count()

        # --- Expire Normal Posts ---
        posts_expired = Post.objects.filter(
            status="active", expires_at__lte=now
        )

        with transaction.atomic():
            for post in posts_expired:
                # delete attached media
                for media in post.mediafile_set.all():
                    if media.file:
                        media.file.delete(save=False)
                    media.delete()

                post.status = "expired"
                post.save(update_fields=["status"])

        total_expired += posts_expired.count()

        # --- Final Report ---
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Expired {seeker_expired.count()} seeker post(s) "
                f"and {posts_expired.count()} normal post(s). "
                f"Total: {total_expired}"
            )
        )
