"""Mixins to wire django-admin-boost into ModelAdmin classes."""

from __future__ import annotations

from typing import Iterable, List

from django.urls import path, reverse


class AdminBoostMixin:
    """Provides automatic URL registration and object tools integration."""

    boost_views: Iterable[str] = ()

    def get_boost_view_names(self) -> List[str]:
        return list(self.boost_views or [])

    def get_boost_view_config(self, view_name: str) -> dict | None:
        view = getattr(self, view_name, None)
        return getattr(view, "_admin_boost_config", None) if view else None

    def get_boost_object_tools(self, request, object_id: str) -> list[dict]:
        items: list[dict] = []
        for view_name in self.get_boost_view_names():
            config = self.get_boost_view_config(view_name)
            if not config or not config.get("show_in_object_tools", True):
                continue
            url = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_{view_name}",
                args=[object_id],
                current_app=self.admin_site.name,
            )
            items.append({"label": config["label"], "url": url})
        return items

    def get_urls(self):
        urls = super().get_urls()
        boost_urls = []
        for view_name in self.get_boost_view_names():
            view = getattr(self, view_name, None)
            config = self.get_boost_view_config(view_name)
            if not view or not config:
                continue

            path_fragment = config.get("path_fragment") or view_name.replace("_", "-")
            boost_urls.append(
                path(
                    f"<path:object_id>/{path_fragment}/",
                    self.admin_site.admin_view(view),
                    name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_{view_name}",
                )
            )
        return boost_urls + urls

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            items = list(extra_context.get("object_tools_items") or [])
            items.extend(self.get_boost_object_tools(request, object_id))
            extra_context["object_tools_items"] = items
        return super().changeform_view(
            request,
            object_id=object_id,
            form_url=form_url,
            extra_context=extra_context,
        )
