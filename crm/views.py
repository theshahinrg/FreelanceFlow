from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)

from .forms import ClientForm, ContactLogForm, InvoiceForm, ProjectForm
from .models import Client, ContactLog, Invoice, Project


class HomeRedirectView(LoginRequiredMixin, RedirectView):
    pattern_name = "client-list"


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "crm/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        queryset = Client.objects.filter(user=self.request.user).prefetch_related(
            "projects__invoices"
        )
        query = self.request.GET.get("q")
        email = self.request.GET.get("email")
        status = self.request.GET.get("status")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(company__icontains=query)
            )
        if email:
            queryset = queryset.filter(email__icontains=email)
        if status:
            queryset = queryset.filter(projects__status=status)
        return queryset.annotate(
            project_count=Count("projects", distinct=True),
            invoice_count=Count("projects__invoices", distinct=True),
        ).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Project.Status.choices
        context["query_params"] = {
            "q": self.request.GET.get("q", ""),
            "email": self.request.GET.get("email", ""),
            "status": self.request.GET.get("status", ""),
        }
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "crm/client_detail.html"
    context_object_name = "client"

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.object
        context["projects"] = client.projects.filter(user=self.request.user).prefetch_related(
            "invoices"
        )
        context["invoices"] = Invoice.objects.filter(
            project__client=client, project__user=self.request.user
        ).select_related("project")
        context["contact_logs"] = ContactLog.objects.filter(
            client=client, user=self.request.user
        ).select_related("project")
        context["contact_log_form"] = ContactLogForm(
            user=self.request.user, initial={"client": client}
        )
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "crm/client_form.html"
    success_url = reverse_lazy("client-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Client created.")
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "crm/client_form.html"

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse("client-detail", args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, "Client updated.")
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "crm/client_confirm_delete.html"
    success_url = reverse_lazy("client-list")

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Client deleted.")
        return super().delete(request, *args, **kwargs)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "crm/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        queryset = Project.objects.filter(user=self.request.user).select_related("client")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Project.Status.choices
        context["selected_status"] = self.request.GET.get("status", "")
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "crm/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).select_related("client")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invoices"] = self.object.invoices.all()
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "crm/project_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        if "client" in self.request.GET:
            kwargs.setdefault("initial", {})["client"] = self.request.GET.get("client")
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Project created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project-detail", args=[self.object.pk])


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "crm/project_form.html"

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Project updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("project-detail", args=[self.object.pk])


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "crm/project_confirm_delete.html"
    success_url = reverse_lazy("project-list")

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Project deleted.")
        return super().delete(request, *args, **kwargs)


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "crm/invoice_list.html"
    context_object_name = "invoices"

    def get_queryset(self):
        queryset = Invoice.objects.filter(project__user=self.request.user).select_related(
            "project", "project__client"
        )
        status = self.request.GET.get("payment_status")
        if status:
            queryset = queryset.filter(payment_status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payment_statuses"] = Invoice.PaymentStatus.choices
        context["selected_status"] = self.request.GET.get("payment_status", "")
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "crm/invoice_detail.html"
    context_object_name = "invoice"

    def get_queryset(self):
        return Invoice.objects.filter(project__user=self.request.user).select_related(
            "project", "project__client"
        )


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "crm/invoice_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        if "project" in self.request.GET:
            kwargs.setdefault("initial", {})["project"] = self.request.GET.get("project")
        return kwargs

    def form_valid(self, form):
        project = form.cleaned_data.get("project")
        if project.user != self.request.user:
            messages.error(self.request, "You cannot create invoices for this project.")
            form.add_error("project", "Select one of your projects.")
            return self.form_invalid(form)
        messages.success(self.request, "Invoice created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("invoice-detail", args=[self.object.pk])


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "crm/invoice_form.html"

    def get_queryset(self):
        return Invoice.objects.filter(project__user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        project = form.cleaned_data.get("project")
        if project.user != self.request.user:
            messages.error(self.request, "You cannot move invoices to another user's project.")
            form.add_error("project", "Select one of your projects.")
            return self.form_invalid(form)
        messages.success(self.request, "Invoice updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("invoice-detail", args=[self.object.pk])


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = "crm/invoice_confirm_delete.html"
    success_url = reverse_lazy("invoice-list")

    def get_queryset(self):
        return Invoice.objects.filter(project__user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Invoice deleted.")
        return super().delete(request, *args, **kwargs)


class ContactLogCreateView(LoginRequiredMixin, CreateView):
    model = ContactLog
    form_class = ContactLogForm
    template_name = "crm/contactlog_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        initial = kwargs.get("initial", {})
        client_id = self.kwargs.get("client_pk")
        project_id = self.request.GET.get("project")
        if client_id:
            initial["client"] = client_id
        if project_id:
            initial["project"] = project_id
        kwargs["initial"] = initial
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        client = form.cleaned_data.get("client")
        if client.user != self.request.user:
            form.add_error("client", "Select one of your clients.")
            return self.form_invalid(form)
        project = form.cleaned_data.get("project")
        if project and project.user != self.request.user:
            form.add_error("project", "Select one of your projects.")
            return self.form_invalid(form)
        messages.success(self.request, "Contact log added.")
        return super().form_valid(form)

    def get_success_url(self):
        client_id = self.object.client.pk
        return reverse("client-detail", args=[client_id])
