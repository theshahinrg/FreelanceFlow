from django import forms

from .models import Client, ContactLog, Invoice, Project


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "phone", "company", "notes"]


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "status",
            "amount",
            "start_date",
            "end_date",
            "client",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["client"].queryset = Client.objects.filter(user=user)


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "number",
            "project",
            "amount",
            "payment_status",
            "issue_date",
            "due_date",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["project"].queryset = Project.objects.filter(user=user)


class ContactLogForm(forms.ModelForm):
    class Meta:
        model = ContactLog
        fields = ["client", "project", "contact_type", "notes", "contacted_at"]
        widgets = {
            "contacted_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["client"].queryset = Client.objects.filter(user=user)
            self.fields["project"].queryset = Project.objects.filter(user=user)
