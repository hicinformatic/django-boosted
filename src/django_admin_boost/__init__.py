"""Public exports for django-admin-boost."""

from .decorators import admin_boost_object_view
from .mixins import AdminBoostMixin

__all__ = [
    "AdminBoostMixin",
    "admin_boost_object_view",
]
__version__ = "0.1.0"
