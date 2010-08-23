from collections import namedtuple
from uuid import uuid4

from django import forms
from django.http import *


_WizardState = namedtuple('_WizardState', ('steps', 'current_step', 'data'))


class SessionWizard(object):
    """
    Add docs
    """

    def __init__(self, steps):
        if [step for step in steps if not isinstance(step, forms.Form)]:
            raise TypeError('Forms but be of type Django Form.')

        slugs = set([step.slug for step in steps])

        # By putting the slugs into a set the duplicates will be filtered out.
        # If the slug list length does not equal the steps length then there
        # must have been duplicates.
        if len(slugs) != len(steps):
            raise ValueError('Step slugs must be unique.')

        self.id = str(uuid4())
        self.base_steps = steps

    def __call__(self, request, *args, **kwargs):
        """
        Initialize the form list for the session if needed and call the proper
        HTTP method handler.
        """
        self._init_wizard(request)
        slug = kwargs.get('slug', None)

        if not slug:
            steps = self.get_steps(request)
            slug = steps[0].slug

        try:
            method_name = 'process_%s' % request.method
            method = getattr(self, method_name)

            return method(request, slug)

        except AttributeError:
            raise Http404()

    def _init_wizard(self, request):
        """
        Since the SessionWizard is used as the callable for the urlconf there
        will be only one instance of the class created. We need to make sure
        each session has its own copy of the step list to manipulate. This
        way multiple connections will not trample on each others steps.
        """
        if self.id not in request.session:
            wizard_state = _WizardState(
                steps=self.base_steps[:],
                current_step=self.base_steps[0],
                form_data={})

            request.session[self.id] = wizard_state

    def process_GET(self, request, slug):
        pass

    def process_POST(self, request, slug):
        pass

    def get_steps(self, request):
        """
        Pull the steps associated with this session
        """
        return request.session.get(self.id).steps
