"""Base view generator for django-boosted."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBase
from django.template.response import TemplateResponse
from django.urls import reverse


@dataclass
class ViewConfig:
    """Configuration for admin custom views."""

    template_name: str
    requires_object: bool = False
    permission: str = "view"
    path_fragment: str | None = None


class ViewGenerator:
    def __init__(self, model_admin):
        self.model_admin = model_admin

    def _check_permissions(self, request, object_id=None):
        if object_id:
            obj = self.model_admin.get_object(request, unquote(object_id))
            if obj is None:
                return None, self.model_admin._get_obj_does_not_exist_redirect(
                    request, self.model_admin.model._meta, object_id
                )
            if not self.model_admin.has_view_permission(request, obj):
                raise PermissionDenied
            return obj, None
        if not self.model_admin.has_view_permission(request):
            raise PermissionDenied
        return None, None

    def _build_base_context(self, request, obj=None):
        opts = self.model_admin.model._meta
        context = {
            **self.model_admin.admin_site.each_context(request),
            "opts": opts,
            "app_label": opts.app_label,
            "model_name": opts.model_name,
            "has_view_permission": self.model_admin.has_view_permission(request, obj),
            "has_add_permission": self.model_admin.has_add_permission(request),
            "has_change_permission": self.model_admin.has_change_permission(
                request, obj
            ),
            "has_delete_permission": self.model_admin.has_delete_permission(
                request, obj
            ),
        }
        if obj:
            changelist_url = reverse(
                f"admin:{opts.app_label}_{opts.model_name}_changelist",
                current_app=self.model_admin.admin_site.name,
            )
            change_url = reverse(
                f"admin:{opts.app_label}_{opts.model_name}_change",
                args=[obj.pk],
                current_app=self.model_admin.admin_site.name,
            )
            context.update(
                {
                    "object": obj,
                    "original": obj,
                    "object_id": obj.pk,
                    "original_url": change_url,
                    "changelist_url": changelist_url,
                }
            )
        else:
            context["changelist_url"] = reverse(
                f"admin:{opts.app_label}_{opts.model_name}_changelist",
                current_app=self.model_admin.admin_site.name,
            )
        return context

    def _create_view(
        self,
        view_func: Callable,
        label: str,
        config: ViewConfig,
    ) -> Callable:
        if config.requires_object:
            def wrapper(request, object_id=None, *args, **kwargs):
                obj, redirect = self._check_permissions(request, object_id)
                if redirect:
                    return redirect

                context = self._build_base_context(request, obj)
                context["title"] = label

                payload = view_func(request, obj, *args, **kwargs)

                if isinstance(payload, (HttpResponse, HttpResponseBase)):
                    return payload
                if payload:
                    context.update(payload)

                request.current_app = self.model_admin.admin_site.name
                return TemplateResponse(request, config.template_name, context)
        else:
            def wrapper(request, *args, **kwargs):
                _obj, redirect = self._check_permissions(request, None)
                if redirect:
                    return redirect

                context = self._build_base_context(request, _obj)
                context["title"] = label

                payload = view_func(request, *args, **kwargs)

                if isinstance(payload, (HttpResponse, HttpResponseBase)):
                    return payload
                if payload:
                    context.update(payload)

                request.current_app = self.model_admin.admin_site.name
                return TemplateResponse(request, config.template_name, context)

        return wrapper

    def _generate_admin_custom_view(
        self,
        view_func: Callable,
        label: str,
        config: ViewConfig,
    ) -> Callable:
        """Generate a custom admin view with common configuration."""
        wrapper = self._create_view(view_func, label, config)
        path_fragment = config.path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": config.permission,
        }
        return wrapper
