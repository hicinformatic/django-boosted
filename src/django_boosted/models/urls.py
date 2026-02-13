from django.db import models
from django.utils.translation import gettext_lazy as _

from django_boosted.managers import UrlManager


class UrlModel(models.Model):
    url: models.URLField = models.URLField(
        max_length=200, primary_key=True, verbose_name=_("URL")
    )
    name: models.CharField = models.CharField(max_length=200, verbose_name=_("Name"))
    namespace: models.CharField = models.CharField(
        max_length=200, verbose_name=_("Namespace")
    )
    module: models.CharField = models.CharField(
        max_length=200, verbose_name=_("Module")
    )
    app_label: models.CharField = models.CharField(
        max_length=200, verbose_name=_("App Label")
    )
    model: models.CharField = models.CharField(max_length=200, verbose_name=_("Model"))
    reverse_name: models.CharField = models.CharField(
        max_length=200, verbose_name=_("Reverse Name")
    )
    lookup_str: models.CharField = models.CharField(
        max_length=200, verbose_name=_("Lookup Str")
    )

    objects = UrlManager()

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = _("URL")
        verbose_name_plural = _("URLs")
