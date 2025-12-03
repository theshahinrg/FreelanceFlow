from django.conf import settings
from django.contrib import admin

from .models import Client, ContactLog, Invoice, Project


admin.site.site_header = f"Freelancer CRM — {settings.PROJECT_AUTHOR}"
admin.site.site_title = f"Freelancer CRM | {settings.PROJECT_AUTHOR}"
admin.site.index_title = f"Created by {settings.PROJECT_AUTHOR} — {settings.PROJECT_SITE_URL}"


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "company", "user")
    search_fields = ("name", "email", "company", "phone")
    list_filter = ("user",)
    readonly_fields = ("created_at",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "status", "amount", "start_date", "end_date", "user")
    list_filter = ("status", "user")
    search_fields = ("name", "client__name")
    readonly_fields = ("created_at",)
    list_select_related = ("client",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "project", "amount", "payment_status", "issue_date", "due_date")
    list_filter = ("payment_status",)
    search_fields = ("number", "project__name", "project__client__name")
    list_select_related = ("project", "project__client")
    readonly_fields = ("created_at",)


@admin.register(ContactLog)
class ContactLogAdmin(admin.ModelAdmin):
    list_display = ("client", "project", "contact_type", "contacted_at", "user")
    list_filter = ("contact_type", "user")
    search_fields = ("client__name", "project__name", "notes")
    date_hierarchy = "contacted_at"
    list_select_related = ("client", "project")
