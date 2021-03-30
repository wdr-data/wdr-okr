"""Read database information from Django models and create a HTML table for the
documentation.
"""

import collections
import os
import sys

import django
from loguru import logger

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DOCS_DIR)

sys.path.insert(0, BASE_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from django_extensions.management.modelviz import generate_graph_data

from database_tables_config import APP_LABELS, HTML_TOP, HTML_BOTTOM, FILENAME


def tabulate(head, rows, head_classes=None, row_classes=None):
    head_classes = head_classes or {}
    row_classes = row_classes or {}

    th = []
    for i, item in enumerate(head):
        attrs = []
        if i in head_classes:
            attrs.append(f'class="{head_classes[i]}"')
        th.append(f"<th{' ' if attrs else ''}{' '.join(attrs)}>{item}</th>")

    tr = []
    for row in rows:
        td = []
        for i, item in enumerate(row):
            attrs = []
            if i in row_classes:
                attrs.append(f'class="{row_classes[i]}"')
            td.append(f"<td{' ' if attrs else ''}{' '.join(attrs)}>{item}</td>")
        tr.append(f"<tr>{' '.join(td)}</tr>")

    head_html = f"<thead><tr>{' '.join(th)}</tr></thead>"
    body_html = "<tbody>" + "\n".join(tr) + "</tbody>"

    return f"<table>{head_html}\n{body_html}</table>"


def build_html(
    app_labels: list = APP_LABELS,
    html_top: str = HTML_TOP,
    html_bottom: str = HTML_BOTTOM,
) -> str:
    """Create an HTML page with a series of html tables for each table in the database.

    Args:
        app_labels (list): List of Django apps to include in HTML page. Defaults to APP_LABELS.
        html_top (str): HTML code to insert above generated table. Defaults to HTML_TOP.
        html_bottom (str): HTML code to insert below generated table. Defaults to HTML_BOTTOM.

    Returns:
        str: HTML page.
    """

    # generate a dict with the table names as keys
    output_table_dict = {}

    for label in app_labels:

        # read basic data with django_extensions.management.modelviz
        data = generate_graph_data([label])

        for db_table in data["graphs"][0]["models"]:
            # generate data for each table (include help_text if present, if not use verbose_name)
            table_fields = []
            for field in db_table["fields"]:
                if field["help_text"]:
                    description = field["help_text"]
                else:
                    description = field["verbose_name"]

                data_type = f'<code>{field["db_type"]}</code>'

                if field["relation"]:
                    field_type = field["internal_type"]
                    field_type = field_type.replace("ForeignKey", "FK")
                    data_type = f"{data_type} (<b>{field_type}</b>)"
                # elif field["type"] == "AutoField":
                #    data_type = f'{data_type}<br/><b>{field["type"]}</b>'

                nullable = "✅" if field["null"] else "❌"
                unique = "✅" if field["unique"] else "❌"

                table_fields.append(
                    [
                        f"<code>{field['column_name']}</code>",
                        data_type,
                        unique,
                        nullable,
                        description,
                    ]
                )

            # only include tables that are stored in db
            if (
                db_table["fields"][0]["name"] == "id"
                and db_table["fields"][0]["type"] == "AutoField"
            ):
                # create table info text from docstring
                docstring_html = db_table["docstring"].replace("\n\n", "<br />\n")
                info_text = f"<p>{docstring_html}</p>"

                # if table uses foreign keys: create a list of foreign keys with links
                if db_table["relations"]:
                    relation_text = ""
                    for relation in db_table["relations"]:
                        if relation["type"] == "ForeignKey":
                            relation_text += f'<li><a href="#{relation["target"]}"><code>{relation["target_table_name"]}</code></a> via <code>{relation["column_name"]}</code></li>'
                        # elif relation["type"] == "ManyToManyField":
                        #     relation_text += f'<li><code>{relation["column_name"]}</code> aus der Tabelle <a href="#{relation["target"]}">{relation["target_table_name"]}</a> (ManyToMany)</li>'
                    if relation_text:
                        if db_table["is_m2m_table"]:
                            info_text += "<p>Sie verbindet die folgenden Tabellen:</p>"
                        else:
                            info_text += "<p>Diese Tabelle hat folgende Relationen zu anderen Tabellen:</p>"
                        info_text += "<ul>"
                        info_text += relation_text
                        info_text += "</ul>"

                if db_table["unique_together"]:
                    info_text += "Für die Tabelle sind die folgenden <code>UNIQUE</code> Constraints definiert: <ul>"
                    for tup in db_table["unique_together"]:
                        info_text += f"<li>{', '.join(f'<code>{field}</code>' for field in tup)}</li>"
                    info_text += "</ul>"

                # combine table name, table info text, table fields, and Django model name
                output_table_dict[db_table["db_table_name"]] = [
                    info_text,
                    table_fields,
                    db_table["name"],
                ]

    # sort dict of database tables alphabetically
    output_sorted = collections.OrderedDict(sorted(output_table_dict.items()))

    # collect HTML items in a string
    html_tables = ""
    for table_name, table_infos in output_sorted.items():
        # convert output table to HTML
        html_tables += (
            f"<h3><a name='{table_infos[2]}'>{table_name}</a></h3>"
            + f"<div class='docstring'>{table_infos[0]}</div>"
            + "\n"
            + tabulate(
                ["Name", "Type", "UNIQUE", "NULL", "Beschreibung"],
                table_infos[1],
                head_classes={2: "mono", 3: "mono"},
                row_classes={2: "hcenter vcenter", 3: "hcenter vcenter"},
            )
            + "\n"
        )

    return str(html_top + html_tables + html_bottom)


if __name__ == "__main__":

    # generate html page (based on constants from database_tables_config)
    html_page = build_html(APP_LABELS, HTML_TOP, HTML_BOTTOM)

    # write output to file
    filepath = os.path.join(DOCS_DIR, FILENAME)
    with open(filepath, "wt") as output_file:
        output_file.write(html_page)
    logger.success("Data written to {}", filepath)
