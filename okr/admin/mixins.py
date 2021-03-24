""" """

class UnrequiredFieldsMixin():

    unrequired_fields = []

    def get_form(self, *args, **kwargs):

        form = super().get_form(*args, **kwargs)

        for field in self.unrequired_fields:
            form.base_fields[field].required = False

        return form
