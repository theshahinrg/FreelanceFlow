from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from crm.models import Client, ContactLog, Invoice, Project


class ModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="alice", password="pass1234")
        self.client_obj = Client.objects.create(
            user=self.user,
            name="Acme Corp",
            email="contact@acme.com",
        )

    def test_client_str(self):
        self.assertEqual(str(self.client_obj), "Acme Corp")

    def test_invoice_str(self):
        project = Project.objects.create(
            user=self.user,
            client=self.client_obj,
            name="Website",
            amount=1000,
        )
        invoice = Invoice.objects.create(
            number="INV-001",
            project=project,
            amount=1000,
            payment_status=Invoice.PaymentStatus.PAID,
            issue_date=timezone.now().date(),
        )
        self.assertEqual(str(invoice), "Invoice INV-001")

    def test_project_requires_same_user_as_client(self):
        other_user = get_user_model().objects.create_user(username="bob", password="pass1234")
        project = Project(
            user=other_user,
            client=self.client_obj,
            name="Mismatched",
            amount=500,
        )
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_contact_log_validates_client_user(self):
        log = ContactLog(
            user=self.user,
            client=self.client_obj,
            contact_type=ContactLog.ContactType.EMAIL,
            notes="Checked in",
            contacted_at=timezone.now(),
        )
        log.full_clean()  # Should not raise

        other_user = get_user_model().objects.create_user(username="charlie", password="pass1234")
        bad_log = ContactLog(
            user=other_user,
            client=self.client_obj,
            contact_type=ContactLog.ContactType.EMAIL,
            notes="Bad log",
            contacted_at=timezone.now(),
        )
        with self.assertRaises(ValidationError):
            bad_log.full_clean()

    def test_unique_email_per_user(self):
        dup = Client(user=self.user, name="Dup", email="contact@acme.com")
        with self.assertRaises(ValidationError):
            dup.full_clean()


class ViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="alice", password="pass1234")
        self.other_user = User.objects.create_user(username="bob", password="pass1234")

        self.client_alice = Client.objects.create(
            user=self.user, name="Alice Client", email="alice@example.com"
        )
        self.client_bob = Client.objects.create(
            user=self.other_user, name="Bob Client", email="bob@example.com"
        )
        self.project_alice = Project.objects.create(
            user=self.user, client=self.client_alice, name="Site", amount=500
        )
        self.invoice_alice = Invoice.objects.create(
            number="INV-1",
            project=self.project_alice,
            amount=500,
            issue_date=timezone.now().date(),
        )
        self.invoice_bob = Invoice.objects.create(
            number="INV-2",
            project=Project.objects.create(
                user=self.other_user, client=self.client_bob, name="Other", amount=100
            ),
            amount=100,
            issue_date=timezone.now().date(),
        )

    def test_login_required_for_clients(self):
        response = self.client.get(reverse("client-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_client_list_shows_only_user_clients(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("client-list"))
        self.assertContains(response, self.client_alice.name)
        self.assertNotContains(response, self.client_bob.name)

    def test_client_search_filters_results(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("client-list"), {"q": "Alice"})
        self.assertContains(response, self.client_alice.name)
        response = self.client.get(reverse("client-list"), {"q": "Bob"})
        self.assertNotContains(response, self.client_alice.name)

    def test_client_detail_blocks_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse("client-detail", args=[self.client_alice.pk]))
        self.assertEqual(response.status_code, 404)

    def test_create_client_sets_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("client-create"),
            {"name": "New Co", "email": "new@example.com", "phone": "", "company": "", "notes": ""},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Client.objects.filter(user=self.user, name="New Co").exists())

    def test_project_create_with_owned_client(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("project-create"),
            {
                "name": "New Project",
                "description": "Desc",
                "status": Project.Status.PLANNED,
                "amount": 250,
                "start_date": "",
                "end_date": "",
                "client": self.client_alice.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name="New Project")
        self.assertEqual(project.user, self.user)
        self.assertEqual(project.client, self.client_alice)

    def test_invoice_list_only_user_projects(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("invoice-list"))
        self.assertContains(response, self.invoice_alice.number)
        self.assertNotContains(response, self.invoice_bob.number)
