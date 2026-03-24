"""Public exports for django-boosted."""
default_app_config = "django_boosted.apps.DjangoBoostedConfig"  # noqa: E402

from .admin import AdminBoostModel, AdminBoostFormat  # noqa: E402
from .decorators import admin_boost_action, admin_boost_view  # noqa: E402
from .middleware import CurrentUserMiddleware, get_current_user  # noqa: E402

# Lazy import for model exports to avoid AppRegistryNotReady when package loads during Django app init
def __getattr__(name):
    if name in ("AuditMixin", "AuditUserField", "AuditUserValue", "format_audit_user"):
        from .models import AuditMixin, AuditUserField, AuditUserValue, format_audit_user
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AdminBoostModel",
    "AdminBoostFormat",
    "admin_boost_action",
    "admin_boost_view",
    "AuditMixin",
    "AuditUserField",
    "AuditUserValue",
    "format_audit_user",
    "CurrentUserMiddleware",
    "get_current_user",
]

try:
    from django_boosted.rest_framework.metadata import BoostedRestFrameworkMetadata
    __all__.append("BoostedRestFrameworkMetadata")
except ImportError:
    pass  # rest_framework not installed

from importlib.metadata import version
__version__ = version("django-boosted")
