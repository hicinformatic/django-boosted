import secrets

import pytest
from django.contrib.auth import get_user_model
from django.test import Client as DjangoClient
from django.urls import reverse

from tests.app.models import Country


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
    country_obj = Country.objects.create(name="Alice")
    url = reverse("admin:tests_app_country_hello_view", args=[country_obj.pk])

    response = admin_client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Hello Alice" in content
    assert "Back to change form" in content


@pytest.mark.django_db()
def test_object_tools_button_is_visible(admin_client):
    country_obj = Country.objects.create(name="Bob")
    change_url = reverse("admin:tests_app_country_change", args=[country_obj.pk])

    response = admin_client.get(change_url)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Say hello" in content
