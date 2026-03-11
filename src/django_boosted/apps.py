"""Django app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoBoostedConfig(AppConfig):
    """Configuration for the django-boosted app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_boosted"
    verbose_name = _("Django Boosted")

    def ready(self):
        from django.contrib import admin

        from django_boosted.models.urls import UrlModel

        if not admin.site.is_registered(UrlModel):
            from django_boosted.admin.urls import UrlAdmin
            admin.site.register(UrlModel, UrlAdmin)
