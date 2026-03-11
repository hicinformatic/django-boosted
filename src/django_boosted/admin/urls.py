from django.contrib import admin


class UrlAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "url",
        "module",
        "app_label",
        "model",
        "namespace",
        "reverse_name",
        "lookup_str",
    ]
    search_fields = [
        "name",
        "url",
        "module",
        "app_label",
        "model",
        "namespace",
        "reverse_name",
        "lookup_str",
    ]
