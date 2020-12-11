def patch():
    from django.utils.encoding import force_str
    from django_extensions.management import modelviz
    from django.db import connection

    class CustomModelGraph(modelviz.ModelGraph):
        def get_appmodel_context(self, appmodel, appmodel_abstracts):
            context = super().get_appmodel_context(appmodel, appmodel_abstracts)
            context["db_table_name"] = appmodel._meta.db_table
            context["unique_together"] = appmodel._meta.unique_together
            context["docstring"] = appmodel.__doc__
            return context

        def add_attributes(self, field, abstract_fields):
            attrs = super().add_attributes(field, abstract_fields)
            attrs["column_name"] = force_str(field.column)
            attrs["verbose_name"] = force_str(field.verbose_name)
            attrs["help_text"] = force_str(field.help_text)
            attrs["internal_type"] = force_str(field.get_internal_type())
            attrs["db_type"] = field.db_type(connection)
            attrs["null"] = field.null
            attrs["unique"] = field.unique
            return attrs

        def get_relation_context(self, target_model, field, label, extras):
            relation = super().get_relation_context(target_model, field, label, extras)
            relation["column_name"] = force_str(field.column)
            relation["target_table_name"] = force_str(target_model._meta.db_table)
            return relation

    modelviz.ModelGraph = CustomModelGraph