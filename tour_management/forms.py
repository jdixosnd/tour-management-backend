from django import forms
from django.contrib.auth.hashers import make_password
from .models import Cardealer, User


class CarDealerForm(forms.ModelForm):
    class Meta:
        model = Cardealer
        fields = ['tour_operator', 'location', 'created_by', 'name', 'contact_no']


class UserCreationForm(forms.ModelForm):
    """Form for creating new users with plain text password."""
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text='Enter the password for this user.'
    )
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        help_text='Enter the same password again for verification.'
    )

    class Meta:
        model = User
        fields = ('tour_operator_id', 'name', 'email', 'role', 'is_active', 'mobileno', 'username')

    def clean_password_confirm(self):
        """Validate that the two password entries match."""
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return password_confirm

    def save(self, commit=True):
        """Save the user with hashed password."""
        user = super().save(commit=False)
        user.password_hash = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Form for updating users. Password field is optional."""
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=False,
        help_text='Leave blank if you don\'t want to change the password.'
    )

    class Meta:
        model = User
        fields = ('tour_operator_id', 'name', 'email', 'role', 'is_active', 'mobileno', 'username')

    def save(self, commit=True):
        """Save the user, hashing the password if it was changed."""
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.password_hash = make_password(password)
        if commit:
            user.save()
        return user