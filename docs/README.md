## Assistant Guidelines

This file provides general guidelines for the AI assistant working on this project.

For detailed information, refer to:
- `AI.md` - Condensed reference guide for AI assistants (start here)
- `purpose.md` - Project purpose and goals
- `structure.md` - Project structure and module organization
- `development.md` - Development guidelines and best practices

### Quick Reference

- Always use `./service.py dev <command>` or `python dev.py <command>` for project tooling
- Always use `./service.py quality <command>` or `python quality.py <command>` for quality checks
- Maintain clean module organization and separation of concerns
- Default to English for all code artifacts (comments, docstrings, logging, error strings, documentation snippets, etc.)
- Follow Python best practices and quality standards
- Keep dependencies minimal and prefer standard library
- Ensure all public APIs have type hints and docstrings
- Write tests for new functionality

### Django Boosted-Specific Guidelines

- **Admin integration**: All admin features must work seamlessly with Django's admin interface
- **View generation**: Use `ViewGenerator` class for creating admin custom views
- **Decorators**: Use `@admin_boost_view` decorator for defining custom admin views
- **Templates**: Provide reusable templates in `templates/admin_boost/`
- **Permissions**: Always check permissions before rendering views
- **DRF integration**: Support Django Rest Framework metadata customization when DRF is installed

### View Implementation Checklist

When creating a new admin view:
- [ ] Use `ViewGenerator` methods for view creation
- [ ] Check permissions appropriately
- [ ] Provide proper context for templates
- [ ] Handle both object and list views correctly
- [ ] Use appropriate decorators
- [ ] Add tests for the view
