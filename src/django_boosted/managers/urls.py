from __future__ import annotations

from dataclasses import dataclass

from django.urls import URLPattern, URLResolver, get_resolver
from virtualqueryset.managers import VirtualManager  # type: ignore[import-untyped]


@dataclass
class UrlCollectionConfig:
    """Configuration for URL collection."""

    namespaces: list[str] | None = None
    app_labels: list[str] | None = None

    def __post_init__(self):
        if self.namespaces is None:
            self.namespaces = []
        if self.app_labels is None:
            self.app_labels = []


class UrlManager(VirtualManager):
    """
    UrlManager inspired by django-extensions show_urls
    Collects all URLs from the Django project with correct namespaces and reverse names.
    """

    def get_data(self) -> list[dict[str, str]]:
        """Collect all URLs from the Django project."""
        self.LANGUAGES = getattr(
            __import__("django.conf").conf.settings, "LANGUAGES", ((None, None),)
        )
        resolver = get_resolver()
        data: list[dict[str, str]] = []
        self._collect_urls(resolver, "", data)
        return data

    def _collect_urls(
        self,
        resolver,
        prefix: str,
        data: list[dict[str, str]],
        *,
        config: UrlCollectionConfig | None = None,
    ) -> None:
        if config is None:
            config = UrlCollectionConfig()
        namespaces = config.namespaces or []
        app_labels = config.app_labels or []

        for pattern in resolver.url_patterns:
            # URLResolver (include)
            if isinstance(pattern, URLResolver):
                new_prefix = self._normalize_path(prefix + str(pattern.pattern))
                new_namespaces = namespaces.copy()
                if pattern.namespace:
                    new_namespaces.append(pattern.namespace)
                new_app_labels = app_labels.copy()
                app_name = getattr(pattern, "app_name", None)
                if app_name:
                    new_app_labels.append(app_name)
                self._collect_urls(
                    pattern,
                    new_prefix,
                    data,
                    config=UrlCollectionConfig(
                        namespaces=new_namespaces, app_labels=new_app_labels
                    ),
                )
            # URLPattern (view endpoint)
            elif isinstance(pattern, URLPattern):
                url_path = self._normalize_path(prefix + str(pattern.pattern))
                name = pattern.name or ""
                namespace = ":".join(namespaces)
                reverse_name = f"{namespace}:{name}" if namespace and name else name

                callback = getattr(pattern, "callback", None)
                module = ""
                app_label = app_labels[-1] if app_labels else ""
                model_name = ""

                if callback:
                    view_class = getattr(callback, "view_class", None)
                    if view_class:
                        # CBV
                        module = view_class.__module__
                        if getattr(view_class, "model", None):
                            model_name = view_class.model._meta.model_name
                            app_label = view_class.model._meta.app_label
                    else:
                        # FBV
                        module = callback.__module__
                        if not app_label:
                            app_label = module.split(".")[0]

                data.append(
                    {
                        "url": url_path,
                        "name": name,
                        "namespace": namespace,
                        "reverse_name": reverse_name,
                        "module": module,
                        "app_label": app_label,
                        "model": model_name,
                        "lookup_str": getattr(pattern, "lookup_str", ""),
                    }
                )
            else:
                # fallback si pattern inconnu
                continue

    def _normalize_path(self, path: str) -> str:
        """Normalize URL path by removing regex markers and ensuring leading slash."""
        path = path.lstrip("^").rstrip("$")
        path = path.replace("\\", "")
        if not path.startswith("/"):
            path = "/" + path
        return path

    def get_queryset(self):
        return super().get_queryset().order_by("name")
