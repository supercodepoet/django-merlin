from django import forms


class Step(object):
    def __init__(self, slug, form):
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
