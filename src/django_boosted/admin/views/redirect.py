"""Redirect view generator for django-boosted."""

from __future__ import annotations

from typing import Callable

from django.http import HttpResponseBase
from django.shortcuts import redirect

from .base import ViewConfig, ViewGenerator


class RedirectViewMixin(ViewGenerator):
    """Mixin for redirect view generation.

    The view function may return:
    - A URL string: will be used for redirect.
    - An HttpResponse/HttpResponseRedirect: returned as-is.
    """

    def generate_admin_custom_redirect_view(
        self,
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
        wrapper = self._generate_redirect_view(view_func, label, config)
        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config.update(  # type: ignore[attr-defined]
            {
                "view_type": "redirect",
                "requires_object": requires_object,
                "show_in_object_tools": True,
            }
        )
        return wrapper

    def _generate_redirect_view(
        self,
        view_func: Callable,
        label: str,
        config: ViewConfig,
    ) -> Callable:
        """Generate redirect view: URL string is converted to redirect()."""
        base_wrapper = self._generate_admin_custom_view(view_func, label, config)

        if config.requires_object:
            def redirect_wrapper(request, object_id=None, *args, **kwargs):
                obj, redir = self._check_permissions(request, object_id)
                if redir:
                    return redir
                payload = view_func(request, obj, *args, **kwargs)
                if isinstance(payload, HttpResponseBase):
                    return payload
                if isinstance(payload, str):
                    return redirect(payload)
                return redirect("admin:index")
        else:
            def redirect_wrapper(request, *args, **kwargs):
                _obj, redir = self._check_permissions(request, None)
                if redir:
                    return redir
                payload = view_func(request, *args, **kwargs)
                if isinstance(payload, HttpResponseBase):
                    return payload
                if isinstance(payload, str):
                    return redirect(payload)
                return redirect("admin:index")

        redirect_wrapper._admin_boost_config = base_wrapper._admin_boost_config
        return redirect_wrapper
