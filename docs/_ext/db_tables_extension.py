"""Custom Sphinx extension to inject database documentation into a ReST document."""

from docutils import nodes
from docutils.parsers.rst import Directive

import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from database_tables import build_html  # noqa: E402


class DbTables(Directive):
    def run(self):
        db_tables_html = build_html(
            app_labels=["okr"],
            html_top='<div id="db_tables">',
            html_bottom="</div>",
        )
        paragraph_node = nodes.raw("", db_tables_html, format="html")

        return [paragraph_node]


def setup(app):
    app.add_directive("db_tables", DbTables)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
