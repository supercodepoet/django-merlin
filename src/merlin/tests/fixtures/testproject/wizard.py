from django.http import HttpResponse

from merlin.tests.fixtures.testproject import forms
from merlin.wizards.session import SessionWizard
from merlin.wizards.utils import Step


class MockWizard(SessionWizard):
    def initialize(self, request, wizard_state):
        if not 'global_id' in wizard_state:
            wizard_state.global_id = '123456789'

    def done(self, request):
        form_data = self.get_form_data(request)
        assert form_data['user-details']['first_name'] == 'Chad'
        assert form_data['user-details']['last_name'] == 'Gallemore'
        assert form_data['user-details']['email'] == 'cgallemore@gmail.com'
        assert form_data['few-more-things']['bio']  == 'My bio'
        assert form_data['social-info']['twitter'] == 'http://twitter.com/localbase'
        assert form_data['social-info']['facebook'] == 'http://facebook.com/localbase'

        self.clear(request)

        return HttpResponse("All done", mimetype="text/plain")

    def process_step(self, request, current_step, form):
        if current_step.slug == 'user-details':
            few_more_things_step = Step('few-more-things', forms.FewMoreThingsForm)
            self.insert_after(request, current_step, few_more_things_step)

            social_step = Step('social-info', forms.SocialForm)
            contact_step = self.get_step(request, 'contact-details')
            self.insert_before(request, contact_step, social_step)

            self.remove_step(request, contact_step)

    def get_template(self, request, step, form):
        if step.slug == 'social-info':
            return 'forms/social_wizard.html'

        else:
            return 'forms/wizard.html'

    def process_show_form(self, request, step, form):
        if step.slug == 'social-info':
            return {
                'global_id': self._get_state(request).global_id}
