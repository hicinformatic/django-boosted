"""Admin form view generator for django-boosted."""

from __future__ import annotations

from typing import Callable

from django.http import HttpResponse, HttpResponseBase
from django.template.response import TemplateResponse

from .base import ViewGenerator


class AdminFormViewMixin(ViewGenerator):
    """Mixin for admin form view generation."""

    def generate_admin_custom_adminform_view(
        self,
        view_func: Callable,
        label: str,
        *,
        template_name: str = "admin_boost/change_form.html",
        path_fragment: str | None = None,
        requires_object: bool = True,
        permission: str = "view",
    ) -> Callable:
        from django.contrib.admin.helpers import AdminErrorList, AdminForm
        from django.forms import Form

        def wrapper(request, object_id=None, *args, **kwargs):
            obj, redirect = self._check_permissions(
                request, object_id if requires_object else None
            )
            if redirect:
                return redirect

            payload = (
                view_func(request, obj, *args, **kwargs)
                if requires_object
                else view_func(request, *args, **kwargs)
            )

            if isinstance(payload, (HttpResponse, HttpResponseBase)):
                return payload

            if isinstance(payload, dict):
                form = payload.get("form")
            elif isinstance(payload, Form):
                form = payload
            else:
                form = None

            if form is None:
                raise ValueError(
                    f"{view_func.__name__} must return a form or a dict with a "
                    "'form' key"
                )

            if request.method == "POST":
                from django.forms import ModelForm
                # Only pass instance for ModelForm, not regular Form
                if isinstance(form, ModelForm):
                    instance = getattr(form, "instance", None)
                    form = form.__class__(
                        request.POST, request.FILES, instance=instance
                    )
                else:
                    form = form.__class__(request.POST, request.FILES)
                if form.is_valid():
                    result = (
                        view_func(request, obj, form=form, *args, **kwargs)
                        if requires_object
                        else view_func(request, form=form, *args, **kwargs)
                    )
                    if isinstance(result, (HttpResponse, HttpResponseBase)):
                        return result
                    if isinstance(result, dict) and "redirect_url" in result:
                        from django.shortcuts import redirect as django_redirect
                        return django_redirect(result["redirect_url"])
                    form = (
                        result.get("form", form) if isinstance(result, dict) else form
                    )
                    if isinstance(result, dict):
                        payload = result
                else:
                    if isinstance(payload, dict):
                        payload["form"] = form

            context = self._build_base_context(request, obj)
            context["title"] = label

            fieldsets = [(None, {"fields": list(form.fields.keys())})]

            adminform = AdminForm(
                form,
                fieldsets,
                {},
                readonly_fields=(),
                model_admin=self.model_admin,
            )

            # Get permission values from payload or model_admin defaults
            has_add_perm = (
                payload.get("has_add_permission")
                if isinstance(payload, dict) and "has_add_permission" in payload
                else self.model_admin.has_add_permission(request)
            )
            has_change_perm = (
                payload.get("has_change_permission")
                if isinstance(payload, dict) and "has_change_permission" in payload
                else self.model_admin.has_change_permission(request, obj)
            )
            has_delete_perm = (
                payload.get("has_delete_permission")
                if isinstance(payload, dict) and "has_delete_permission" in payload
                else self.model_admin.has_delete_permission(request, obj)
            )

            context.update(
                {
                    "adminform": adminform,
                    "errors": AdminErrorList(form, []),
                    "inline_admin_formsets": [],
                    "inline_admin_formset": [],
                    # Required for Django 4.2+
                    "has_editable_inline_admin_formsets": False,
                    "media": self.model_admin.media + form.media,
                    "preserved_filters": "",
                    "prepopulated_fields": {},
                    "prepopulated_fields_json": "[]",
                    "has_view_permission": self.model_admin.has_view_permission(
                        request, obj
                    ),
                    "has_add_permission": has_add_perm,
                    "has_change_permission": has_change_perm,
                    "has_delete_permission": has_delete_perm,
                    "show_save": True,
                    "show_save_and_continue": False,
                    "show_save_and_add_another": False,
                    "show_delete": False,
                    "show_close": False,
                    "add": False,
                    "change": True,
                    "is_popup": False,
                    "save_as": False,
                    "save_on_top": False,
                }
            )

            if isinstance(payload, dict):
                if "form" in payload:
                    new_form = payload["form"]
                    if new_form != form:
                        form = new_form
                        fieldsets = [(None, {"fields": list(form.fields.keys())})]
                        context["adminform"] = AdminForm(
                            form,
                            fieldsets,
                            {},
                            readonly_fields=(),
                            model_admin=self.model_admin,
                        )
                        context["errors"] = AdminErrorList(form, [])
                        context["media"] = self.model_admin.media + form.media

                excluded_keys = {
                    "form", "has_add_permission", "has_change_permission",
                    "has_delete_permission",
                }
                context.update(
                    {k: v for k, v in payload.items() if k not in excluded_keys}
                )

            request.current_app = self.model_admin.admin_site.name
            return TemplateResponse(request, template_name, context)

        path_fragment = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path_fragment,
            "permission": permission,
            "view_type": "adminform",
            "requires_object": requires_object,
            "show_in_object_tools": True,
        }
        return wrapper
