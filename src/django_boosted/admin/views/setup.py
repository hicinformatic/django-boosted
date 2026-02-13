"""Views setup logic for django-boosted."""

import inspect

from .generator import ViewGenerator


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
        template_name = config.get("template_name")
        path_fragment = config.get("path_fragment")
        requires_object = config.get("requires_object")
        permission = config.get("permission", "view")

        if requires_object is None:
            sig = inspect.signature(attr)
            params = list(sig.parameters.keys())
            requires_object = len(params) > 2 and "obj" in params[2:]

        original_method = getattr(self, attr_name)

        kwargs = {
            "path_fragment": path_fragment,
            "requires_object": requires_object,
            "permission": permission,
        }

        if template_name is not None:
            # JSON uses _template_name instead of template_name
            template_key = "_template_name" if view_type == "json" else "template_name"
            kwargs[template_key] = template_name

        method_name = f"generate_admin_custom_{view_type}_view"
        generator_method = getattr(view_generator, method_name, None)

        if generator_method is None:
            continue

        view = generator_method(original_method, label, **kwargs)
        setattr(self, attr_name, view)
