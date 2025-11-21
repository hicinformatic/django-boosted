from django import forms
from django.contrib import admin

from django_admin_boost.decorators import admin_boost_object_view
from django_admin_boost.mixins import AdminBoostMixin

from .models import Client, Company


class ClientAdmin(AdminBoostMixin, admin.ModelAdmin):
    boost_views = ["hello_view", "raw_id_form_view", "autocomplete_form_view"]
    change_form_template = "admin_boost/change_form.html"
    search_fields = ["name"]  # Required for autocomplete_fields

    @admin_boost_object_view(
        label="Say hello",
        template_name="admin_boost/hello.html",
    )
    def hello_view(self, request, obj):
        return {"message": f"Hello {obj}!"}

    class RawIdForm(forms.Form):
        company = forms.ModelChoiceField(queryset=Company.objects.all())

    @admin_boost_object_view(
        label="Raw ID Form",
        template_name="admin_boost/form_view.html",
        form=RawIdForm,
        raw_id_fields=["company"],
    )
    def raw_id_form_view(self, request, obj, form):
        if request.method == "POST" and form.is_valid():
            company = form.cleaned_data["company"]
            return {"message": f"Selected company: {company}"}
        return {}

    class AutocompleteForm(forms.Form):
        company = forms.ModelChoiceField(queryset=Company.objects.all())

    @admin_boost_object_view(
        label="Autocomplete Form",
        template_name="admin_boost/form_view.html",
        form=AutocompleteForm,
        autocomplete_fields=["company"],
    )
    def autocomplete_form_view(self, request, obj, form):
        if request.method == "POST" and form.is_valid():
            company = form.cleaned_data["company"]
            return {"message": f"Selected company: {company}"}
        return {}


class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "owner"]
    search_fields = ["name", "owner__name"]
    autocomplete_fields = ["owner"]


admin.site.register(Client, ClientAdmin)
admin.site.register(Company, CompanyAdmin)
