from django import forms
from .models import Cardealer
class CarDealerForm(forms.ModelForm):
    class Meta:
        model = Cardealer
        fields = ['tour_operator', 'location', 'created_by', 'name', 'contact_no']