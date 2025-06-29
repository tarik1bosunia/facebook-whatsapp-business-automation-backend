import os
import uuid
import requests
from urllib.parse import urlparse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def save_image_from_url_to_field(url, upload_dir="messenger_images"):
    """
    Downloads an image from a Messenger CDN URL and returns a Django File object
    that can be saved to a FileField.

    Args:
        url (str): The Messenger media URL (temporary CDN).
        upload_dir (str): The upload directory relative to MEDIA_ROOT.

    Returns:
        File object that can be assigned to a model's FileField.
    """
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # Parse and sanitize filename
        parsed_url = urlparse(url)
        base_name = os.path.basename(parsed_url.path)
        _, ext = os.path.splitext(base_name)
        ext = ext or ".jpg"  # Fallback to jpg

        # Generate safe and unique filename
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_dir, filename)

        # Save using Django's default storage
        content = ContentFile(response.content)
        saved_path = default_storage.save(file_path, content)

        return default_storage.open(saved_path, 'rb')  # Django File object
    else:
        raise Exception(f"Failed to download image: {response.status_code}")
