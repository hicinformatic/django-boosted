"""Confirm view generator for django-boosted."""

from __future__ import annotations

from typing import Callable

from django.http import HttpResponse, HttpResponseBase
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .base import ViewGenerator


class ConfirmViewMixin(ViewGenerator):
    """Mixin for confirm view generation."""

    def generate_admin_custom_confirm_view(
        self,
        view_func: Callable,
        label: str,
        *,
        template_name: str = "admin_boost/confirm.html",
        path_fragment: str | None = None,
        requires_object: bool = False,
        permission: str = "view",
    ) -> Callable:

        def _safe_redirect_url(request, fallback: str) -> str:
            referer = request.META.get("HTTP_REFERER")
            if referer:
                url = request.build_absolute_uri(referer)
                if url_has_allowed_host_and_scheme(
                    url, allowed_hosts=request.get_host()
                ):
                    return referer
            return fallback

        def wrapper(request, object_id=None, *args, **kwargs):
            obj, redirect_response = self._check_permissions(
                request, object_id if requires_object else None
            )
            if redirect_response:
                return redirect_response

            if request.method == "POST":
                action = request.POST.get("action")
                opts = self.model_admin.model._meta
                fallback = reverse(
                    f"admin:{opts.app_label}_{opts.model_name}_changelist",
                    current_app=self.model_admin.admin_site.name,
                )
                if action == "confirm":
                    result = (
                        view_func(request, obj, confirmed=True, *args, **kwargs)
                        if requires_object
                        else view_func(request, confirmed=True, *args, **kwargs)
                    )
                    if isinstance(result, (HttpResponse, HttpResponseBase)):
                        return result
                return redirect(_safe_redirect_url(request, fallback))

            payload = (
                view_func(request, obj, *args, **kwargs)
                if requires_object
                else view_func(request, *args, **kwargs)
            )

            if isinstance(payload, (HttpResponse, HttpResponseBase)):
                return payload

            confirm_message = payload.get("confirm", "Are you sure?")
            choices = payload.get("choices", ["Confirm", "Cancel"])

            context = self._build_base_context(request, obj)
            context.update({
                "title": label,
                "confirm_message": confirm_message,
                "confirm_choice": choices[0] if len(choices) > 0 else "Confirm",
                "cancel_choice": choices[1] if len(choices) > 1 else "Cancel",
            })

            if payload:
                excluded = ["confirm", "choices"]
                context.update({k: v for k, v in payload.items() if k not in excluded})

            request.current_app = self.model_admin.admin_site.name
            return TemplateResponse(request, template_name, context)

        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
            "view_type": "confirm",
            "requires_object": requires_object,
            "show_in_object_tools": True,
        }
        return wrapper
