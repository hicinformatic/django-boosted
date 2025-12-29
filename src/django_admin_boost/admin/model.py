"""ModelAdmin mixin for django-admin-boost."""

from __future__ import annotations

import inspect
from typing import Iterable, List

from django.contrib.admin import ModelAdmin
from django.urls import path, reverse

from .format import format_label, format_status, format_with_help_text
from .fieldsets import add_to_fieldset, remove_from_fieldset
from .views import ViewGenerator


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
    add_to_fieldset = staticmethod(add_to_fieldset)
    remove_from_fieldset = staticmethod(remove_from_fieldset)

    def __init__(self, *args, **kwargs):
        if hasattr(self, "change_fieldsets"):
            self.change_fieldsets()
        super().__init__(*args, **kwargs)


    def get_boost_view_names(self) -> List[str]:
        return list(self.boost_views or [])

    def get_boost_view_config(self, view_name: str) -> dict | None:
        view = getattr(self, view_name, None)
        return getattr(view, "_admin_boost_config", None) if view else None

    def get_boost_object_tools(self, request, object_id: str) -> list[dict]:
        items: list[dict] = []
        for view_name in self.get_boost_view_names():
            config = self.get_boost_view_config(view_name)
            if not config:
                continue
            if not config.get("requires_object", False):
                continue
            if not config.get("show_in_object_tools", True):
                continue
            url = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_{view_name}",
                args=[object_id],
                current_app=self.admin_site.name,
            )
            items.append({"label": config["label"], "url": url})
        return items

    def get_boost_list_tools(self, request) -> list[dict]:
        items: list[dict] = []
        for view_name in self.get_boost_view_names():
            config = self.get_boost_view_config(view_name)
            if not config:
                continue
            if config.get("requires_object", False):
                continue
            if not config.get("show_in_object_tools", True):
                continue
            url = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_{view_name}",
                current_app=self.admin_site.name,
            )
            items.append({"label": config["label"], "url": url})
        return items

    def get_urls(self):
        urls = super().get_urls()
        boost_urls = []
        for view_name in self.get_boost_view_names():
            view = getattr(self, view_name, None)
            config = self.get_boost_view_config(view_name)
            if not view or not config:
                continue

            path_fragment = config.get("path_fragment") or view_name.replace("_", "-")
            requires_object = config.get("requires_object", True)

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

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        view_generator = ViewGenerator(self)
        for attr_name in dir(self.__class__):
            if attr_name.startswith("_"):
                continue
            attr = getattr(self.__class__, attr_name, None)
            if not callable(attr):
                continue
            config = getattr(attr, "_admin_boost_view_config", None)
            if not config:
                continue

            view_type = config["view_type"]
            label = config["label"]
            template_name = config.get("template_name") or "admin_boost/message.html"
            path_fragment = config.get("path_fragment")
            requires_object = config.get("requires_object")
            permission = config.get("permission", "view")

            if requires_object is None:
                sig = inspect.signature(attr)
                params = list(sig.parameters.keys())
                requires_object = len(params) > 2 and "obj" in params[2:]

            original_method = getattr(self, attr_name)

            if view_type == "list":
                if requires_object:
                    view = view_generator.generate_admin_custom_form_view(
                        original_method, label, template_name, path_fragment, permission
                    )
                else:
                    view = view_generator.generate_admin_custom_list_view(
                        original_method, label, template_name, path_fragment, permission
                    )
                view._admin_boost_config["view_type"] = "list"
                view._admin_boost_config["requires_object"] = requires_object
                view._admin_boost_config["show_in_object_tools"] = True
            elif view_type == "form":
                view = view_generator.generate_admin_custom_form_view(
                    original_method, label, template_name, path_fragment, permission
                )
                view._admin_boost_config["requires_object"] = requires_object
                view._admin_boost_config["show_in_object_tools"] = True
            elif view_type == "message":
                view = view_generator.generate_admin_custom_message_view(
                    original_method, label, path_fragment, requires_object, permission
                )
            elif view_type == "json":
                view = view_generator.generate_admin_custom_json_view(
                    original_method, label, path_fragment, requires_object, permission
                )
            else:
                continue

            setattr(self, attr_name, view)

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
        return super().changeform_view(
            request,
            object_id=object_id,
            form_url=form_url,
            extra_context=extra_context,
        )
