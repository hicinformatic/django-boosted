"""Tools methods for django-boosted."""

from typing import List

from django.urls import reverse


def get_boost_view_names(self) -> List[str]:
    """Get list of boost view names."""
    return list(self.boost_views or [])


def get_boost_view_config(self, view_name: str) -> dict | None:
    """Get configuration for a boost view."""
    view = getattr(self, view_name, None)
    return getattr(view, "_admin_boost_config", None) if view else None


def get_boost_object_tools(self, request, object_id: str) -> list[dict]:
    """Get object tools for boost views."""
    items: list[dict] = []
    for view_name in self.get_boost_view_names():
        config = self.get_boost_view_config(view_name)
        if not config:
            continue
        if not config.get("requires_object", False):
            continue
        if not config.get("show_in_object_tools", True):
            continue
        url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_{view_name}",
            args=[object_id],
            current_app=self.admin_site.name,
        )
        items.append({"label": config["label"], "url": url})
    return items


def get_boost_list_tools(self, request) -> list[dict]:
    """Get list tools for boost views."""
    items: list[dict] = []
    for view_name in self.get_boost_view_names():
        config = self.get_boost_view_config(view_name)
        if not config:
            continue
        if config.get("requires_object", False):
            continue
        if not config.get("show_in_object_tools", True):
            continue
        url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_{view_name}",
            current_app=self.admin_site.name,
        )
        items.append({"label": config["label"], "url": url})
    return items
