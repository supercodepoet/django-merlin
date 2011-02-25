from django.conf.urls.defaults import *

from merlin.tests.fixtures.testproject.wizard import MockWizard
from merlin.wizards.utils import Step
from merlin.wizards.session import SessionWizard

from merlin.tests.fixtures.testproject import forms
from merlin.tests.fixtures.testproject import views

urlpatterns = patterns('',
    url(r'^simpletest$', SessionWizard([
        Step('user-details', forms.UserDetailsForm),
        Step('contact-details', forms.ContactDetailsForm)])),
    url(r'^simpletest/(?P<slug>[A-Za-z0-9_-]+)$', SessionWizard([
        Step('user-details', forms.UserDetailsForm),
        Step('contact-details', forms.ContactDetailsForm)])),
    url(r'^bettertest/(?P<slug>[A-Za-z0-9_-]+)$', MockWizard([
        Step('user-details', forms.UserDetailsForm),
        Step('contact-details', forms.ContactDetailsForm)])),
    url(r'^$', views.index, name='test-index'),
    url(r'^more$', views.more, name='test-more'),
)
