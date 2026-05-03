from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.models import UserProfile, VerificationRequest
from news.models import News
from properties.models import PropertyImage
from utils.supabase_storage import is_supabase_storage_enabled, upload_existing_file_to_supabase


class Command(BaseCommand):
    help = "Upload existing local media files to Supabase Storage buckets."

    def handle(self, *args, **options):
        if not is_supabase_storage_enabled():
            raise CommandError("Supabase Storage is not configured in environment variables.")

        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            raise CommandError(f"MEDIA_ROOT does not exist: {media_root}")

        upload_jobs = []

        for profile in UserProfile.objects.exclude(avatar="").exclude(avatar__isnull=True):
            upload_jobs.append((settings.SUPABASE_AVATARS_BUCKET, profile.avatar.name))

        for image in PropertyImage.objects.exclude(image="").exclude(image__isnull=True):
            upload_jobs.append((settings.SUPABASE_PROPERTY_IMAGES_BUCKET, image.image.name))

        for news in News.objects.exclude(thumbnail="").exclude(thumbnail__isnull=True):
            upload_jobs.append((settings.SUPABASE_NEWS_BUCKET, news.thumbnail.name))

        for verification_request in VerificationRequest.objects.all():
            if verification_request.id_card_front:
                upload_jobs.append((settings.SUPABASE_VERIFICATION_DOCS_BUCKET, verification_request.id_card_front.name))
            if verification_request.id_card_back:
                upload_jobs.append((settings.SUPABASE_VERIFICATION_DOCS_BUCKET, verification_request.id_card_back.name))

        total = len(upload_jobs)
        uploaded = 0
        skipped = 0

        for bucket_name, storage_path in upload_jobs:
            local_path = media_root / storage_path
            if not local_path.exists():
                self.stdout.write(self.style.WARNING(f"Missing local file, skipped: {storage_path}"))
                skipped += 1
                continue

            upload_existing_file_to_supabase(
                bucket_name=bucket_name,
                storage_path=storage_path,
                local_path=local_path,
            )
            uploaded += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Supabase media sync completed. Uploaded {uploaded} file(s), skipped {skipped}, total references {total}."
            )
        )
