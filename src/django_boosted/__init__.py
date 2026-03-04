"""Public exports for django-boosted."""
default_app_config = "django_boosted.apps.DjangoBoostedConfig"  # noqa: E402

from .admin import AdminBoostModel, AdminBoostFormat  # noqa: E402
from .decorators import admin_boost_view  # noqa: E402

__all__ = [
    "AdminBoostModel",
    "AdminBoostFormat",
    "admin_boost_view",
]

__version__ = "0.1.0"
