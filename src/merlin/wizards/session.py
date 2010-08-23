from urlparse import urljoin
from uuid import uuid4

from django.http import *
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from merlin.wizards.utils import *


class SessionWizard(object):
    # TODO: add class documentation
    def __init__(self, steps):
        if not isinstance(steps, list):
            raise TypeError('steps must be an instance of or subclass of list')

        if [step for step in steps if not isinstance(step, Step)]:
            raise TypeError('All steps must be an instance of Step')

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
            raise Http404()

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
            request.session[self.id] = WizardState(
                steps=self.base_steps[:], # Copies the list
                current_step=self.base_steps[0],
                form_data={})

    def _get_state(self, request):
        return request.session[self.id]

    def _show_form(self, request, slug, form):
        context = self.process_show_form(request, slug, form)
        step = self._set_current_step(request, slug)

        return self.render_form(request, slug, form, {
            'current_step': step,
            'form': form,
            'previous_step': self.get_before(request, step),
            'next_step': self.get_after(request, step),
            'url_base': self._get_URL_base(request, slug),
            'extra_context': context
        })

    def _set_current_step(self, request, slug):
        step = self.get_step(request, slug)
        self._get_state(request).current_step = step

        return step

    def _get_URL_base(self, request, slug):
        index = request.path.find(slug)

        return request.path[:index]

    def process_GET(self, request, slug):
        form_data = self.get_cleaned_data(request, slug)
        step = self.get_step(request, slug)

        if form_data:
            form = step.form(initial=form_data)

        else:
            form = step.form()

        return self._show_form(request, slug, form)

    def process_POST(self, request, slug):
        step = self.get_step(request, slug)
        form = step.form(request.POST)

        if form.is_valid():
            self.set_cleaned_data(request, slug, form.cleaned_data)
            self.process_step(request, slug, step, form)
            next_step = self.get_after(request, step)

            if next_step:
                url_base = self._get_URL_base(request, slug)

                return HttpResponseRedirect(urljoin(url_base, next_step.slug))

            else:
                try:
                    return self.done(request)

                finally:
                    self.clear(request)

        return self._show_form(request, slug, form)

    def get_steps(self, request):
        return self._get_state(request).steps

    def get_step(self, request, slug):
        steps = self.get_steps(request)

        try:
            return [step for step in steps if step.slug == slug][0]

        except IndexError:
            return None

    def get_before(self, request, step):
        steps = self.get_steps(request)
        index = steps.index(step)

        if index > 0:
            return steps[index - 1]

        else:
            return None

    def get_after(self, request, step):
        steps = self.get_steps(request)
        index = steps.index(step)

        try:
            return steps[index + 1]

        except IndexError:
            return None

    def remove_step(self, request, step):
        steps = self.get_steps(request)

        if step in steps:
            steps.remove(step)

    def insert_before(self, request, current_step, step):
        steps = self.get_steps(request)

        if step not in steps:
            index = steps.index(current_step) - 1
            steps.insert(index, step)

    def insert_after(self, request, current_step, step):
        steps = self.get_steps(request)

        if step not in steps:
            index = steps.index(current_step) + 1
            steps.insert(index, step)

    def get_cleaned_data(self, request, slug):
        return self._get_state(request).form_data.get(slug, None)

    def set_cleaned_data(self, request, slug, data):
        self._get_state(request).form_data[slug] = data

    def clear(self, request):
        del request.session[self.id]

    # METHODS SUBCLASSES MIGHT OVERRIDE IF APPROPRIATE #
    def process_show_form(self, request, slug, form):
        """
        Hook for providing extra context to the rendering of the form.
        """
        pass

    def process_step(self, request, slug, form, step):
        """
        Hook for modifying the StepWizard's internal state, given a fully
        validated Form object. The Form is guaranteed to have clean, valid
        data.

        This method should *not* modify any of that data. Rather, it might want
        dynamically alter self.form_list, based on previously submitted forms.

        Note that this method is called every time a page is rendered for *all*
        submitted steps through POST.
        """
        pass

    def get_template(self, request, slug, form):
        """
        Hook for specifying the path of a template to use for rendering this
        form.
        """
        return 'forms/wizard.html'

    def render_form(self, request, slug, form, context):
        """
        Hook for altering how the form is rendered to the response.
        """
        return render_to_response(self.get_template(request, slug, form),
            context, RequestContext(request))

    def done(self, request):
        """
        Hook for doing something with the validated data. This is responsible
        for the final processing including clearing the session scope of items
        created by this wizard.
        """
        raise NotImplementedError("Your %s class has not defined a done() " + \
                                  "method, which is required." \
                                  % self.__class__.__name__)
