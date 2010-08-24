.. _sessionwizard:

==============
Session Wizard
==============

Django comes with an optional "form wizard" application that allows you to
split forms across multiple web pages in a sequential order. This ability is
provided by using the :class:`~django.contrib.formtools.wizard.FormWizard`
class. You would use this when you have, for example, a long registration
process that needs to be split up in small digestable chunks, making it
easier on your users to complete the process.

You can see the :class:`~django.contrib.formtools.wizard.FormWizard`
documentation at:
http://docs.djangoproject.com/en/dev/ref/contrib/formtools/form-wizard/

Is there a need for a different one?
====================================

In a word, yes. A few things the ``FormWizard`` does that may not work for your
projects, as it did not for ours. First, the ``FormWizard`` using an HTTP
``POST`` to process a form. This makes it tough when you are trying to use
the browser's back button to change some data on a previous step. The
``FormWizard`` checks for any ``GET`` requests and moves you to the first
step in the wizard process, YUCK! Secondly, the ``FormWizard`` docs recommends
using your wizard subclass as the callable in a ``urlconf`` in your urls.py.
This is a really nice feature except that it will only create one copy of
your ``FormWizard`` for all requests. This works well until you start messing
with the hooks it provides to inserting or removing steps based on data
from a form submission. Once you insert or remove a form, the steps are now
changed for any subsequent users.

How is ``SessionWizard`` different?
===================================

    1. The :ref:`SessionWizard <api_sessionwizard>` is given a list of
       :ref:`Step <api_step>` objects instead of a list of Django ``Form``
       classes.
    2. :ref:`SessionWizard <api_sessionwizard>` stores all of its state in the
       Django ``Session`` object. This allows you to use the ``SessionWizard``
       in the ``urlconf`` and keep state seperate by user (or session). When
       the ``SessionWizard`` starts it makes a copy of the
       :ref:`Step <api_step>` list for the session so it can be manipulated
       independantly of any other session.
    3. The :ref:`SessionWizard <api_sessionwizard>` process all ``GET`` requests
       as a form view and only moves to the next step in the sequence on a
       succesful ``POST`` request. This allows for the browser's Back button
       to function correctly.
    4. Each :ref:`Step <api_step>` in the sequence has a unique slug for that
       step. This slug is used in the ``urlconf`` to be able to go to any part
       of the wizard. This allows you to provide proper "Back" and "Next"
       buttons on your forms.

How to use ``SessionWizard``
============================

Here is the basic workflow needed to use the ``SessionWizard`` object:

    1. Make sure you have enabled the Django session middleware.
    2. Create a subclass the ``SessionWizard`` class and override the
       ``done`` method. The ``done`` method allows you to collect all of the
       validated form data, process that data and move on to the next
       web page after successful processing of the wizard.
    3. Override the ``get_template`` method to return the path to the template
       the forms should use. The default is to return "forms/wizard.html",
       which you provide. Based on the step passed in you could return different
       templates for different forms.
    4. Create a url that will be the entry point of your wizard. This url should
       provide a (?P<slug>[A-Za-z0-9_-]+) option in the url pattern.
    5. Point this url to the subclass of ``SessionWizard``, providing a ``list``
       of :ref:`Step <api_step>` objects that the wizard should process in the
       order it should process them.
    6. Sit back and enjoy form wizard goodness!

How it works
============

    1. The user makes a ``GET`` request to your wizard url with the first
       slug of the sequence.
    2. The wizard returns the form using the template you specify.
    3. The user submits the form using a ``POST`` request.
    4. The wizard validates the form data. If the data is invalid it returns the
       user to the current form and you can display to the user any errors
       that have occured. If the data is valid then the wizard stores the
       clean data in its state object.
    5. If there is another step in the process the wizard sends a redirect to
       the user to the next step in the sequence. If not next step is found
       the wizard then calls the ``done`` method, which expects to return
       some ``HttpResponse`` to the user letting them know they are
       finished with the process.

Creating templates for the forms
================================

You'll need to create a template that renders the step's form. By
default, every form uses a template called :file:`forms/wizard.html`. (You can
change this template name by overriding :meth:`~SessionWizard.get_template()`)

The template recieves the following context:

    * ``current_step`` -- The current :ref:`Step <api_step>` being processed
    * ``form``-- The current form for the current step (with any data already
      available)
    * ``previous_step`` -- The previous :ref:`Step <api_step>` or ``None``
    * ``next_step`` -- The next :ref:`Step <api_step>` or ``None``
    * ``url_base`` -- The base URL that can be used in creating links to the
      next for previous steps
    * ``extra_context`` -- Any extra context you have provided using
      overriding the :meth:`~SessionWizard.process_show_form()` method

A couple of goodies
===================

There are couple of hooks in the ``SessionWizard`` that allow you to modify the
execution of the wizard in interesting ways. For more in depth information make
sure to check out the API docs for :ref:`SessionWizard <api_sessionwizard>`.

    * :meth:`~SessionWizard.process_show_form()` -- allows you to provide any
      extra context data that needs to be provided to the template for
      processing
    * :meth:`~SessionWizard.process_step()` -- allows for changing the internal
      state of the wizard. For example, you could use this hook to add or remove
      steps in the process based off some user submitted information. You can
      use the methods to :meth:`~SessionWizard.remove_step()`,
      :meth:`~SessionWizard.insert_before()` and
      :meth:`~SessionWizard.insert_after()` accomplish this.
    * :meth:`~SessionWizard.get_template()` -- allows you to return a template
      path to use for processing the currently executing step.
    * :meth:`~SessionWizard.render_form()` -- allows you the ability to render
      the form however you see fit. The default is to use the
      ``render_to_response`` Django shortcut; but, you could use this hook
      to provide a :class:`PageAssembly` render method from the excellent
      django-crunchyfrog project found at :
      http://github.com/localbase/django-crunchyfrog


Enjoy!
======

We are always looking for updates to make ``SessionWizard`` even better and
provide even more form wizards to this tool chest. If you have any questions,
comments or suggestions please email us at development@localbase.com. You can
always particapte by using the projects GitHub account as well:
http://github.com/localbase/django-merlin
