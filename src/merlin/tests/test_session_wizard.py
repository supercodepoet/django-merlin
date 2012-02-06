from BeautifulSoup import BeautifulSoup
from django.core.urlresolvers import reverse
from django.test import TestCase

from merlin.tests.fixtures.testproject import forms
from merlin.wizards import MissingStepException, MissingSlugException
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

    def test_session_wizard_no_slug(self):
        with self.assertRaises(MissingSlugException):
            self.client.get('/simpletest')

    def test_form_not_valid(self):
        response = self.client.get('/simpletest/user-details')
        self.assertEquals(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        self.assertTrue(soup.find('input', id='id_first_name'))
        self.assertTrue(soup.find('input', id='id_last_name'))
        self.assertTrue(soup.find('input', id='id_email'))
        self.assertTrue(soup.find('a', href="/simpletest/contact-details"))
        self.assertFalse(soup.find('a', text="Back"))

        post = self.client.post('/simpletest/user-details', {})
        self.assertEquals(post.status_code, 200)

        #The form should be invalid, and it should put us on the same form as before.
        soup = BeautifulSoup(post.content)
        self.assertTrue(soup.find('input', id='id_first_name'))
        self.assertTrue(soup.find('input', id='id_last_name'))
        self.assertTrue(soup.find('input', id='id_email'))
        self.assertTrue(soup.find('a', href="/simpletest/contact-details"))
        self.assertFalse(soup.find('a', text="Back"))

    def test_session_wizard(self):
        response = self.client.get('/simpletest/user-details')
        self.assertEquals(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        self.assertTrue(soup.find('input', id='id_first_name'))
        self.assertTrue(soup.find('input', id='id_last_name'))
        self.assertTrue(soup.find('input', id='id_email'))
        self.assertTrue(soup.find('a', href="/simpletest/contact-details"))
        self.assertFalse(soup.find('a', text="Back"))

        post = self.client.post('/simpletest/user-details', {
            'first_name': 'Chad',
            'last_name': 'Gallemore',
            'email': 'cgallemore@gmail.com'
        }, follow=True)

        self.assertEquals(post.redirect_chain[0],
            ('http://testserver/simpletest/contact-details', 302))
        self.assertEquals(post.status_code, 200)

        soup = BeautifulSoup(post.content)
        self.assertTrue(soup.find('input', id="id_street_address"))
        self.assertTrue(soup.find('input', id="id_city"))
        self.assertTrue(soup.find('input', id="id_state"))
        self.assertTrue(soup.find('input', id="id_zipcode"))
        self.assertTrue(soup.find('input', id="id_phone"))
        self.assertFalse(soup.find('a', text="Next"))
        self.assertTrue(soup.find('a', text="Back"))
        self.assertTrue(soup.find('a', href="/simpletest/user-details"))

        try:
            post_last = self.client.post(post.request['PATH_INFO'], {
                'street_address': '122 Main St.',
                'city': 'Joplin',
                'state': 'MO',
                'zipcode': '64801',
                'phone': '5555555555'
            })

            self.fail("this should have raised a not implemented error")

        except NotImplementedError as nie:
            self.assertEquals(nie.message, "Your SessionWizard class has not " \
                "defined a done() method, which is required.")

        except Exception as e:
            self.fail("We should have raised a not implemented error, " \
                "instead the exception was %s" % e)

    def test_session_wizard_cancel_default(self):
        response = self.client.get('/simpletest/user-details')
        self.assertEquals(response.status_code, 200)

        post = self.client.post('/simpletest/user-details', {
            'first_name': 'Chad',
            'last_name': 'Gallemore',
            'email': 'cgallemore@gmail.com'
        }, follow=True)

        self.assertEquals(post.redirect_chain[0],
            ('http://testserver/simpletest/contact-details', 302))
        self.assertEquals(post.status_code, 200)

        response = self.client.get('/simpletest/cancel', follow=True)

        self.assertEquals(response.redirect_chain[0],
            ('http://testserver/', 302))
        self.assertEquals(response.status_code, 200)

    def test_session_wizard_cancel_with_redirect(self):
        response = self.client.get('/simpletest/user-details')
        self.assertEquals(response.status_code, 200)

        post = self.client.post('/simpletest/user-details', {
            'first_name': 'Chad',
            'last_name': 'Gallemore',
            'email': 'cgallemore@gmail.com'
        }, follow=True)

        self.assertEquals(post.redirect_chain[0],
            ('http://testserver/simpletest/contact-details', 302))
        self.assertEquals(post.status_code, 200)

        response = self.client.get('/simpletest/cancel?rd=%s' % reverse(
            'test-more'), follow=True)

        self.assertEquals(response.redirect_chain[0],
            ('http://testserver/more', 302))
        self.assertEquals(response.status_code, 200)


class MockWizardTest(TestCase):

    def test_mock_wizard(self):
        response = self.client.get('/bettertest/user-details')
        self.assertEquals(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        self.assertTrue(soup.find('input', id='id_first_name'))
        self.assertTrue(soup.find('input', id='id_last_name'))
        self.assertTrue(soup.find('input', id='id_email'))

        post = self.client.post('/bettertest/user-details', {
            'first_name': 'Chad',
            'last_name': 'Gallemore',
            'email': 'cgallemore@gmail.com'
        }, follow=True)

        self.assertEquals(post.redirect_chain[0],
            ('http://testserver/bettertest/few-more-things', 302))
        self.assertEquals(post.status_code, 200)

        soup = BeautifulSoup(post.content)
        self.assertTrue(soup.find('input', id="id_bio"))

        post = self.client.post(post.request['PATH_INFO'], {
            'bio': 'My bio'
        }, follow=True)

        self.assertEquals(post.redirect_chain[0],
            ('http://testserver/bettertest/social-info', 302))
        self.assertEquals(post.status_code, 200)

        soup = BeautifulSoup(post.content)
        self.assertTrue(soup.find('input', id="id_twitter"))
        self.assertTrue(soup.find('input', id="id_facebook"))

        div = soup.find('div', id="global_id")

        self.assertEquals(div.string, '123456789')

        post = self.client.post(post.request['PATH_INFO'], {
            'twitter': 'http://twitter.com/localbase',
            'facebook': 'http://facebook.com/localbase'
        }, follow=True)

        self.assertEquals(post.status_code, 200)
        self.assertEquals(post.content, 'All done')
