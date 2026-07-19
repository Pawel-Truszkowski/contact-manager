from django.test import TestCase
from django.db import IntegrityError
from rest_framework.test import APITestCase
from rest_framework import status as http_status

from .models import Contact, ContactStatusChoices
from .services import import_contacts_from_rows


def create_status(name="nowy"):
    return ContactStatusChoices.objects.create(name=name)


def contact_data(**overrides):
    """Base valid contact payload; override any field per test."""
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "email": "jan@example.com",
        "phone_number": "601234567",
        "city": "Wroclaw",
    }
    data.update(overrides)
    return data


class ContactModelTests(TestCase):
    def setUp(self):
        self.status = create_status()

    def test_duplicate_email_is_rejected(self):
        """Email uniqueness is enforced at the database level."""
        Contact.objects.create(status=self.status, **contact_data())
        with self.assertRaises(IntegrityError):
            Contact.objects.create(
                status=self.status,
                **contact_data(phone_number="609999999"),  # same email, new phone
            )


class CsvImportTests(TestCase):
    def setUp(self):
        create_status("nowy")

    def test_valid_rows_are_imported_and_broken_rows_are_skipped(self):
        rows = [
            # valid row
            {**contact_data(), "status": "nowy"},
            # invalid: unknown status
            {**contact_data(email="a@example.com", phone_number="602000000"),
             "status": "vip"},
            # invalid: duplicate email of the first row
            {**contact_data(phone_number="603000000"), "status": "nowy"},
        ]
        imported, error_lines = import_contacts_from_rows(rows)

        self.assertEqual(imported, 1)
        self.assertEqual(len(error_lines), 2)
        self.assertEqual(Contact.objects.count(), 1)


class ContactApiTests(APITestCase):
    def setUp(self):
        self.status = create_status()

    def test_post_creates_contact(self):
        payload = {**contact_data(), "status": self.status.pk}
        response = self.client.post("/api/contacts/", payload, format="json")

        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(response.data["status_name"], "nowy")
    