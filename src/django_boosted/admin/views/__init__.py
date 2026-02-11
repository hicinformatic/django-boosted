"""View generation utilities for django-boosted."""

from .base import ViewConfig
from .generator import ViewGenerator
from .setup import setup_boost_views

__all__ = ["ViewConfig", "ViewGenerator", "setup_boost_views"]
