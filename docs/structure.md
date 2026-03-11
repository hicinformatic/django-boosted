## Project Structure

Django Boosted follows a standard Django app structure with clear separation between admin utilities, models, managers, and templates.

### General Structure

```
django-boosted/
├── src/
│   └── django_boosted/       # Main package directory
│       ├── __init__.py       # Package exports
│       ├── admin/            # Admin utilities
│       │   ├── __init__.py   # Admin exports
│       │   ├── model.py      # AdminBoostMixin and AdminBoostModel
│       │   ├── views.py      # ViewGenerator class
│       │   ├── views_setup.py # View setup logic
│       │   ├── decorators.py # @admin_boost_view decorator
│       │   ├── fieldsets.py # Fieldset utilities
│       │   ├── format.py    # Formatting utilities
│       │   ├── tools.py     # Admin tools
│       │   └── urls.py      # URL registration
│       ├── models/           # Django models
│       │   └── urls.py      # URL model
│       ├── managers/         # Custom managers
│       │   └── urls.py      # URL manager
│       ├── rest_framework/  # DRF integration
│       │   ├── __init__.py  # Conditional DRF imports
│       │   └── metadata.py  # Custom metadata class
│       ├── templatetags/    # Template tags
│       │   └── boosted_tags.py
│       ├── templates/       # Django templates
│       │   └── admin_boost/
│       ├── static/          # Static files
│       │   └── admin_boost/
│       ├── apps.py          # App configuration
│       └── decorators.py    # Main decorators module
├── tests/                    # Test suite
│   └── ...
├── docs/                     # Documentation
│   └── ...
├── service.py                # Main service entry point
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

### Module Organization Principles

- **Single Responsibility**: Each module should have a clear, single purpose
- **Separation of Concerns**: Keep admin, models, managers, and templates separate
- **Django Conventions**: Follow Django's app structure conventions
- **Clear Exports**: Use `__init__.py` to define public API
- **Logical Grouping**: Organize related functionality together

### Admin Organization

The `admin/` directory contains Django admin utilities:

- **`model.py`**: `AdminBoostMixin` and `AdminBoostModel` classes
- **`views.py`**: `ViewGenerator` class for creating admin views
- **`views_setup.py`**: Logic for setting up views from decorators
- **`decorators.py`**: `@admin_boost_view` decorator (re-exported from main decorators module)
- **`urls.py`**: URL registration utilities
- **`fieldsets.py`**: Fieldset manipulation utilities
- **`format.py`**: Formatting utilities for admin
- **`tools.py`**: Admin tool utilities

### Package Exports

The public API is defined in `src/django_boosted/__init__.py`:
- `AdminBoostModel`: Main admin model mixin
- `admin_boost_view`: Decorator for defining custom views
- Conditional DRF exports when DRF is installed
