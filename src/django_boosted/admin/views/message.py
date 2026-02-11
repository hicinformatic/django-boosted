"""Message view generator for django-boosted."""

from __future__ import annotations

from typing import Callable

from .base import ViewConfig, ViewGenerator


class MessageViewMixin:
    """Mixin for message view generation."""

    def generate_admin_custom_message_view(
        self: ViewGenerator,
        view_func: Callable,
        label: str,
        *,
        template_name: str = "admin_boost/message.html",
        path_fragment: str | None = None,
        requires_object: bool = False,
        permission: str = "view",
    ) -> Callable:
        config = ViewConfig(
            template_name=template_name,
            path_fragment=path_fragment,
            requires_object=requires_object,
            permission=permission,
        )
        wrapper = self._generate_admin_custom_view(view_func, label, config)
        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config.update(  # type: ignore[attr-defined]
            {
                "view_type": "message",
                "requires_object": requires_object,
                "show_in_object_tools": True,
            }
        )
        return wrapper
