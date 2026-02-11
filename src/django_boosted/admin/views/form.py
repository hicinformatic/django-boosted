"""Form view generator for django-boosted."""

from __future__ import annotations

from typing import Callable

from .base import ViewConfig, ViewGenerator


class FormViewMixin:
    """Mixin for form view generation."""

    def generate_admin_custom_form_view(
        self: ViewGenerator,
        view_func: Callable,
        label: str,
        *,
        template_name: str = "admin_boost/admin_boost_form.html",
        path_fragment: str | None = None,
        requires_object: bool = True,
        permission: str = "view",
    ) -> Callable:
        config = ViewConfig(
            template_name=template_name,
            path_fragment=path_fragment,
            permission=permission,
            requires_object=requires_object,
        )
        wrapper = self._generate_admin_custom_view(view_func, label, config)
        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
            "view_type": "form",
            "requires_object": requires_object,
            "show_in_object_tools": True,
        }
        return wrapper
