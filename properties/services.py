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
            raise PermissionDenied("You do not have permission to update this property.")

        for key, value in validated_data.items():
            setattr(property_obj, key, value)
        return PropertyRepository.save(property_obj)

    @staticmethod
    def delete_property(user, property_obj: Property) -> None:
        if property_obj.owner != user and not user.is_staff:
            raise PermissionDenied("You do not have permission to delete this property.")
        for image_obj in property_obj.images.all():
            image_obj.image.delete(save=False)
        property_obj.delete()

    @staticmethod
    def track_view(property_obj: Property) -> None:
        PropertyRepository.increment_view(property_obj)

    @staticmethod
    def toggle_favorite(user, property_id: int) -> dict:
        try:
            property_obj = PropertyRepository.get_by_id(property_id)
        except ObjectDoesNotExist as exc:
            raise NotFound("Property not found.") from exc

        favorite, created = PropertyRepository.get_or_create_favorite(user=user, property_obj=property_obj)
        if created:
            return {"message": "Added to favorites.", "is_favorited": True}

        PropertyRepository.delete_favorite(favorite)
        return {"message": "Removed from favorites.", "is_favorited": False}

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
            raise ValidationError("No image files were uploaded.")
        if start_order < 0:
            raise ValidationError({"order": ["Order must be 0 or greater."]})

        normalized_caption = (caption or "").strip()
        if not normalized_caption:
            raise ValidationError({"caption": ["Caption is required for every property image."]})
        if len(normalized_caption) > PropertyService.IMAGE_CAPTION_MAX_LENGTH:
            raise ValidationError(
                {"caption": [f"Caption cannot exceed {PropertyService.IMAGE_CAPTION_MAX_LENGTH} characters."]}
            )

        try:
            property_obj = PropertyRepository.get_owned_by_id(pk=property_id, user=user)
        except ObjectDoesNotExist as exc:
            raise NotFound("Property not found or you do not have access to it.") from exc

        max_files_per_upload = int(getattr(settings, "PROPERTY_IMAGE_MAX_FILES_PER_UPLOAD", 10))
        max_files_per_property = int(getattr(settings, "PROPERTY_IMAGE_MAX_FILES_PER_PROPERTY", 30))
        allowed_types = set(getattr(settings, "PROPERTY_IMAGE_ALLOWED_TYPES", {"image/jpeg", "image/png"}))
        max_upload_bytes = int(getattr(settings, "PROPERTY_IMAGE_MAX_UPLOAD_BYTES", 5 * 1024 * 1024))

        if len(images) > max_files_per_upload:
            raise ValidationError(
                {"images": [f"You can upload at most {max_files_per_upload} images per request."]}
            )

        current_image_count = PropertyRepository.count_images(property_obj)
        if current_image_count + len(images) > max_files_per_property:
            raise ValidationError(
                {"images": [f"A property can have at most {max_files_per_property} images."]}
            )

        for image_file in images:
            content_type = (getattr(image_file, "content_type", "") or "").lower().strip()
            if not content_type or content_type not in allowed_types:
                raise ValidationError(
                    {"images": [f"File '{getattr(image_file, 'name', 'unknown')}' has an invalid format."]}
                )
            if getattr(image_file, "size", 0) > max_upload_bytes:
                raise ValidationError(
                    {"images": [f"File '{getattr(image_file, 'name', 'unknown')}' exceeds the size limit."]}
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
            raise NotFound("Image not found or you do not have access to it.") from exc

        property_obj = image_obj.property
        was_primary = image_obj.is_primary
        image_obj.image.delete(save=False)
        image_obj.delete()

        if was_primary:
            replacement = PropertyRepository.get_first_image(property_obj)
            if replacement:
                PropertyRepository.set_primary(replacement)
