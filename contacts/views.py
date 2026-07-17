from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from django.db.models import Q
from .models import Contact

def contact_list(request):
    contacts = Contact.objects.all()
    
    q = request.GET.get('q', '')
    if q:
        contacts = contacts.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(city__icontains=q)
        )
    
    sort = request.GET.get('sort', '')
    allowed_sort_fields = ['last_name', '-last_name', 'created_at', '-created_at']
    if sort in allowed_sort_fields:
        contacts = contacts.order_by(sort)
    
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