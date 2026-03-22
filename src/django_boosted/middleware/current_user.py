"""Thread-local storage for the current request user."""

import threading

_user = threading.local()


def get_current_user():
    """Return the current request user, or None if outside a request or not authenticated."""
    return getattr(_user, "value", None)


class CurrentUserMiddleware:
    """Middleware that stores the current request user in thread-local storage."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user
        try:
            return self.get_response(request)
        finally:
            _user.value = None
