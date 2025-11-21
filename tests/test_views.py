import secrets

import pytest
from django.contrib.admin.widgets import AutocompleteSelect, ForeignKeyRawIdWidget
from django.contrib.auth import get_user_model
from django.test import Client as DjangoClient
from django.urls import reverse

from tests.app.models import Client, Company


@pytest.fixture()
def superuser(db):
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password=secrets.token_urlsafe(16),
    )


@pytest.fixture()
def admin_client(superuser):
    client = DjangoClient()
    client.force_login(superuser)
    return client


@pytest.mark.django_db()
def test_boost_view_renders_context(admin_client):
    client_obj = Client.objects.create(name="Alice")
    url = reverse("admin:tests_app_client_hello_view", args=[client_obj.pk])

    response = admin_client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Hello Alice" in content
    assert "Back to change form" in content


@pytest.mark.django_db()
def test_object_tools_button_is_visible(admin_client):
    client_obj = Client.objects.create(name="Bob")
    change_url = reverse("admin:tests_app_client_change", args=[client_obj.pk])

    response = admin_client.get(change_url)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Say hello" in content


@pytest.mark.django_db()
def test_raw_id_widget_is_applied(admin_client):
    """Test that ForeignKeyRawIdWidget is applied when raw_id_fields is used."""
    from django.contrib import admin

    from tests.app.admin import ClientAdmin

    client_obj = Client.objects.create(name="Alice")
    Company.objects.create(name="Test Company", owner=client_obj)

    # Get the admin instance and check the form class
    admin_instance = ClientAdmin(Client, admin.site)
    form_class = admin_instance.RawIdForm

    # Apply widgets (this is done by the decorator)
    from django_admin_boost.decorators import _apply_admin_widgets_to_form

    _apply_admin_widgets_to_form(form_class, admin_instance, raw_id_fields=["company"])

    # Check the widget type
    assert hasattr(form_class.base_fields["company"], "widget")
    assert isinstance(form_class.base_fields["company"].widget, ForeignKeyRawIdWidget)


@pytest.mark.django_db()
def test_autocomplete_widget_is_applied(admin_client):
    """Test that AutocompleteSelect is applied when autocomplete_fields is used."""
    from tests.app.admin import ClientAdmin

    client_obj = Client.objects.create(name="Bob")
    Company.objects.create(name="Test Company", owner=client_obj)

    # Get the admin instance and check the form class
    from django.contrib import admin

    admin_instance = ClientAdmin(Client, admin.site)
    form_class = admin_instance.AutocompleteForm

    # Apply widgets (this is done by the decorator)
    from django_admin_boost.decorators import _apply_admin_widgets_to_form

    _apply_admin_widgets_to_form(
        form_class, admin_instance, autocomplete_fields=["company"]
    )

    # Check the widget type
    assert hasattr(form_class.base_fields["company"], "widget")
    assert isinstance(form_class.base_fields["company"].widget, AutocompleteSelect)
