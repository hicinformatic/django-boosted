"""Complete view generator combining all mixins."""

from .adminform import AdminFormViewMixin
from .base import ViewGenerator as BaseViewGenerator
from .confirm import ConfirmViewMixin
from .form import FormViewMixin
from .json import JsonViewMixin
from .list import ListViewMixin
from .message import MessageViewMixin
from .redirect import RedirectViewMixin


class ViewGenerator(
    ListViewMixin,
    FormViewMixin,
    MessageViewMixin,
    RedirectViewMixin,
    ConfirmViewMixin,
    JsonViewMixin,
    AdminFormViewMixin,
    BaseViewGenerator,
):
    """Complete view generator with all view types."""
