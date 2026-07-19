from rest_framework import viewsets
from contacts.models import Contact
from .serializers import ContactSerializer


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.select_related('status').all()
    serializer_class = ContactSerializer
