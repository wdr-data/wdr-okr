""" """

from os import environ

from django.core.paginator import Paginator
from django.db import connection
from django.utils.functional import cached_property
from loguru import logger


# Source: https://medium.com/squad-engineering/estimated-counts-for-faster-django-admin-change-list-963cbf43683e
class LargeTablePaginator(Paginator):
    """
    Warning: Postgresql only hack
    Overrides the count method of QuerySet objects to get an estimate instead of actual count when not filtered.
    However, this estimate can be stale and hence not fit for situations where the count of objects actually matter.
    """

    @cached_property
    def count(self):
        query = self.object_list.query
        if not query.where:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT reltuples FROM pg_class WHERE relname = %s",
                    [query.model._meta.db_table],
                )
                return int(cursor.fetchone()[0])
            except Exception:
                logger.warning("Failed to do performant count on {}", query)
                return super().count
        else:
            return super().count


def large_table(cls):
    """
    Class decorator to apply custom paginator that doesn't do accurate row counts
    as they are exceedingly slow for large tables.
    Triggers only if we're connected to PostgreSQL.
    """

    if environ.get("DATABASE_URL", "").startswith("postgres://"):
        cls.paginator = LargeTablePaginator
        cls.show_full_result_count = False

    return cls


class UnrequiredFieldsMixin:

    unrequired_fields = []

    def get_form(self, *args, **kwargs):

        form = super().get_form(*args, **kwargs)

        for field in self.unrequired_fields:
            try:
                form.base_fields[field].required = False
            except Exception:
                # Fails when user has read-only permissions as they won't be fields in that case
                pass

        return form
