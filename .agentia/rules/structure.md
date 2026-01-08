## Project Structure

django-admin-boost follows a standard Python package structure with Django admin extensions.

### General Structure

```
django-admin-boost/
├── src/
│   └── django_admin_boost/    # Main package directory
│       ├── __init__.py         # Package exports (AdminBoostModel, admin_boost_view)
│       ├── admin/              # Admin module
│       │   ├── __init__.py     # Admin exports
│       │   ├── model.py        # AdminBoostModel class
│       │   ├── views_setup.py  # View setup functions
│       │   ├── tools.py        # Object tools functions
│       │   ├── fieldsets.py    # Fieldset utilities
│       │   └── format.py      # Formatting utilities
│       ├── decorators.py       # Decorator functions (admin_boost_view)
│       ├── static/             # Static files (CSS)
│       │   └── admin_boost/    # Admin boost CSS
│       └── templates/          # Django templates
│           └── admin_boost/    # Admin boost templates
├── tests/                      # Test suite
│   └── ...
├── docs/                       # Documentation
│   └── ...
├── service.py                  # Main service entry point script
├── pyproject.toml             # Project configuration
└── README.md                   # Project documentation
```

### Module Organization Principles

- **Single Responsibility**: Each module should have a clear, single purpose
- **Separation of Concerns**: Keep different concerns in separate modules
- **Django Admin Integration**: Extends Django's ModelAdmin with custom views and tools
- **Clear Exports**: Use `__init__.py` to define public API
- **Logical Grouping**: Organize related functionality together

### Admin Module Organization

The `admin/` directory contains Django admin extensions:

- **`model.py`**: Defines `AdminBoostModel` class that extends `ModelAdmin`
- **`views_setup.py`**: Functions for setting up custom admin views
- **`tools.py`**: Functions for generating object tools and list tools
- **`fieldsets.py`**: Utilities for managing fieldsets
- **`format.py`**: Formatting utilities for labels, status, etc.

### Decorators

The `decorators.py` module provides:

- **`admin_boost_view`**: Decorator for marking methods as admin views with configuration

### Templates and Static Files

- **`templates/admin_boost/`**: Django templates for change forms and list views
- **`static/admin_boost/`**: CSS files for admin boost styling

### Package Exports

The public API is defined in `src/django_admin_boost/__init__.py`:
- `AdminBoostModel`: Main ModelAdmin class with boost functionality
- `admin_boost_view`: Decorator for creating custom admin views

### Key Components

- **AdminBoostModel**: Extends Django's ModelAdmin with custom view support
- **Decorators**: Mark methods as admin views with automatic URL registration
- **View Generator**: Creates proper admin views with permissions and context
- **Templates**: Provide UI components for object tools and custom views