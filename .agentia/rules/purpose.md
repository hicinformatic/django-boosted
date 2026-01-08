## Project Purpose

**django-admin-boost** is a lightweight Django library that provides helpers to extend Django's admin interface with extra views, custom forms, and matching UI affordances (object tools, permissions, standard responses).

### Core Functionality

The library enables you to:

1. **Extend Django admin with custom views**:
   - Use the `@admin_boost_object_view` decorator to create custom admin views
   - Automatically fetch target objects and check permissions
   - Build default context before rendering templates
   - Register custom URLs with proper admin protection

2. **Add custom forms to admin views**:
   - Automatically apply admin widgets (`ForeignKeyRawIdWidget` or `AutocompleteSelect`)
   - Respect `raw_id_fields` and `autocomplete_fields` settings
   - Handle form validation on POST requests
   - Add forms to template context automatically

3. **Enhance admin UI with object tools**:
   - Inject extra object-tool buttons into change forms
   - Use `AdminBoostMixin` to register custom URLs
   - Protect views with `admin_site.admin_view`
   - Provide additional templates for change forms and list views

### Architecture

The library uses a mixin-based approach:

- `AdminBoostModel` (or `AdminBoostMixin`) extends Django's `ModelAdmin`
- Decorators mark methods as admin views with configuration
- View generator creates proper admin views with permissions and context
- Templates provide UI components for object tools and custom views

### Use Cases

- Adding custom actions to Django admin change forms
- Creating custom views for specific admin operations
- Extending admin with additional functionality beyond standard CRUD
- Building admin interfaces with custom workflows
- Adding object-specific tools and buttons to admin pages
