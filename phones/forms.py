from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'payment_method', 'delivery_method', 'city_ref',  'warehouse_ref']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['full_name'].error_messages = {'required': 'Please enter your Full Name.'}
        self.fields['phone'].error_messages = {'required': 'Please enter your phone.'}
        self.fields['city_ref'].error_messages = {'required': 'Please select city.'}
        self.fields['warehouse_ref'].error_messages = {'required': 'Please select branch number.'}

