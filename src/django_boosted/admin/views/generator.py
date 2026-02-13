"""Complete view generator combining all mixins."""

from .adminform import AdminFormViewMixin
from .base import ViewGenerator as BaseViewGenerator
from .confirm import ConfirmViewMixin
from .form import FormViewMixin
from .json import JsonViewMixin
from .list import ListViewMixin
from .message import MessageViewMixin


class ViewGenerator(
    ListViewMixin,
    FormViewMixin,
    MessageViewMixin,
    ConfirmViewMixin,
    JsonViewMixin,
    AdminFormViewMixin,
    BaseViewGenerator,
):
    """Complete view generator with all view types."""
