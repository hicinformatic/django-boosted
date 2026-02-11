from django.contrib import admin
from django.urls import reverse

from django_boosted import AdminBoostModel, admin_boost_view

from ..forms import AlphabetForm, CountryForm
from ..models import Country


class CountryAdmin(AdminBoostModel):
    search_fields = ["name"]
    list_display = [
        "name",
        "label_link_success_small",
        "label_link_info_small",
        "label_link_warning_default",
        "label_link_danger_default",
        "label_link_primary_big",
        "label_link_secondary_big",
        "label_link_default_big",
    ]

    @admin.display(description="Success Small")
    def label_link_success_small(self, obj):
        return self.format_label("Success", "success", size="small")

    @admin.display(description="Info Small")
    def label_link_info_small(self, obj):
        return self.format_label(
            "Message",
            "info",
            size="small",
            link=reverse(
                "admin:tests_app_country_custom_message_object_view", args=[obj.pk]
            ),
        )

    @admin.display(description="Warning Default")
    def label_link_warning_default(self, obj):
        return self.format_label(
            "Json",
            "warning",
            link=reverse(
                "admin:tests_app_country_custom_json_object_view", args=[obj.pk]
            ),
        )

    @admin.display(description="Danger Default")
    def label_link_danger_default(self, obj):
        return self.format_label(
            "List",
            "danger",
            link=reverse(
                "admin:tests_app_country_custom_list_object_view", args=[obj.pk]
            ),
        )

    @admin.display(description="Primary Big")
    def label_link_primary_big(self, obj):
        return self.format_label(
            "Form",
            "primary",
            size="big",
            link=reverse(
                "admin:tests_app_country_custom_form_object_view", args=[obj.pk]
            ),
        )

    @admin.display(description="Secondary Big")
    def label_link_secondary_big(self, obj):
        return self.format_label("Secondary", "secondary", size="big")

    @admin.display(description="Default Big")
    def label_link_default_big(self, obj):
        return self.format_label("Default", "default", size="big")

    @admin_boost_view("message", "Custom Message View")
    def custom_message_view(self, request):
        return {"message": "This is a custom message view"}

    @admin_boost_view("json", "Custom JSON View")
    def custom_json_view(self, request):
        return {
            "json_custom": [
                {"name": "Custom 1", "id": 1},
                {"name": "Custom 2", "id": 2},
                {"name": "Custom 3", "id": 3},
            ]
        }

    @admin_boost_view("list", "Custom List View")
    def custom_list_view(self, request):
        queryset = Country.objects.all()
        return {
            "queryset": queryset,
            "list_display": ["name"],
            "search_fields": ["name"],
        }

    @admin_boost_view("form", "Custom Form View")
    def custom_form_view(self, request):
        return {"form": CountryForm()}

    @admin_boost_view("json", "Custom Json Object View")
    def custom_json_object_view(self, request, obj):
        return {"object_json": {"name": "Custom 1", "id": 1}}

    @admin_boost_view("message", "Custom Message Object View")
    def custom_message_object_view(self, request, obj):
        return {"message": f"This is a custom message object view for {obj}"}

    @admin_boost_view("list", "Custom List Object View")
    def custom_list_object_view(self, request, obj):
        queryset = Country.objects.filter(name__icontains="a")
        return {
            "queryset": queryset,
            "list_display": ["name"],
            "search_fields": ["name"],
        }

    @admin_boost_view("form", "Custom Form Object View")
    def custom_form_object_view(self, request, obj):
        return {"form": AlphabetForm()}

