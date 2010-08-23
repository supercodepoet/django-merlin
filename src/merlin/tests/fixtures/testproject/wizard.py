from django.http import HttpResponse

from merlin.tests.fixtures.testproject import forms
from merlin.wizards.session import SessionWizard
from merlin.wizards.utils import Step


class MockWizard(SessionWizard):
    def done(self, request):
        return HttpResponse("All done", mimetype="text/plain")

    def process_step(self, request, current_step, form):
        if current_step.slug == 'user-details':
            new_step = Step('few-more-things', forms.FewMoreThingsForm)
            self.insert_after(request, current_step, new_step)

        elif current_step.slug == 'few-more-things':
            new_step = Step('social-info', forms.SocialForm)
            step = self.get_step(request, 'contact-details')
            self.insert_before(request, step, new_step)

        elif current_step.slug == 'social-info':
            step = self.get_step(request, 'contact-details')
            self.remove_step(request, step)