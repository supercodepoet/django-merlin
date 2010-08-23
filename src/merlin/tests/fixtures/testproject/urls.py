from django.conf.urls.defaults import *

from merlin.wizards.utils import Step
from merlin.wizards.session import SessionWizard

from merlin.tests.fixtures.testproject import forms

urlpatterns = patterns('',
    url(r'^simpletest/(?P<slug>[A-Za-z0-9_-]+)$', SessionWizard([
        Step('user-details', forms.UserDetailsForm),
        Step('contact-details', forms.ContactDetailsForm)]), name="simpletest"),
)
