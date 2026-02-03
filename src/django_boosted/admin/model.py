"""ModelAdmin mixin for django-boosted."""

from __future__ import annotations

from typing import Iterable

from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.urls import path

from .fieldsets import add_to_fieldset, remove_from_fieldset
from .format import format_label, format_status, format_with_help_text
from .tools import (
    get_boost_list_tools,
    get_boost_object_tools,
    get_boost_view_config,
    get_boost_view_names,
)
from .views import ViewGenerator
from .views_setup import setup_boost_views


class AdminBoostModel(ModelAdmin):
    change_form_template = "admin_boost/change_form.html"
    change_list_template = "admin_boost/change_list.html"
    boost_views: Iterable[str] = ()

    class Media:
        css = {
            "all": ("admin_boost/admin_boost.css",),
        }

    format_label = staticmethod(format_label)
    format_status = staticmethod(format_status)
    format_with_help_text = staticmethod(format_with_help_text)
    add_to_fieldset = add_to_fieldset
    remove_from_fieldset = remove_from_fieldset
    get_boost_view_names = get_boost_view_names
    get_boost_view_config = get_boost_view_config
    get_boost_object_tools = get_boost_object_tools
    get_boost_list_tools = get_boost_list_tools

    def get_urls(self):
        urls = super().get_urls()
        boost_urls = []
        for view_name in self.get_boost_view_names():
            view = getattr(self, view_name, None)
            config = self.get_boost_view_config(view_name)
            if not view or not config:
                continue

            path_fragment = config.get("path_fragment") or view_name.replace("_", "-")
            requires_object = config.get("requires_object", False)

            if requires_object:
                boost_urls.append(
                    path(
                        f"<path:object_id>/{path_fragment}/",
                        self.admin_site.admin_view(view),
                        name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_{view_name}",
                    )
                )
            else:
                boost_urls.append(
                    path(
                        f"{path_fragment}/",
                        self.admin_site.admin_view(view),
                        name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_{view_name}",
                    )
                )
        return boost_urls + urls

    def __init__(self, *args, **kwargs):
        if hasattr(self, "change_fieldsets"):
            self.change_fieldsets()
        super().__init__(*args, **kwargs)
        view_generator = ViewGenerator(self)
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            func = getattr(attr, "__func__", attr)
            if hasattr(func, "_admin_boost_view_config"):
                self.boost_views += (func._admin_boost_view_config["name"],)
        setup_boost_views(self, view_generator)

    def has_change_permission(self, request, obj=None):
        """Allow change form if custom actions are defined."""
        if getattr(self, "changeform_actions", None):
            return True
        return super().has_change_permission(request, obj)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        items = list(extra_context.get("object_tools_items") or [])
        items.extend(self.get_boost_list_tools(request))
        extra_context["object_tools_items"] = items
        return super().changelist_view(request, extra_context)


    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            items = list(extra_context.get("object_tools_items") or [])
            items.extend(self.get_boost_object_tools(request, object_id))
            extra_context["object_tools_items"] = items
        if "submit_actions" not in extra_context:
            extra_context["submit_actions"] = self.get_submit_actions(request, object_id)
        
        if request.method == "POST":
            submit_actions = extra_context.get("submit_actions", {})
            django_actions = {"_save", "_saveasnew", "_addanother", "_continue", "_saveas", "_save_and_continue"}
            for action_name in submit_actions.keys():
                if action_name in request.POST and action_name not in django_actions:
                    custom_response = self.handle_custom_action(action_name, request, object_id)
                    if custom_response is not None:
                        return custom_response
                    from django.shortcuts import redirect
                    return redirect(request.path)
        
        return super().changeform_view(
            request,
            object_id=object_id,
            form_url=form_url,
            extra_context=extra_context,
        )

    def handle_custom_action(self, action_name, request, object_id=None):
        """Handle custom form actions. Override handle_<action_name> for specific actions."""
        handler_method = getattr(self, f"handle_{action_name}", None)
        if handler_method:
            return handler_method(request, object_id)
        
        messages.warning(
            request,
            f"Action '{action_name}' is defined but no handler method 'handle_{action_name}' exists."
        )
        return None

    def get_submit_actions(self, request, object_id=None):
        """Return dict of custom submit actions. Uses changeform_actions if defined."""
        changeform_actions = getattr(self, "changeform_actions", None)
        if changeform_actions is None:
            return {}
        if isinstance(changeform_actions, dict):
            return changeform_actions
        if isinstance(changeform_actions, (list, tuple)):
            return dict(changeform_actions)
        return {}
