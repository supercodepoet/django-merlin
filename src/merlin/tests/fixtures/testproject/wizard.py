from django.http import HttpResponse

from merlin.tests.fixtures.testproject import forms
from merlin.wizards.session import SessionWizard
from merlin.wizards.utils import Step


class MockWizard(SessionWizard):
    def done(self, request):
        return HttpResponse("All done", mimetype="text/plain")

    def process_step(self, request, current_step, form):
        if current_step.slug == 'user-details':
            few_more_things_step = Step('few-more-things', forms.FewMoreThingsForm)
            self.insert_after(request, current_step, few_more_things_step)

            social_step = Step('social-info', forms.SocialForm)
            contact_step = self.get_step(request, 'contact-details')
            self.insert_before(request, contact_step, social_step)

            self.remove_step(request, contact_step)
