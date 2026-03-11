## Development Guidelines

### General Rules

- Always execute project tooling through `./service.py dev <command>` or `python dev.py <command>`.
- Default to English for all code artifacts (comments, docstrings, logging, error strings, documentation snippets, etc.) regardless of the language used in discussions.
- Keep comments minimal and only when they clarify non-obvious logic.
- Avoid reiterating what the code already states clearly.
- Add comments only when they resolve likely ambiguity or uncertainty.

### Simplicity and Dependencies

- **Keep functions simple**: Always write the simplest possible functions. Avoid unnecessary complexity unless it's clearly evident or necessary.
- **Minimize dependencies**: Limit dependencies to the absolute minimum. Only add new dependencies when they provide essential functionality that cannot be reasonably implemented otherwise.
- **Prefer standard library**: Use Python standard library whenever possible before adding external dependencies.
- **Avoid over-engineering**: Don't add abstractions, patterns, or layers unless they solve a real problem or are clearly needed.

### Code Quality

- **Testing**: Use pytest with pytest-django for all tests. Place tests in `tests/` directory.
- **Type Hints**: All public functions and methods must have complete type hints.
- **Docstrings**: Use Google-style docstrings for all public classes, methods, and functions.
- **Linting**: Follow PEP 8 and use the configured linters (ruff, mypy, etc.).
- **Formatting**: Use the configured formatter (`ruff format`).

### Module Organization

- Keep related functionality grouped together in logical modules
- Maintain clear separation of concerns between modules
- Use `__init__.py` to define clean public APIs
- Avoid circular dependencies
- Follow Django app structure conventions

### Django-Specific Guidelines

- **Admin Integration**: All admin features must integrate seamlessly with Django's admin interface
- **Permissions**: Always check permissions before rendering views or performing actions
- **Templates**: Use Django's template system and follow admin template patterns
- **URLs**: Register URLs through Django admin's URL system
- **Models**: Use Django models appropriately, including virtual models when needed

### Qualitybase Integration

- **qualitybase is an installed package**: Always use standard Python imports from `qualitybase.services`
- **No path manipulation**: Never manipulate `sys.path` or use file paths to import qualitybase modules
- **Direct imports only**: Use `from qualitybase.services import ...` or `import qualitybase.services ...`
- **Standard library imports**: Use `importlib.import_module()` from the standard library if needed for dynamic imports
- **Works everywhere**: Since qualitybase is installed in the virtual environment, imports work consistently across all projects

### Configuration and Secrets

- Never hardcode API keys, credentials, or sensitive information
- Use environment variables or Django settings for configuration
- Provide clear documentation on required configuration

### Error Handling

- Always handle errors gracefully
- Provide clear, actionable error messages
- Use appropriate exception types
- Document exceptions in docstrings

### Versioning

- Follow semantic versioning (SemVer)
- Update version numbers appropriately for changes
- Document breaking changes clearly
