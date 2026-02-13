"""List view generator for django-boosted."""

from __future__ import annotations

from typing import Callable

from django.contrib.admin.views.main import ChangeList
from django.http import HttpResponse, HttpResponseBase
from django.template.response import TemplateResponse

from .base import ViewGenerator


class CustomChangeList(ChangeList):
    """ChangeList with an injected queryset."""

    def __init__(self, *args, queryset=None, **kwargs):
        self._custom_queryset = queryset
        super().__init__(*args, **kwargs)

    def get_queryset(self, request):
        if self._custom_queryset is not None:
            return self._custom_queryset
        return super().get_queryset(request)


def build_changelist(
    *,
    request,
    model_admin,
    queryset,
    list_display,
    list_filter,
    search_fields,
):
    list_display_links = model_admin.list_display_links
    if list_display_links is None and list_display:
        list_display_links = (list_display[0],)

    # Use queryset's model if available, otherwise use model_admin's model
    model = getattr(queryset, 'model', None) or model_admin.model

    cl = CustomChangeList(
        request,
        model,
        list_display,
        list_display_links,
        list_filter,
        model_admin.date_hierarchy,
        search_fields,
        model_admin.list_select_related,
        model_admin.list_per_page,
        model_admin.list_max_show_all,
        model_admin.list_editable,
        model_admin,
        model_admin.sortable_by,
        getattr(model_admin, "search_help_text", None),
        queryset=queryset,
    )

    cl.get_results(request)
    if not hasattr(cl, "formset"):
        cl.formset = None
    return cl


class ListViewMixin(ViewGenerator):
    """Mixin for list view generation."""

    def generate_admin_custom_list_view(
        self,
        view_func: Callable,
        label: str,
        *,
        template_name: str = "admin_boost/change_list.html",
        path_fragment: str | None = None,
        requires_object: bool = False,
        permission: str = "view",
    ) -> Callable:

        def render_list_view(request, obj, payload):
            queryset = payload.get("queryset")

            if queryset is None:
                queryset = self.model_admin.model.objects.none()

            list_display = payload.get("list_display", self.model_admin.list_display)
            list_filter = payload.get("list_filter", ())
            search_fields = payload.get("search_fields", ())

            cl = build_changelist(
                request=request,
                model_admin=self.model_admin,
                queryset=queryset,
                list_display=list_display,
                list_filter=list_filter,
                search_fields=search_fields,
            )

            context = self._build_base_context(request, obj)
            context.update({
                "title": label,
                "cl": cl,
                "has_filters": bool(list_filter),
                "has_active_filters": cl.has_active_filters,
                "preserved_filters": self.model_admin.get_preserved_filters(request),
                "action_form": getattr(cl, "action_form", None),
                "actions_on_top": self.model_admin.actions_on_top,
                "actions_on_bottom": self.model_admin.actions_on_bottom,
            })

            context.update({
                k: v
                for k, v in payload.items()
                if k not in {
                    "queryset",
                    "list_display",
                    "list_filter",
                    "search_fields",
                }
            })

            request.current_app = self.model_admin.admin_site.name
            return TemplateResponse(request, template_name, context)

        def wrapper(request, object_id=None, *args, **kwargs):
            obj, redirect = self._check_permissions(
                request,
                object_id if requires_object else None,
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

            return render_list_view(request, obj, payload or {})

        path = path_fragment or view_func.__name__.replace("_", "-")
        wrapper._admin_boost_config = {  # type: ignore[attr-defined]
            "label": label,
            "path_fragment": path,
            "permission": permission,
            "view_type": "list",
            "requires_object": requires_object,
            "show_in_object_tools": True,
        }

        return wrapper
