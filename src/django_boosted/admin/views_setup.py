"""Views setup logic for django-boosted."""

import inspect

from .views import ViewGenerator


def setup_boost_views(self, view_generator: ViewGenerator):
    """Setup boost views from class attributes."""
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
        template_name = config.get("template_name")  # None si non spécifié, laisse chaque méthode utiliser son défaut
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
                    original_method,
                    label,
                    template_name=template_name,
                    path_fragment=path_fragment,
                    permission=permission,
                )
            else:
                view = view_generator.generate_admin_custom_list_view(
                    original_method,
                    label,
                    template_name=template_name,
                    path_fragment=path_fragment,
                    permission=permission,
                )
            view._admin_boost_config["view_type"] = "list"  # type: ignore[attr-defined]
            view._admin_boost_config["requires_object"] = (  # type: ignore[attr-defined]
                requires_object
            )
            view._admin_boost_config["show_in_object_tools"] = True  # type: ignore[attr-defined]
        elif view_type == "form":
            kwargs = {"path_fragment": path_fragment, "permission": permission}
            if template_name is not None:
                kwargs["template_name"] = template_name
            view = view_generator.generate_admin_custom_form_view(
                original_method,
                label,
                **kwargs
            )
            view._admin_boost_config["requires_object"] = (  # type: ignore[attr-defined]
                requires_object
            )
            view._admin_boost_config["show_in_object_tools"] = True  # type: ignore[attr-defined]
        elif view_type == "message":
            view = view_generator.generate_admin_custom_message_view(
                original_method,
                label,
                template_name=template_name,
                path_fragment=path_fragment,
                requires_object=requires_object,
                permission=permission,
            )
        elif view_type == "json":
            view = view_generator.generate_admin_custom_json_view(
                original_method,
                label,
                _template_name=template_name,
                path_fragment=path_fragment,
                requires_object=requires_object,
                permission=permission,
            )
            view._admin_boost_config["requires_object"] = (  # type: ignore[attr-defined]
                requires_object
            )
            view._admin_boost_config["show_in_object_tools"] = True  # type: ignore[attr-defined]
        elif view_type == "adminform":
            kwargs = {"path_fragment": path_fragment, "permission": permission}
            if template_name is not None:
                kwargs["template_name"] = template_name
            view = view_generator.generate_admin_custom_adminform_view(
                original_method,
                label,
                **kwargs
            )
            view._admin_boost_config["requires_object"] = (  # type: ignore[attr-defined]
                requires_object
            )
            view._admin_boost_config["show_in_object_tools"] = True  #
        else:
            continue

        setattr(self, attr_name, view)
