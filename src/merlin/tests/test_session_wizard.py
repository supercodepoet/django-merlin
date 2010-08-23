from django.core.urlresolvers import reverse
from django.test import TestCase


class SessionWizardTest(TestCase):

    def test_steps(self):
        url = reverse('simpletest',
                kwargs={'slug': 'user-details'})

        response = self.client.get(url)