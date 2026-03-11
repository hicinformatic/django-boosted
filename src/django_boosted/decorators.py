"""Decorators for django-boosted."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class AdminBoostViewConfig:
    """Configuration for admin boost view decorator."""

    template_name: str | None = None
    path_fragment: str | None = None
    requires_object: bool | None = None
    permission: str = "view"
    hidden: bool = False


def admin_boost_view(
    view_type: str,
    label: str,
    *,
    config: AdminBoostViewConfig | None = None,
    **kwargs,
):
    if config is None:
        config = AdminBoostViewConfig(
            template_name=kwargs.get("template_name"),
            path_fragment=kwargs.get("path_fragment"),
            requires_object=kwargs.get("requires_object"),
            permission=kwargs.get("permission", "view"),
            hidden=kwargs.get("hidden", False),
        )

    def decorator(func: Callable) -> Callable:
        func._admin_boost_view_config = {  # type: ignore[attr-defined]
            "name": func.__name__,
            "view_type": view_type,
            "label": label,
            "template_name": config.template_name,
            "path_fragment": config.path_fragment,
            "requires_object": config.requires_object,
            "permission": config.permission,
            "hidden": config.hidden,
        }
        return func

    return decorator


def admin_boost_action(action_name: str, label: str):
    """Register a changeform action. Populates changeform_actions automatically.
    Requires a handle_<action_name> method to process the action."""
    def decorator(func: Callable) -> Callable:
        func._changeform_action_config = {  # type: ignore[attr-defined]
            "name": action_name,
            "label": label,
        }
        return func
    return decorator
