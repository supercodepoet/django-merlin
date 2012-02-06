from functools import wraps

from django.http import *
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from merlin.wizards import MissingStepException, MissingSlugException

from merlin.wizards.utils import *


def modifies_session(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        result = func(self, request, *args, **kwargs)
        request.session.modified = True

        return result
    return wrapper


class SessionWizard(object):
    """
    This class allows for the ability to chop up a long form into sizable steps
    and process each step in sequence. It also provides the ability to go back
    to a previous step or move on to the next step in the sequence. When the
    wizard runs out of steps it calls a final function that finishes the form
    process. This class should be subclassed and the subclass should at a
    minimum override the ``done`` method.

    .. versionadded:: 0.1

    :param steps:
        Provides a list of :class:`Step` objects in the order in
        which the wizard should display them to the user. This list can
        be manipulated to add or remove steps as needed.
    """
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

        clazz = self.__class__

        self.id = '%s.%s' % (clazz.__module__, clazz.__name__,)
        self.base_steps = steps

    def __call__(self, request, *args, **kwargs):
        """
        Initialize the step list for the session if needed and call the proper
        HTTP method handler.
        """
        self._init_wizard(request)

        slug = kwargs.get('slug', None)

        if not slug:
            raise MissingSlugException("Slug not found.")

        step = self.get_step(request, slug)

        if not step:
            if slug == 'cancel':
                self.cancel(request)
                redirect = request.REQUEST.get('rd', '/')

                return HttpResponseRedirect(redirect)

            raise MissingStepException("Step for slug %s not found." % slug)

        method_name = 'process_%s' % request.method
        method = getattr(self, method_name)

        return method(request, step)


    def _init_wizard(self, request):
        """
        Since the SessionWizard can be used as the callable for the urlconf
        there will be only one instance of the class created. We need to
        make sure each session has its own copy of the step list to manipulate.
        This way multiple connections will not trample on each others steps.
        """
        if self.id not in request.session:
            request.session[self.id] = WizardState(
                steps=self.base_steps[:], # Copies the list
                current_step=self.base_steps[0],
                form_data={})

        self.initialize(request, request.session[self.id])

    def _get_state(self, request):
        """
        Returns the :class:`WizardState` object used to manage this
        wizards internal state.
        """
        return request.session[self.id]

    def _show_form(self, request, step, form):
        """
        Render the provided form for the provided step to the
        response stream.
        """
        context = self.process_show_form(request, step, form)

        return self.render_form(request, step, form, {
            'current_step': step,
            'form': form,
            'previous_step': self.get_before(request, step),
            'next_step': self.get_after(request, step),
            'url_base': self._get_URL_base(request, step),
            'extra_context': context
        })

    def _set_current_step(self, request, step):
        """
        Sets the currenlty executing step.
        """
        self._get_state(request).current_step = step

        return step

    def _get_URL_base(self, request, step):
        """
        Returns the base URL of the wizard.
        """
        index = request.path.rfind(step.slug)

        return request.path[:index]

    def process_GET(self, request, step):
        """
        Renders the ``Form`` for the requested :class:`Step`
        """
        form_data = self.get_cleaned_data(request, step)

        if form_data:
            form = step.form(form_data)

        else:
            form = step.form()

        return self._show_form(request, step, form)

    def process_POST(self, request, step):
        """
        Processes the current :class:`Step` and either send a redirect to the
        next :class:`Step` in the sequence or finished the wizard process
        by calling ``self.done``
        """
        form = step.form(request.POST)

        if not form.is_valid():
            return self._show_form(request, step, form)

        self.set_cleaned_data(request, step, form.cleaned_data)
        self.process_step(request, step, form)
        next_step = self.get_after(request, step)

        if next_step:
            url_base = self._get_URL_base(request, step)

            return HttpResponseRedirect(urljoin(url_base, next_step.slug))

        else:
            return self.done(request)

    def get_steps(self, request):
        """
        Returns the list of :class:`Step`s used in this wizard sequence.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.
        """
        return self._get_state(request).steps

    def get_step(self, request, slug):
        """
        Returns the :class:`Step` that matches the provided slug.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param slug:
            The unique identifier for a particular :class:`Step` in the
            sequence.
        """
        steps = self.get_steps(request)

        try:
            return [step for step in steps if step.slug == slug][0]

        except IndexError:
            return None

    def get_before(self, request, step):
        """
        Returns the previous :class:`Step` in the sequence after the provided
        :class:`Step`. This function will return ``None`` if there is no
        previous step.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param step:
            The :class:`Step` to use as an index for finding the next
            :class:`Step`
        """
        steps = self.get_steps(request)
        index = steps.index(step)

        if index > 0:
            return steps[index - 1]

        else:
            return None

    def get_after(self, request, step):
        """
        Returns the next :class:`Step` in the sequence after the provided
        :class:`Step`. This function will return ``None`` if there is no
        next step.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param step:
            The :class:`Step` to use as an index for finding the next
            :class:`Step`
        """
        steps = self.get_steps(request)
        index = steps.index(step)

        try:
            return steps[index + 1]

        except IndexError:
            return None

    @modifies_session
    def remove_step(self, request, step):
        """
        Removes step from the wizard sequence.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param step:
            The :class:`Step` to remove.
        """
        steps = self.get_steps(request)

        if step in steps:
            steps.remove(step)

    @modifies_session
    def insert_before(self, request, current_step, step):
        """
        Inserts a new step into the wizard sequence before the provided step.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param current_step:
            The :class:`Step` to use as an index for inserting a new step

        :param step:
            The new :class:`Step` to insert.
        """
        steps = self.get_steps(request)

        if step not in steps:
            index = steps.index(current_step)
            steps.insert(index, step)

    @modifies_session
    def insert_after(self, request, current_step, step):
        """
        Inserts a new step into the wizard sequence after the provided step.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param current_step:
            The :class:`Step` to use as an index for inserting a new step

        :param step:
            The new :class:`Step` to insert.
        """
        steps = self.get_steps(request)

        if step not in steps:
            index = steps.index(current_step) + 1
            steps.insert(index, step)

    def get_cleaned_data(self, request, step):
        """
        Returns the cleaned form data for the provided step.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param step:
            The :class:`Step` to use to pull the cleaned form data.
        """
        return self._get_state(request).form_data.get(step.slug, None)

    @modifies_session
    def set_cleaned_data(self, request, step, data):
        """
        Sets the cleaned form data for the provided step.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param step:
            The :class:`Step` to use to store the cleaned form data.

        :param data:
            The cleaned ``Form`` data to store.
        """
        self._get_state(request).form_data[step.slug] = data

    def get_form_data(self, request):
        """
        This will return the form_data dictionary that has been saved in the
        session.  This will mainly be used in the done to query for the form_data
        that has been saved throughout the wizard process.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.
        """
        return request.session[self.id]['form_data']

    def clear(self, request):
        """
        Removes the internal wizard state from the session. This should be
        called right be for the return from a successful
        :meth:`~SessionWizard.done()` call.
        """
        del request.session[self.id]

    # METHODS SUBCLASSES MIGHT OVERRIDE IF APPROPRIATE ########################
    def initialize(self, request, wizard_state):
        """
        Hook used to initialize the wizard subclass. This will be called for
        every request to the wizard before it processes the GET or POST.

        :param request:
            A ``HttpRequest`` object for this request.

        :param wizard_state:
            The :class:`WizardState` object representing the current state of
            the wizard. Extra information can be appended to the state so it
            can be available to :class:`Step`'s of the wizard.

            For example::
                if 'profile' not in wizard_state:
                    wizard_state.profile = request.user.get_profile()
        """
        pass

    def cancel(self, request):
        """
        Hook used to cancel a wizard. This will be called when slug is passed
        that matches "cancel". By default the method will clear the session
        data.

        :param request:
            A ``HttpRequest`` object for this request.
        """
        self.clear(request)

    def process_show_form(self, request, step, form):
        """
        Hook used for providing extra context that can be used in the
        template used to render the current form.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param step:
            The current :class:`Step` that is being processed.

        :param form:
            The Django ``Form`` object that is being processed.
        """
        pass

    def process_step(self, request, step, form):
        """
        Hook for modifying the ``SessionWizard``'s internal state, given a fully
        validated ``Form`` object. The ``Form`` is guaranteed to have clean,
        valid data.

        This method should *not* modify any of that data. Rather, it might want
        dynamically alter the step list, based on previously submitted forms.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param step:
            The current :class:`Step` that is being processed.

        :param form:
            The Django ``Form`` object that is being processed.
        """
        pass

    def get_template(self, request, step, form):
        """
        Responsible for return the path to the template that should be used
        to render this current form.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param step:
            The current :class:`Step` that is being processed.

        :param form:
            The Django ``Form`` object that is being processed.
        """
        return 'forms/wizard.html'

    def render_form(self, request, step, form, context):
        """
        Renders a form with the provided context and returns a ``HttpResponse``
        object. This can be overridden to provide custom rendering to the
        client or using a different template engine.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.

        :param step:
            The current :class:`Step` that is being processed.

        :param form:
            The Django ``Form`` object that is being processed.

        :param context:
            The default context that templates can use which also contains
            any extra context created in the ``process_show_form`` hook.
        """
        return render_to_response(self.get_template(request, step, form),
            context, RequestContext(request))

    def done(self, request):
        """
        Responsible for processing the validated form data that the wizard
        collects from the user. This function should be overridden by the
        implementing subclass. This function needs to return a ``HttpResponse``
        object.

        :param request:
            A ``HttpRequest`` object that carries along with it the session
            used to access the wizard state.
        """
        raise NotImplementedError("Your %s class has not defined a done() " \
                                  "method, which is required." \
                                  % self.__class__.__name__)
