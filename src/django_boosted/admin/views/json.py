"""JSON view generator for django-boosted."""

from __future__ import annotations

from typing import Callable

from django.http import HttpResponse, HttpResponseBase, JsonResponse

from .base import ViewGenerator


class JsonViewMixin:
    """Mixin for JSON view generation."""

    def generate_admin_custom_json_view(
        self: ViewGenerator,
        view_func: Callable,
        label: str,
        *,
        _template_name: str | None = None,
        path_fragment: str | None = None,
        requires_object: bool = False,
        permission: str = "view",
    ) -> Callable:

        if requires_object:
            def wrapper(request, object_id=None, *args, **kwargs):
                obj, redirect = self._check_permissions(request, object_id)
                if redirect:
                    return redirect

                payload = view_func(request, obj, *args, **kwargs)

                if isinstance(payload, (HttpResponse, HttpResponseBase)):
                    return payload

                return JsonResponse(payload, safe=False)
        else:
            def wrapper(request, *args, **kwargs):
                _obj, redirect = self._check_permissions(request, None)
                if redirect:
                    return redirect

                payload = view_func(request, *args, **kwargs)

                if isinstance(payload, (HttpResponse, HttpResponseBase)):
                    return payload

                return JsonResponse(payload, safe=False)

        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
            "view_type": "json",
            "requires_object": requires_object,
            "show_in_object_tools": True,
        }
        return wrapper
