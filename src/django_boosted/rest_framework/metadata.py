"""DRF utilities for django-boosted."""

from rest_framework.metadata import SimpleMetadata  # type: ignore[import-not-found]


class BoostedRestFrameworkMetadata(SimpleMetadata):
    """Generic metadata class that uses field.extra_metadata if available."""

    def get_field_info(self, field):
        """Get field info and merge extra_metadata if field has it."""
        field_info = super().get_field_info(field)
        # Check if field has get_extra_metadata method (for lazy evaluation)
        if hasattr(field, "get_extra_metadata") and callable(field.get_extra_metadata):
            extra_metadata = field.get_extra_metadata()
            if isinstance(extra_metadata, dict):
                field_info.update(extra_metadata)
        # Otherwise check for extra_metadata attribute directly
        elif hasattr(field, "extra_metadata") and isinstance(
            field.extra_metadata, dict
        ):
            field_info.update(field.extra_metadata)
        return field_info


__all__ = ["BoostedRestFrameworkMetadata"]
