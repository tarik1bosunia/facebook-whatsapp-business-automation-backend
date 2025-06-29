from django.core.exceptions import ValidationError
from messaging.models import SocialMediaUser


def get_or_create_socialuser(social_media_id, platform=None, name=None, avatar_url=None, customer=None):
    """
    Get or create a SocialMediaUser with the given social_media_id.

    Args:
        social_media_id (str): The unique ID from the social platform
        platform (str, optional): The social platform (e.g., 'facebook', 'whatsapp')
        name (str, optional): The socialuser's display name
        avatar_url (str, optional): URL to the socialuser's avatar/image
        customer (Customer, optional): Associated Customer object

    Returns:
        tuple: (SocialMediaUser instance, created: bool)

    Raises:
        ValidationError: If social_media_id is not provided or invalid
    """
    if not social_media_id:
        raise ValidationError("social_media_id is required")

    defaults = {}
    if name:
        defaults['name'] = name
    else:
        defaults['name'] = f"SocialUser {social_media_id[:8]}..."  # Truncate long IDs

    if platform:
        defaults['platform'] = platform

    if avatar_url:
        defaults['avatar_url'] = avatar_url

    if customer:
        defaults['customer'] = customer

    try:
        socialuser, _ = SocialMediaUser.objects.get_or_create(
            social_media_id=social_media_id,
            defaults=defaults
        )
        return socialuser
    except Exception as e:
        # Handle cases where the same social_media_id exists with different platform
        existing_socialuser = SocialMediaUser.objects.filter(social_media_id=social_media_id).first()
        if existing_socialuser:
            # Update fields if provided
            update_fields = []
            if name and existing_socialuser.name != name:
                existing_socialuser.name = name
                update_fields.append('name')
            if avatar_url and existing_socialuser.avatar_url != avatar_url:
                existing_socialuser.avatar_url = avatar_url
                update_fields.append('avatar_url')
            if customer and existing_socialuser.customer != customer:
                existing_socialuser.customer = customer
                update_fields.append('customer')

            if update_fields:
                existing_socialuser.save(update_fields=update_fields)
            return existing_socialuser, False

        raise ValidationError(f"Failed to get or create socialuser: {str(e)}")