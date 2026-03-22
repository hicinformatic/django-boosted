# django-boosted

Lightweight helpers to extend Django’s admin with extra views, custom forms, and the matching UI affordances (object tools, permissions, standard responses).

## Features

- **`@admin_boost_object_view` decorator** – fetches the target object, checks permissions, and builds the default context before rendering your template.
- **`AdminBoostMixin`** – registers the custom URLs, protects them with `admin_site.admin_view`, and injects extra object-tool buttons into the change form.
- **`AuditMixin`** – adds `created_by`, `updated_by`, `created_at`, `updated_at` with automatic user tracking via middleware.
- **Additional templates** – a change form template that renders the injected buttons plus a simple “Hello” view as a teaching aid.

## Installation

```bash
pip install django-boosted
```

## Quick start

```python
# app/admin.py
from django.contrib import admin
from django_boosted.mixins import AdminBoostMixin
from django_boosted.decorators import admin_boost_object_view
from .models import Client


class ClientAdmin(AdminBoostMixin, admin.ModelAdmin):
    boost_views = ["hello_view"]
    change_form_template = "admin_boost/change_form.html"

    @admin_boost_object_view(label="Say hello", template_name="admin_boost/hello.html")
    def hello_view(self, request, obj):
        return {"message": f"Hello {obj}!"}


admin.site.register(Client, ClientAdmin)
```

Include the provided templates in your `TEMPLATES["DIRS"]` (or copy them to customize).

## Using forms with ForeignKey widgets

The decorator can automatically apply admin widgets (`ForeignKeyRawIdWidget` or `AutocompleteSelect`) to your form fields, using the same logic as `ModelAdmin.change_view()`:

```python
# app/admin.py
from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect
from django_boosted.mixins import AdminBoostMixin
from django_boosted.decorators import admin_boost_object_view
from .models import Company

class SyncFullGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Company.objects.all())
    option = forms.ChoiceField(
        label="sync method",
        choices=[("method1", "Method 1"), ("method2", "Method 2")],
    )

class CompanyAdmin(AdminBoostMixin, admin.ModelAdmin):
    boost_views = ["sync_full_group_view"]
    change_form_template = "admin_boost/change_form.html"

    @admin_boost_object_view(
        label="Sync Full Group",
        template_name="admin/sync_full_group.html",
        form=SyncFullGroupForm,
        raw_id_fields=["group"],  # Automatically applies ForeignKeyRawIdWidget
    )
    def sync_full_group_view(self, request, obj, form):
        if request.method == "POST" and form.is_valid():
            # Process form...
            group = form.cleaned_data["group"]
            option = form.cleaned_data["option"]
            # ... your logic ...
            self.message_user(request, "Sync completed", messages.SUCCESS)
            return redirect(obj.admin_change_url)
        return {}  # Return additional context if needed
```

The decorator handles:
- Widget application (respects `raw_id_fields` and `autocomplete_fields`)
- Form validation on POST
- Adding the form to the template context
- Backward compatibility (if your view doesn't accept a `form` parameter, it won't be passed)

## Audit (created_by / updated_by)

1. Add `CurrentUserMiddleware` to `MIDDLEWARE` (after `AuthenticationMiddleware`):

```python
MIDDLEWARE = [
    ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    ...
    "django_boosted.middleware.CurrentUserMiddleware",
]
```

2. Use `AuditMixin` on your models:

```python
from django.db import models
from django_boosted import AuditMixin

class Article(AuditMixin, models.Model):
    title = models.CharField(max_length=200)
```

The mixin automatically sets `created_by` on first save and `updated_by` on each save when a user is authenticated.

`created_by` and `updated_by` use `AuditUserField`: auto-filled with configurable concatenation. Default: `('pk', 'username')` joined with `_`. Override `audit_user_format` and `audit_user_separator` on the model, or use the field directly:

```python
# Via mixin
class Article(AuditMixin, models.Model):
    audit_user_format = ("pk", "email")
    audit_user_separator = "-"

# Or use AuditUserField standalone
from django_boosted import AuditUserField

class Log(models.Model):
    editor = AuditUserField(format_fields=("pk", "username"), mode="updated")
```

**Settings**:
- `DJANGO_BOOSTED_AUDIT_USER_FALLBACK` — default value when no request user (migrations, commands, scripts). Example: `"robot_octolo"`. If not set, default is `None`.
- `DJANGO_BOOSTED_AUDIT_USER_FORMAT_FIELDS` — tuple of user attributes for the stored value. Default: `("pk", "username")`.
- `DJANGO_BOOSTED_AUDIT_USER_SEPARATOR` — separator between format fields. Default: `"_"`.

In templates or Python, `created_by` and `updated_by` return `AuditUserValue` (str subclass) with `admin_url`:

```python
obj.created_by  # "42-johndoe"
obj.created_by.admin_url  # "/admin/auth/user/42/change/"
```

## Development commands

Run everything via `./service.py dev <command>` or `python dev.py <command>`:

| Command | Description |
| --- | --- |
| `./service.py dev install-dev` or `python dev.py install-dev` | create the venv and install the package editable with `dev` extras. |
| `./service.py dev lint` or `python dev.py lint` | run Ruff + Black in check mode. |
| `./service.py dev format` or `python dev.py format` | apply Ruff --fix then Black. |
| `./service.py dev test` or `python dev.py test` | run `pytest` (with `pytest-django`). |
| `./service.py dev build` or `python dev.py build` | clean then build wheel + sdist. |
| `./service.py quality security` or `python dev.py security` | Bandit + Safety + pip-audit. |
| `./service.py dev help` or `python dev.py help` | list all commands. |

## License

MIT — see the `LICENSE` file. Contributions welcome!
