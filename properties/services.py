from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .models import Property
from .repositories import PropertyRepository


class PropertyService:
    """Business logic for property workflows."""

    IMAGE_CAPTION_MAX_LENGTH = 200

    @staticmethod
    def create_property(owner, validated_data: dict) -> Property:
        return PropertyRepository.create(owner=owner, **validated_data)

    @staticmethod
    def update_property(user, property_obj: Property, validated_data: dict) -> Property:
        if property_obj.owner != user and not user.is_staff:
            raise PermissionDenied("Ban khong co quyen cap nhat bat dong san nay.")

        for key, value in validated_data.items():
            setattr(property_obj, key, value)
        return PropertyRepository.save(property_obj)

    @staticmethod
    def delete_property(user, property_obj: Property) -> None:
        if property_obj.owner != user and not user.is_staff:
            raise PermissionDenied("Ban khong co quyen xoa bat dong san nay.")
        property_obj.delete()

    @staticmethod
    def track_view(property_obj: Property) -> None:
        PropertyRepository.increment_view(property_obj)

    @staticmethod
    def toggle_favorite(user, property_id: int) -> dict:
        try:
            property_obj = PropertyRepository.get_by_id(property_id)
        except ObjectDoesNotExist as exc:
            raise NotFound("Khong tim thay bat dong san.") from exc

        favorite, created = PropertyRepository.get_or_create_favorite(user=user, property_obj=property_obj)
        if created:
            return {"message": "Da them vao yeu thich", "is_favorited": True}

        PropertyRepository.delete_favorite(favorite)
        return {"message": "Da xoa khoi yeu thich", "is_favorited": False}

    @staticmethod
    def upload_images(
        *,
        user,
        property_id: int,
        images: list,
        caption: str = "",
        is_primary: bool = False,
        start_order: int = 0,
    ):
        if not images:
            raise ValidationError("Thieu file anh upload.")
        if start_order < 0:
            raise ValidationError({"order": ["Order phai >= 0."]})

        normalized_caption = (caption or "").strip()
        if not normalized_caption:
            raise ValidationError({"caption": ["Caption is required for every property image."]})
        if len(normalized_caption) > PropertyService.IMAGE_CAPTION_MAX_LENGTH:
            raise ValidationError(
                {"caption": [f"Caption khong duoc vuot qua {PropertyService.IMAGE_CAPTION_MAX_LENGTH} ky tu."]}
            )

        try:
            property_obj = PropertyRepository.get_owned_by_id(pk=property_id, user=user)
        except ObjectDoesNotExist as exc:
            raise NotFound("Khong tim thay hoac ban khong co quyen.") from exc

        max_files_per_upload = int(getattr(settings, "PROPERTY_IMAGE_MAX_FILES_PER_UPLOAD", 10))
        max_files_per_property = int(getattr(settings, "PROPERTY_IMAGE_MAX_FILES_PER_PROPERTY", 30))
        allowed_types = set(getattr(settings, "PROPERTY_IMAGE_ALLOWED_TYPES", {"image/jpeg", "image/png"}))
        max_upload_bytes = int(getattr(settings, "PROPERTY_IMAGE_MAX_UPLOAD_BYTES", 5 * 1024 * 1024))

        if len(images) > max_files_per_upload:
            raise ValidationError(
                {"images": [f"Moi lan upload toi da {max_files_per_upload} anh."]}
            )

        current_image_count = PropertyRepository.count_images(property_obj)
        if current_image_count + len(images) > max_files_per_property:
            raise ValidationError(
                {"images": [f"Tong so anh moi bat dong san toi da {max_files_per_property} anh."]}
            )

        for image_file in images:
            content_type = (getattr(image_file, "content_type", "") or "").lower().strip()
            if not content_type or content_type not in allowed_types:
                raise ValidationError(
                    {"images": [f"File '{getattr(image_file, 'name', 'unknown')}' co dinh dang khong hop le."]}
                )
            if getattr(image_file, "size", 0) > max_upload_bytes:
                raise ValidationError(
                    {"images": [f"File '{getattr(image_file, 'name', 'unknown')}' vuot qua gioi han dung luong."]}
                )

        uploaded = []
        has_primary = PropertyRepository.has_primary_image(property_obj)
        for index, image_file in enumerate(images):
            will_primary = False
            if is_primary and index == 0:
                will_primary = True
                PropertyRepository.clear_primary_image(property_obj)
            elif current_image_count == 0 and not has_primary and index == 0:
                will_primary = True

            image_obj = PropertyRepository.create_image(
                property_obj=property_obj,
                image=image_file,
                caption=normalized_caption,
                is_primary=will_primary,
                order=start_order + index,
            )
            uploaded.append(image_obj)
        return uploaded

    @staticmethod
    def delete_image(user, image_id: int) -> None:
        try:
            image_obj = PropertyRepository.get_owned_image(image_id=image_id, user=user)
        except ObjectDoesNotExist as exc:
            raise NotFound("Khong tim thay anh hoac ban khong co quyen.") from exc

        property_obj = image_obj.property
        was_primary = image_obj.is_primary
        image_obj.image.delete(save=False)
        image_obj.delete()

        if was_primary:
            replacement = PropertyRepository.get_first_image(property_obj)
            if replacement:
                PropertyRepository.set_primary(replacement)
