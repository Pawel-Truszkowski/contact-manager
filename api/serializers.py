from rest_framework import serializers
from contacts.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id", "first_name", "last_name", "email",
            "phone_number", "city", "status", "status_name", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
