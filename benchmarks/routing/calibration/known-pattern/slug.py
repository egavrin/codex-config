"""Small display-name slug helper."""


def slugify(value: str) -> str:
    """Return a lowercase slug for a display name."""
    return value.strip().lower().replace(" ", "-")
