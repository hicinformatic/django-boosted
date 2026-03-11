## Project Purpose

**Django Boosted** is a lightweight Django library that extends Django's admin interface with extra views, custom forms, and matching UI affordances (object tools, permissions, standard responses).

### Core Functionality

The library provides:

1. **Admin View Extensions**:
   - Custom views for Django admin (list views, form views, message views, JSON views)
   - Automatic permission checking
   - Context building with standard admin variables
   - URL registration and protection via `admin_site.admin_view`

2. **Decorators**:
   - `@admin_boost_view` decorator for defining custom admin views
   - Automatic object fetching and permission checking
   - Template rendering with proper context

3. **Admin Mixins**:
   - `AdminBoostMixin` for registering custom URLs
   - Automatic injection of object-tool buttons into change forms
   - Integration with Django admin's permission system

4. **Templates**:
   - Reusable admin templates for custom views
   - Change form template with object tools support
   - Message and form templates

5. **DRF Integration**:
   - Custom metadata class for Django Rest Framework
   - Support for `extra_metadata` on DRF fields
   - Conditional import when DRF is installed

### Architecture

The library uses a service-based architecture:

- View generation is handled by `ViewGenerator` class
- Decorators provide a simple interface for defining views
- Mixins integrate with Django admin's existing infrastructure
- Templates follow Django admin's design patterns

### Use Cases

- Adding custom actions to Django admin change forms
- Creating custom admin views with proper permissions
- Extending admin interface with additional functionality
- Building admin tools that integrate seamlessly with Django admin
- Customizing DRF metadata for admin-related fields
