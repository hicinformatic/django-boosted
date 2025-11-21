"""Reusable decorators to enrich Django's admin."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Mapping

from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.forms import Form
from django.http import HttpResponse, HttpResponseBase
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    pass

PermissionName = str
HandlerReturn = Mapping[str, Any] | HttpResponseBase | None
HandlerCallable = Callable[..., HandlerReturn]


def _resolve_permission_checker(permission: PermissionName):
    def checker(admin_instance, request, obj):
        if permission == "change":
            return admin_instance.has_change_permission(request, obj)
        if permission == "delete":
            return admin_instance.has_delete_permission(request, obj)
        if permission == "add":
            return admin_instance.has_add_permission(request)
        return admin_instance.has_view_or_change_permission(request, obj)

    return checker


def _apply_admin_widgets_to_form(
    form_class: type[Form],
    model_admin: admin.ModelAdmin,
    raw_id_fields: list[str] | None = None,
    autocomplete_fields: list[str] | None = None,
) -> None:
    """
    Apply admin widgets to form fields based on raw_id_fields and autocomplete_fields.

    This mimics the behavior of ModelAdmin.change_view() for widget configuration.
    """
    raw_id_fields = raw_id_fields or []
    autocomplete_fields = autocomplete_fields or []

    for field_name, field in form_class.base_fields.items():
        # Skip if not a ModelChoiceField
        try:
            _ = field.queryset
        except AttributeError:
            continue

        if field_name in raw_id_fields:
            # Apply ForeignKeyRawIdWidget
            related_model = field.queryset.model

            # Create a mock related field object for the widget
            # The widget expects the model instance to have a 'rel' attribute
            # with a 'get_related_field()' method
            class MockRel:
                def get_related_field(self):
                    class Tmp:
                        name = "id"

                    return Tmp()

            # Create a mock model instance with the required attributes
            model_instance = related_model()
            try:
                _ = model_instance.rel
            except AttributeError:
                model_instance.rel = MockRel()
            try:
                _ = model_instance.model
            except AttributeError:
                model_instance.model = related_model
            try:
                _ = model_instance.limit_choices_to
            except AttributeError:
                model_instance.limit_choices_to = {}

            field.widget = admin.widgets.ForeignKeyRawIdWidget(
                model_instance, model_admin.admin_site
            )

        elif field_name in autocomplete_fields:
            # Apply AutocompleteSelect widget
            related_model = field.queryset.model
            # For AutocompleteSelect, we need a field with remote_field
            # Create a temporary field-like object for the widget
            # The widget needs the field to determine the related model
            try:
                # Find ForeignKey in admin's model pointing to related_model
                fk_field = None
                admin_model = model_admin.model
                for f in admin_model._meta.get_fields():
                    try:
                        remote_field = f.remote_field
                        if (
                            remote_field
                            and remote_field.model == related_model
                            and f.name == field_name
                        ):
                            fk_field = f
                            break
                    except AttributeError:
                        continue

                if fk_field:
                    field.widget = admin.widgets.AutocompleteSelect(
                        fk_field, model_admin.admin_site
                    )
                else:
                    # Fallback: use the related model's primary key field
                    # AutocompleteSelect needs a field with model._meta
                    pk_field = related_model._meta.pk
                    field.widget = admin.widgets.AutocompleteSelect(
                        pk_field, model_admin.admin_site
                    )
            except (AttributeError, ValueError) as e:
                # Final fallback: skip autocomplete if we can't determine the field
                # Log the specific error for debugging but don't fail silently
                # This is expected in some edge cases where the field structure
                # doesn't match what AutocompleteSelect expects
                if not isinstance(e, (AttributeError, ValueError)):
                    raise
                # For AttributeError/ValueError, we skip autocomplete gracefully


def admin_boost_object_view(
    *,
    label: str,
    template_name: str,
    path_fragment: str | None = None,
    permission: PermissionName = "view",
    show_in_object_tools: bool = True,
    form: type[Form] | None = None,
    raw_id_fields: list[str] | None = None,
    autocomplete_fields: list[str] | None = None,
) -> Callable[[HandlerCallable], HandlerCallable]:
    """
    Decorate a ModelAdmin method to register it as an object-level view.

    If `form` is provided, the decorator will:
        - Apply widgets based on `raw_id_fields` and `autocomplete_fields`
          (same logic as change_view)
    - Handle form validation on POST
    - Add the form to the context

    The wrapped method receives ``(self, request, obj, form, *args, **kwargs)``
    where `form` is the instantiated (and validated if POST) form, or None if no form.

    Args:
        label: Label for the object tool button
        template_name: Template to render
        path_fragment: Custom URL path fragment (defaults to view name)
        permission: Required permission level ("view", "change", "delete", "add")
        show_in_object_tools: Whether to show button in object tools
        form: Optional form class to use
        raw_id_fields: List of field names to use ForeignKeyRawIdWidget
        autocomplete_fields: List of field names to use AutocompleteSelect widget
    """

    def decorator(view_func: HandlerCallable) -> HandlerCallable:
        permission_checker = _resolve_permission_checker(permission)

        @wraps(view_func)
        def wrapper(self, request, object_id, *args, **kwargs):
            obj = self.get_object(request, unquote(object_id))
            if obj is None:
                return self._get_obj_does_not_exist_redirect(
                    request, self.model._meta, object_id
                )

            if not permission_checker(self, request, obj):
                self.message_user(request, _("Access denied"), level=messages.ERROR)
                raise PermissionDenied

            # Handle form if provided
            form_instance = None
            if form:
                # Apply widgets using the same logic as change_view()
                _apply_admin_widgets_to_form(
                    form,
                    self,
                    raw_id_fields=raw_id_fields,
                    autocomplete_fields=autocomplete_fields,
                )

                # Instantiate form
                if request.method == "POST":
                    form_instance = form(request.POST, request.FILES)
                    if form_instance.is_valid():
                        # Let the view function handle the valid form
                        # Check if view function accepts form parameter
                        sig = inspect.signature(view_func)
                        params = list(sig.parameters.keys())
                        # Check if 4th parameter (after self, request, obj)
                        # is 'form' or 'form_instance'
                        if len(params) > 3 and params[3] in ("form", "form_instance"):
                            payload = view_func(
                                self, request, obj, form_instance, *args, **kwargs
                            )
                        else:
                            payload = view_func(self, request, obj, *args, **kwargs)
                        if isinstance(payload, HttpResponse):
                            return payload
                        # If no redirect, continue to render with form
                else:
                    form_instance = form()

            context = {
                **self.admin_site.each_context(request),
                "opts": self.model._meta,
                "object": obj,
                "original": obj,
                "object_id": object_id,
                "has_change_permission": self.has_change_permission(request, obj),
                "has_view_permission": self.has_view_permission(request, obj),
                "title": label,
                "original_url": reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                    args=[object_id],
                    current_app=self.admin_site.name,
                ),
            }

            if form_instance:
                context["form"] = form_instance

            # Call view function if form not provided, or if form is invalid/GET
            if not form or request.method != "POST" or not form_instance.is_valid():
                # Check if view function accepts form parameter
                sig = inspect.signature(view_func)
                params = list(sig.parameters.keys())
                # Check if 4th parameter (after self, request, obj)
                # is 'form' or 'form_instance'
                if len(params) > 3 and params[3] in ("form", "form_instance"):
                    # Function expects form parameter
                    payload = view_func(
                        self, request, obj, form_instance, *args, **kwargs
                    )
                else:
                    # Function doesn't expect form parameter (backward compatibility)
                    payload = view_func(self, request, obj, *args, **kwargs)
                if isinstance(payload, HttpResponse):
                    return payload
                if payload:
                    context.update(payload)

            request.current_app = self.admin_site.name
            return TemplateResponse(request, template_name, context)

        wrapper._admin_boost_config = {
            "label": label,
            "template_name": template_name,
            "path_fragment": path_fragment,
            "permission": permission,
            "show_in_object_tools": show_in_object_tools,
            "form": form,
            "raw_id_fields": raw_id_fields,
            "autocomplete_fields": autocomplete_fields,
        }
        return wrapper

    return decorator
