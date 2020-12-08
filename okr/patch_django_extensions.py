def patch():
    from django.utils.encoding import force_str
    from django_extensions.management import modelviz

    class CustomModelGraph(modelviz.ModelGraph):
        def get_appmodel_context(self, appmodel, appmodel_abstracts):
            context = super().get_appmodel_context(appmodel, appmodel_abstracts)
            context["db_table_name"] = appmodel._meta.db_table
            context["docstring"] = appmodel.__doc__
            return context

        def add_attributes(self, field, abstract_fields):
            attrs = super().add_attributes(field, abstract_fields)
            attrs["verbose_name"] = force_str(field.verbose_name)
            attrs["help_text"] = force_str(field.help_text)
            return attrs

    modelviz.ModelGraph = CustomModelGraph
