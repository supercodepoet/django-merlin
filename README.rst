Django Merlin
=============

What's this for
---------------

The Django FormWizard was not exactly what we were looking for so we decided to
scratch our own itch and create a project that would host different types
of form wizards for use with Django. Currently we have a SessionWizard, which is
a form wizard that is backed by the Django session object. This wizard provides
the ability to use the SessionWizard as a callable in the URLConf but still
provide thread safety.

Besides the storage of SessionWizard state being in session, it uses an HTTP
GET to render a form and a POST to process a form. This differs from the
Django FormWizard which uses POST for everything. One benefit of this is the
ability to got to previous steps in the wizard.

Documentation and examples can be found at: http://packages.python.org/django-merlin/

Installation
------------

You need Django for this to work, if you need help with that `head here
<http://djangoproject.com>`_

Using Pip::

    pip install django-merlin

Credits
-------

This was mostly inspired by the Django form wizard and the SessionWizard snippet
located `here <http://djangosnippets.org/snippets/1078/>`_
