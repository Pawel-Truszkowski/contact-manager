from django.contrib import admin

from .models import Contact, ContactStatusChoices

@admin.register(ContactStatusChoices)
class ContactStatusChoicesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'city', 'status', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'city')
    list_filter = ('status', 'created_at', 'updated_at')
    ordering = ('-created_at',)
