
from django.contrib import admin
from django.urls import reverse

from django_boosted import AdminBoostModel, admin_boost_view


class AlphabetAdmin(AdminBoostModel):
    list_display = [
        "name",
        "country",
        "status_example_1",
        "status_example_2",
        "status_example_3",
        "status_example_4",
    ]
    search_fields = ["name", "country__name"]
    autocomplete_fields = ["country"]

    @admin.display(description="Status Example 1")
    def status_example_1(self, obj):
        return self.format_status("django", True)

    @admin.display(description="Status Example 2")
    def status_example_2(self, obj):
        return self.format_status("pytest", False)

    @admin.display(description="Status Example 3")
    def status_example_3(self, obj):
        return self.format_status(
            "django-rest-framework",
            True,
            link=reverse(
                "admin:tests_app_alphabet_custom_message_status_object_view",
                args=[obj.pk],
            ),
        )

    @admin.display(description="Status Example 2")
    def status_example_4(self, obj):
        return self.format_status(
            "django-channels",
            False,
            link=reverse(
                "admin:tests_app_alphabet_custom_message_status_object_view",
                args=[obj.pk],
            ),
        )

    @admin_boost_view("message", "Custom Message View")
    def custom_message_status_object_view(self, request, obj):
        return {"message": "This is a custom message view"}
