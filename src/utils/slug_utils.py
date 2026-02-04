import secrets
import string
from django.utils.text import slugify


def generate_nonce(length=4):
    """Generates a short, URL-friendly random string."""
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def unique_slugify(value):
    """
    Generates a unique slug by appending a random nonce.
    This avoids expensive database lookups and race conditions.
    """
    base_slug = slugify(value)
    return f"{base_slug}-{generate_nonce()}"
