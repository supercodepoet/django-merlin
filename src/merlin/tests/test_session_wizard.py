from django.core.urlresolvers import reverse
from django.test import TestCase

from merlin.tests.fixtures.testproject import forms
from merlin.wizards.session import SessionWizard
from merlin.wizards.utils import Step


class SessionWizardTest(TestCase):

    def test_type_error_if_session_wizard_is_not_list(self):
        try:
            SessionWizard((
                Step('user-details', forms.UserDetailsForm),
                Step('contact-details', forms.ContactDetailsForm))
            )
            self.fail("We shouldn't be allowed to create a SessionWizard with a tuple")
        except TypeError as te:
            self.assertEquals(te.message, 'steps must be an instance of or subclass of list')

        except Exception as e:
            self.fail("We should only fail with a TypeError, exception was %s" % e)

    def test_type_error_if_step_is_not_type_step(self):
        try:
            SessionWizard([
                ('user-details', forms.UserDetailsForm),
                ('contact-details', forms.ContactDetailsForm)]
            )
            self.fail("We shouldn't be allowed to create a SessionWizard with a tuple")
        except TypeError as te:
            self.assertEquals(te.message, 'All steps must be an instance of Step')

        except Exception as e:
            self.fail("We should only fail with a TypeError, exception was %s" % e)

    def test_steps(self):
        url = reverse('simpletest',
                kwargs={'slug': 'user-details'})

        response = self.client.get(url)