from django import forms
from .models import ContactUsTicket

class ContactUsTicketForm(forms.ModelForm):
    class Meta:
        model = ContactUsTicket
        fields = ['email', 'ticketType', 'description']
        labels = {
            'email': 'Email Address',
            'ticketType': 'Ticket Type',
            'description': 'Comments'
        }