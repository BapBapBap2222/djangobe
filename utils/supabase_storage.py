import mimetypes
import os
import uuid
from io import BytesIO
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


def is_supabase_storage_enabled() -> bool:
    return bool(
        getattr(settings, "SUPABASE_URL", "").strip()
        and getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )


def _looks_like_absolute_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _extract_url(payload: Any) -> str | None:
    if payload is None:
        return None
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        direct_keys = ("publicUrl", "publicURL", "signedUrl", "signedURL", "url")
        for key in direct_keys:
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        for nested_key in ("data",):
            nested = payload.get(nested_key)
            value = _extract_url(nested)
            if value:
                return value
        return None

    for attr in ("public_url", "publicURL", "signed_url", "signedURL", "url"):
        value = getattr(payload, attr, None)
        if isinstance(value, str) and value:
            return value
    return None


def build_media_url(file_value: Any, request=None) -> str | None:
    if not file_value:
        return None

    if hasattr(file_value, "url"):
        try:
            url = file_value.url
        except Exception:
            url = str(file_value)
    else:
        url = str(file_value)

    if not url:
        return None
    if _looks_like_absolute_url(url):
        return url
    return request.build_absolute_uri(url) if request is not None else url


def _join_supabase_url(base_url: str, url_or_path: str) -> str:
    if _looks_like_absolute_url(url_or_path):
        return url_or_path
    return f"{base_url.rstrip('/')}/{url_or_path.lstrip('/')}"


def _read_upload_bytes(file_obj: Any) -> bytes:
    if isinstance(file_obj, bytes):
        return file_obj

    if hasattr(file_obj, "seek"):
        file_obj.seek(0)

    if hasattr(file_obj, "read"):
        data = file_obj.read()
        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            return data.encode("utf-8")

    raise TypeError("Supabase upload expects binary content that can be read into bytes.")


_supabase_client = None


def get_supabase_client():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not is_supabase_storage_enabled():
        raise RuntimeError("Supabase Storage is not configured.")

    from supabase import create_client

    _supabase_client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )
    return _supabase_client


@deconstructible
class SupabaseStorage(Storage):
    def __init__(
        self,
        bucket_name: str,
        *,
        public_bucket: bool = True,
        signed_url_expires_in: int | None = None,
    ):
        self.bucket_name = bucket_name
        self.public_bucket = public_bucket
        self.signed_url_expires_in = (
            signed_url_expires_in
            if signed_url_expires_in is not None
            else getattr(settings, "SUPABASE_SIGNED_URL_EXPIRES_IN", 3600)
        )

    def _open(self, name, mode="rb"):
        data = get_supabase_client().storage.from_(self.bucket_name).download(name)
        if hasattr(data, "read"):
            return data
        return ContentFile(data, name=name)

    def _save(self, name, content):
        base_name, ext = os.path.splitext(name)
        normalized_name = name.replace("\\", "/").lstrip("/")
        content_type = (
            getattr(content, "content_type", None)
            or mimetypes.guess_type(normalized_name)[0]
            or "application/octet-stream"
        )

        for _ in range(10):
            candidate_name = normalized_name
            if _ > 0:
                candidate_name = f"{base_name}_{uuid.uuid4().hex[:8]}{ext}".replace("\\", "/").lstrip("/")

            upload_file = getattr(content, "file", content)
            upload_bytes = _read_upload_bytes(upload_file)

            try:
                get_supabase_client().storage.from_(self.bucket_name).upload(
                    path=candidate_name,
                    file=upload_bytes,
                    file_options={
                        "content-type": content_type,
                        "cache-control": "3600",
                        "upsert": "false",
                    },
                )
                return candidate_name
            except Exception as exc:
                message = str(exc).lower()
                duplicate_markers = ("duplicate", "already exists", "409", "conflict")
                if any(marker in message for marker in duplicate_markers):
                    continue
                raise

        raise RuntimeError(f"Could not save '{normalized_name}' to Supabase Storage after multiple attempts.")

    def delete(self, name):
        if not name:
            return
        try:
            get_supabase_client().storage.from_(self.bucket_name).remove([name])
        except Exception:
            return

    def exists(self, name):
        return False

    def size(self, name):
        raise NotImplementedError("Supabase Storage size lookup is not implemented.")

    def url(self, name):
        if not name:
            return ""

        storage = get_supabase_client().storage.from_(self.bucket_name)
        if self.public_bucket:
            url = _extract_url(storage.get_public_url(name))
            if not url:
                return ""
            return _join_supabase_url(settings.SUPABASE_URL, url)

        signed_payload = storage.create_signed_url(name, self.signed_url_expires_in)
        url = _extract_url(signed_payload)
        if not url:
            return ""
        return _join_supabase_url(settings.SUPABASE_URL, url)


def upload_existing_file_to_supabase(*, bucket_name: str, storage_path: str, local_path: Path, content_type: str | None = None):
    with local_path.open("rb") as file_handle:
        return get_supabase_client().storage.from_(bucket_name).upload(
            path=storage_path.replace("\\", "/").lstrip("/"),
            file=_read_upload_bytes(file_handle),
            file_options={
                "content-type": content_type or mimetypes.guess_type(str(local_path))[0] or "application/octet-stream",
                "cache-control": "3600",
                "upsert": "true",
            },
        )


def configure_supabase_model_storages():
    if not is_supabase_storage_enabled():
        return

    from accounts.models import UserProfile, VerificationRequest
    from news.models import News
    from properties.models import PropertyImage

    avatar_storage = SupabaseStorage(
        getattr(settings, "SUPABASE_AVATARS_BUCKET", "avatars"),
        public_bucket=True,
    )
    property_image_storage = SupabaseStorage(
        getattr(settings, "SUPABASE_PROPERTY_IMAGES_BUCKET", "property-images"),
        public_bucket=True,
    )
    verification_storage = SupabaseStorage(
        getattr(settings, "SUPABASE_VERIFICATION_DOCS_BUCKET", "verification-docs"),
        public_bucket=False,
        signed_url_expires_in=getattr(settings, "SUPABASE_SIGNED_URL_EXPIRES_IN", 3600),
    )
    news_storage = SupabaseStorage(
        getattr(settings, "SUPABASE_NEWS_BUCKET", getattr(settings, "SUPABASE_PROPERTY_IMAGES_BUCKET", "property-images")),
        public_bucket=True,
    )

    UserProfile._meta.get_field("avatar").storage = avatar_storage
    PropertyImage._meta.get_field("image").storage = property_image_storage
    VerificationRequest._meta.get_field("id_card_front").storage = verification_storage
    VerificationRequest._meta.get_field("id_card_back").storage = verification_storage
    News._meta.get_field("thumbnail").storage = news_storage
