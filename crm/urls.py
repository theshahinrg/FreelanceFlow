from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeRedirectView.as_view(), name="home"),
    path("clients/", views.ClientListView.as_view(), name="client-list"),
    path("clients/create/", views.ClientCreateView.as_view(), name="client-create"),
    path("clients/<int:pk>/", views.ClientDetailView.as_view(), name="client-detail"),
    path("clients/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client-update"),
    path("clients/<int:pk>/delete/", views.ClientDeleteView.as_view(), name="client-delete"),
    path(
        "clients/<int:client_pk>/logs/add/",
        views.ContactLogCreateView.as_view(),
        name="contactlog-create",
    ),
    path("projects/", views.ProjectListView.as_view(), name="project-list"),
    path("projects/create/", views.ProjectCreateView.as_view(), name="project-create"),
    path("projects/<int:pk>/", views.ProjectDetailView.as_view(), name="project-detail"),
    path("projects/<int:pk>/edit/", views.ProjectUpdateView.as_view(), name="project-update"),
    path("projects/<int:pk>/delete/", views.ProjectDeleteView.as_view(), name="project-delete"),
    path("invoices/", views.InvoiceListView.as_view(), name="invoice-list"),
    path("invoices/create/", views.InvoiceCreateView.as_view(), name="invoice-create"),
    path("invoices/<int:pk>/", views.InvoiceDetailView.as_view(), name="invoice-detail"),
    path("invoices/<int:pk>/edit/", views.InvoiceUpdateView.as_view(), name="invoice-update"),
    path("invoices/<int:pk>/delete/", views.InvoiceDeleteView.as_view(), name="invoice-delete"),
]
