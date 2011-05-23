from django import forms
from django.forms import formsets

class UserDetailsForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

UserDetailsFormSet = formsets.formset_factory(UserDetailsForm)

class ContactDetailsForm(forms.Form):
    street_address = forms.CharField()
    city  = forms.CharField()
    state = forms.CharField()
    zipcode = forms.CharField()
    phone = forms.CharField()


class FewMoreThingsForm(forms.Form):
    bio = forms.CharField()


class SocialForm(forms.Form):
    twitter = forms.URLField()
    facebook = forms.URLField()
