from UserDict import UserDict

from django import forms


__all__ = ('Step', 'WizardState',)


class Step(object):
    """
    Wrapper for providing a :class:`SessionWizard` with a ``Form`` sequence to
    process.
    """
    def __init__(self, slug, form):
        """
        Contructs a new ``Step`` object by providing a slug and a ``Form`` to
        be used for this step in the sequnce.

        e.g.::

            Step('user-details', UserDetailsForm)

        :param slug:
            The unique identifer for this :class:`Step`. This slug is used
            throughout the :class:`SessionWizard` for navigating to the
            proper form for rendering.

        :param form:
            An Django ``Form`` subclass that should be used for this step in
            the sequence.
        """
        if not issubclass(form, forms.Form):
            raise ValueError('Form must be subclass of a Django Form')

        self.slug = str(slug)
        self.form = form

    def __hash__(self):
        return hash(self.slug)

    def __eq__(self, other):
        if isinstance(other, Step):
            return self.__hash__() == other.__hash__()

        return False

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return str(self.slug)

    def __unicode__(self):
        return unicode(self.slug)

    def __repr__(self):
        return str(self)


class WizardState(UserDict):
    """
    Provides the ability for a :class:`SessionWizard` to keep track of its
    state by storing the list of steps, the currently executing step and any
    validated form data for the steps.
    """
    def __init__(self, *args, **kwargs):
        UserDict.__init__(self, *args, **kwargs)

        self.steps = kwargs.get('steps', None)
        self.current_step = kwargs.get('current_step', None)
        self.form_data = kwargs.get('form_data', None)
