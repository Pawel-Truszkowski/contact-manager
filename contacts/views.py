from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from .forms import ContactForm
from .models import Contact
from .services import get_weather

def contact_list(request):
    contacts = Contact.objects.select_related('status').all()
    
    q = request.GET.get('q', '')
    if q:
        contacts = contacts.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(city__icontains=q)
        )
    
    sort = request.GET.get('sort', '-created_at')
    allowed_sort_fields = ['last_name', '-last_name', 'created_at', '-created_at']
    if sort in allowed_sort_fields:
        contacts = contacts.order_by(sort)
    
    for contact in contacts:
        contact.weather = get_weather(contact.city)
        
    context = {
        'contacts': contacts,
        'q': q,
        'sort': sort,
    }
    
    return render(request, 'contacts/contact_list.html', context)


def contact_edit(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kontakt został zaktualizowany.')
            return redirect('contact_list')
    else:
        form = ContactForm(instance=contact)

    return render(request, 'contacts/contact_form.html', {'form': form, 'contact': contact})


def contact_delete(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)

    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Kontakt został usunięty.')
        return redirect('contact_list')

    return render(request, 'contacts/contact_confirm_delete.html', {'contact': contact})

def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kontakt został dodany.')
            return redirect('contact_list')
    else:
        form = ContactForm()
    return render(request, 'contacts/contact_form.html', {'form': form})
