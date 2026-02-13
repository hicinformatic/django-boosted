"""ModelAdmin mixin for django-boosted."""

from __future__ import annotations

import copy
from typing import Iterable

from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.contrib.admin.utils import unquote
from django.urls import path, reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .fieldsets import add_to_fieldset, remove_from_fieldset
from .format import format_label, format_status, format_with_help_text
from .tools import (
    get_boost_list_tools,
    get_boost_object_tools,
    get_boost_view_config,
    get_boost_view_names,
)
from .views import ViewGenerator, setup_boost_views


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

            opts = self.model._meta
            path_name = f"{opts.app_label}_{opts.model_name}_{view_name}"
            if requires_object:
                boost_urls.append(
                    path(
                        f"<path:object_id>/{path_fragment}/",
                        self.admin_site.admin_view(view),
                        name=path_name,
                    )
                )
            else:
                boost_urls.append(
                    path(
                        f"{path_fragment}/",
                        self.admin_site.admin_view(view),
                        name=path_name,
                    )
                )
        return boost_urls + urls

    def __init__(self, *args, **kwargs):
        if hasattr(self, "fieldsets") and self.fieldsets is not None:
            self.fieldsets = copy.deepcopy(self.fieldsets)
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
        obj = None
        if object_id:
            obj = self.get_object(request, unquote(object_id))
            items = list(extra_context.get("object_tools_items") or [])
            items.extend(self.get_boost_object_tools(request, object_id))
            extra_context["object_tools_items"] = items

        if "submit_actions" not in extra_context:
            extra_context["submit_actions"] = self.get_submit_actions(request, obj)

        if request.method == "POST":
            submit_actions = extra_context.get("submit_actions", {})
            django_actions = {
                "_save", "_saveasnew", "_addanother", "_continue",
                "_saveas", "_save_and_continue",
            }
            for action_name in submit_actions.keys():
                if action_name in request.POST and action_name not in django_actions:
                    custom_response = self.handle_custom_action(
                        action_name, request, object_id
                    )
                    if custom_response is not None:
                        return custom_response
                    from django.shortcuts import redirect
                    url = request.build_absolute_uri(request.path)
                    if url_has_allowed_host_and_scheme(
                        url, allowed_hosts=request.get_host()
                    ):
                        redirect_url = request.path
                    else:
                        opts = self.model._meta
                        redirect_url = reverse(
                            f"admin:{opts.app_label}_{opts.model_name}_change",
                            args=[object_id] if object_id else [],
                            current_app=self.admin_site.name,
                        )
                    return redirect(redirect_url)

        return super().changeform_view(
            request,
            object_id=object_id,
            form_url=form_url,
            extra_context=extra_context,
        )

    def handle_custom_action(self, action_name, request, object_id=None):
        """Handle custom form actions. Override handle_<action_name>."""
        handler_method = getattr(self, f"handle_{action_name}", None)
        if handler_method:
            return handler_method(request, object_id)

        messages.warning(
            request,
            f"Action '{action_name}' is defined but no handler "
            f"method 'handle_{action_name}' exists.",
        )
        return None

    def get_action_permission(self, request, action, obj=None):
        perm = f"has_{action}_permission"
        if hasattr(self, perm):
            perm_method = getattr(self, perm)
            if callable(perm_method):
                return perm_method(request, obj)
            return perm_method
        return True

    def get_submit_actions(self, request, obj=None):
        """Return dict of custom submit actions. Uses changeform_actions if defined."""
        changeform_actions = getattr(self, "changeform_actions", {})
        actions_enable = {}
        for action_name, action_label in changeform_actions.items():
            perm = self.get_action_permission(request, action_name, obj)
            handle = hasattr(self, f"handle_{action_name}")
            if perm and handle:
                actions_enable[action_name] = action_label
        return actions_enable
