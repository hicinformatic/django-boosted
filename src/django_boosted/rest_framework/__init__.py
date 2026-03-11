from django.conf import settings

if settings.INSTALLED_APPS and "rest_framework" in settings.INSTALLED_APPS:
    from django_boosted.rest_framework.metadata import (
        BoostedRestFrameworkMetadata,  # noqa: F401
    )

    __all__ = ["BoostedRestFrameworkMetadata"]
else:
    __all__ = []
