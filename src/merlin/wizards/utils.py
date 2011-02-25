from UserDict import UserDict

from django import forms


__all__ = ('Step', 'WizardState',)


class Step(object):
    """
    When constucting a form wizard, the wizard needs to be composed of a
    sequental series of steps in which it is to display forms to the user and
    collect the data from those forms. To be able to provide these forms to the
    :ref:`SessionWizard <api_sessionwizard>`, you must first wrap the Django
    :class:`django.forms.Form` in a ``Step`` object. The ``Step`` object gives
    the ability to store the :class:`django.forms.Form` class to be used, as
    well as, a unique slug to be used in the wizard navigation.

    .. versionadded:: 0.1

    :param slug:
        Each step in the wizard should have a unique "slug" that identifies that
        ``Step`` in the process. By using slugs the wizard has the ability to go
        forward, as well as, back in the process adjusting what data it collects
        from the user.

    :param form:
        This *MUST* be a subclass of :class:`django.forms.Form` or
        :class:`django.forms.ModelForm`. This should not be an instance of that
        subclass. The :ref:`SessionWizard <api_sessionwizard>` will use this
        class to create instances for the user. If going back in the wizard
        process, the :ref:`SessionWizard <api_sessionwizard>` will prepopulate
        the form with any cleaned data already collected.
    """
    def __init__(self, slug, form):
        if not issubclass(form, (forms.Form, forms.ModelForm,)):
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
    This class provides the ability for a
    :ref:`SessionWizard <api_sessionwizard>` to keep track of the important
    state of a multi-step form. Instead of keeping track of the state through
    :samp:`<input type="hidden">` fields, it subclasses the python ``UserDict``
    object and stores its data in the properties ``steps``,``current_step``
    and ``form_data``.

    .. versionadded:: 0.1

    :param steps:
        A list of the :ref:`Step <api_step>` objects that provide the sequence
        in which the forms should be presented to the user.

    :param current_step:
        The current :ref:`Step <api_step>` that the user is currently on.

    :param form_data:
        A ``dict`` of the cleaned form data collected to this point and
        referenced using the :ref:`Step <api_step>`'s slug as the key to
        the ``dict``
    """
    def __init__(self, *args, **kwargs):
        UserDict.__init__(self, *args, **kwargs)

        self.steps = kwargs.get('steps', None)
        self.current_step = kwargs.get('current_step', None)
        self.form_data = kwargs.get('form_data', None)
