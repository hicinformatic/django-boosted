"""Custom model fields for django-boosted."""

from django.conf import settings
from django.db import models
from django.urls import NoReverseMatch, reverse

from django_boosted.middleware.current_user import get_current_user


class AuditUserValue(str):
    """String subclass with admin_url property for linking to the user in admin."""

    def __new__(cls, value, pk=None):
        if value is None:
            return None
        self = super().__new__(cls, value)
        self._pk = pk
        return self

    def __reduce__(self):
        return (str, (str(self),))

    @property
    def admin_url(self):
        """Return admin change URL for the user, or None if pk unknown or not found."""
        if self._pk is None:
            return None
        from django.apps import apps

        User = apps.get_model(settings.AUTH_USER_MODEL)
        info = (User._meta.app_label, User._meta.model_name)
        try:
            return reverse(
                "admin:%s_%s_change" % info, args=[self._pk]
            )
        except NoReverseMatch:
            return None


def format_audit_user(user, format_fields=("pk", "username"), separator="_"):
    """Format user as string from attribute names. Joins with separator."""
    if not user or not user.is_authenticated:
        return None
    attr_map = {
        "pk": lambda u: u.pk,
        "username": lambda u: getattr(u, "username", u.get_username()),
        "email": lambda u: getattr(u, "email", ""),
    }
    values = []
    for field in format_fields:
        try:
            getter = attr_map.get(field)
            val = getter(user) if getter else getattr(user, field, "")
            if val is not None and str(val).strip():
                values.append(str(val))
        except (AttributeError, TypeError):
            pass
    return separator.join(values) if values else None


def _parse_pk_from_value(value, separator="_"):
    """Extract user pk from stored value. Assumes first segment is pk when numeric."""
    if not value:
        return None
    try:
        first = str(value).split(separator)[0]
        return int(first) if first.isdigit() else None
    except (ValueError, IndexError):
        return None


class AuditUserField(models.CharField):
    """CharField that auto-fills with formatted current user on save.

    mode='created': set only when instance is new and field is empty.
    mode='updated': set on every save.
    """

    def __init__(
        self,
        format_fields=("pk", "username"),
        separator="_",
        mode="updated",
        *args,
        **kwargs,
    ):
        self.format_fields = format_fields
        self.separator = separator
        self.mode = mode
        kwargs.setdefault("max_length", 255)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("null", True)
        kwargs.setdefault("default", getattr(settings, "DJANGO_BOOSTED_AUDIT_USER_FALLBACK", None))
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if self.mode == "created" and not add:
            return getattr(model_instance, self.attname, None)
        if self.mode == "created" and add:
            current = getattr(model_instance, self.attname, None)
            if current:
                return current
        user = get_current_user()
        format_fields = getattr(
            model_instance.__class__, "audit_user_format", self.format_fields
        )
        separator = getattr(
            model_instance.__class__, "audit_user_separator", self.separator
        )
        value = format_audit_user(user, format_fields, separator)
        if not value:
            return getattr(model_instance, self.attname, None)
        pk = _parse_pk_from_value(value, separator)
        return AuditUserValue(value, pk=pk)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        pk = _parse_pk_from_value(value, self.separator)
        return AuditUserValue(value, pk=pk)

    def to_python(self, value):
        if value is None or isinstance(value, AuditUserValue):
            return value
        pk = _parse_pk_from_value(str(value), self.separator)
        return AuditUserValue(str(value), pk=pk)

    def get_prep_value(self, value):
        return str(value) if value is not None else None

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.format_fields != ("pk", "username"):
            kwargs["format_fields"] = self.format_fields
        if self.separator != "_":
            kwargs["separator"] = self.separator
        if self.mode != "updated":
            kwargs["mode"] = self.mode
        return name, path, args, kwargs
