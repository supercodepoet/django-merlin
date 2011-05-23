from django import forms
from django.forms import formsets
from django.forms.util import ErrorList

class UserDetailsForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

UserDetailsFormSet = formsets.formset_factory(UserDetailsForm)

class UserDetailsFormSet(formsets.BaseFormSet):

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, form=UserDetailsForm,
                 extra= 1, can_order=False,
                 can_delete=False, max_num=10):

        self.form = form
        self.extra = extra
        self.can_order = can_order
        self.can_delete = can_delete
        self.max_num = max_num

        super(UserDetailsFormSet, self).__init__(data=data, files=files,
                                                auto_id=auto_id, prefix=prefix,
                                                initial=initial,
                                                error_class=error_class)


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
