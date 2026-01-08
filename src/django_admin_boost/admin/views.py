"""View generation utilities for django-admin-boost."""

from __future__ import annotations

from typing import Callable

from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBase, JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse


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
        else:
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
        template_name: str,
        requires_object: bool = False,
        permission: str = "view",
    ) -> Callable:
        def wrapper(request, object_id=None, *args, **kwargs):
            obj, redirect = self._check_permissions(
                request, object_id if requires_object else None
            )
            if redirect:
                return redirect

            context = self._build_base_context(request, obj)
            context["title"] = label

            if requires_object:
                payload = view_func(request, obj, *args, **kwargs)
            else:
                payload = view_func(request, *args, **kwargs)

            if isinstance(payload, (HttpResponse, HttpResponseBase)):
                return payload
            if payload:
                context.update(payload)

            request.current_app = self.model_admin.admin_site.name
            return TemplateResponse(request, template_name, context)

        return wrapper

    def _generate_admin_custom_view(
        self,
        view_func: Callable,
        label: str,
        template_name: str,
        requires_object: bool = False,
        permission: str = "view",
    ) -> Callable:
        wrapper = self._create_view(
            view_func, label, template_name, requires_object, permission
        )
        path_fragment = view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
        }
        return wrapper

    def _generate_admin_custom_list_view(
        self,
        view_func: Callable,
        label: str,
        template_name: str = "admin_boost/change_list.html",
        path_fragment: str | None = None,
        permission: str = "view",
    ) -> Callable:
        wrapper = self._create_view(
            view_func,
            label,
            template_name,
            requires_object=False,
            permission=permission,
        )
        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
        }
        return wrapper

    def _generate_admin_custom_form_view(
        self,
        view_func: Callable,
        label: str,
        template_name: str = "admin_boost/change_form.html",
        path_fragment: str | None = None,
        permission: str = "view",
    ) -> Callable:
        wrapper = self._create_view(
            view_func, label, template_name, requires_object=True, permission=permission
        )
        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
        }
        return wrapper

    def _generate_admin_custom_message_view(
        self,
        view_func: Callable,
        label: str,
        template_name: str = "admin_boost/message.html",
        path_fragment: str | None = None,
        requires_object: bool = False,
        permission: str = "view",
    ) -> Callable:
        wrapper = self._create_view(
            view_func,
            label,
            template_name,
            requires_object=requires_object,
            permission=permission,
        )
        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
        }
        return wrapper

    def generate_admin_custom_list_view(
        self,
        view_func: Callable,
        label: str,
        template_name: str = "admin_boost/change_list.html",
        path_fragment: str | None = None,
        permission: str = "view",
    ) -> Callable:
        wrapper = self._generate_admin_custom_list_view(
            view_func, label, template_name, path_fragment, permission
        )
        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
            "view_type": "list",
            "requires_object": False,
            "show_in_object_tools": True,
        }
        return wrapper

    def generate_admin_custom_form_view(
        self,
        view_func: Callable,
        label: str,
        template_name: str = "admin_boost/change_form.html",
        path_fragment: str | None = None,
        permission: str = "view",
    ) -> Callable:
        wrapper = self._generate_admin_custom_form_view(
            view_func, label, template_name, path_fragment, permission
        )
        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
            "view_type": "form",
            "requires_object": True,
            "show_in_object_tools": True,
        }
        return wrapper

    def generate_admin_custom_message_view(
        self,
        view_func: Callable,
        label: str,
        template_name: str = "admin_boost/message.html",
        path_fragment: str | None = None,
        requires_object: bool = False,
        permission: str = "view",
    ) -> Callable:
        wrapper = self._generate_admin_custom_message_view(
            view_func, label, template_name, path_fragment, requires_object, permission
        )
        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config.update(  # type: ignore[attr-defined]
            {
                "view_type": "message",
                "requires_object": requires_object,
                "show_in_object_tools": True,
            }
        )
        return wrapper

    def generate_admin_custom_json_view(
        self,
        view_func: Callable,
        label: str,
        template_name: str | None = None,
        path_fragment: str | None = None,
        requires_object: bool = False,
        permission: str = "view",
    ) -> Callable:
        import inspect

        def wrapper(request, object_id=None, *args, **kwargs):
            obj, redirect = self._check_permissions(
                request, object_id if requires_object else None
            )
            if redirect:
                return redirect

            # Vérifier la signature de la méthode pour savoir si elle accepte obj
            sig = inspect.signature(view_func)
            params = list(sig.parameters.keys())
            method_accepts_obj = len(params) > 2 and "obj" in params[2:]

            if requires_object and method_accepts_obj:
                payload = view_func(request, obj, *args, **kwargs)
            else:
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
