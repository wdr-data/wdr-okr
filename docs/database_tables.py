import collections
import django
import os
import sys

from tabulate import tabulate

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DOCS_DIR)

sys.path.insert(0, BASE_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from django_extensions.management.modelviz import generate_graph_data

from database_tables_config import APP_LABELS, HTML_TOP, HTML_BOTTOM, FILENAME


def build_html(app_labels: list, html_top: str, html_bottom: str) -> str:
    """Create an HTML page with a series of html tables for each table in the database.

    Args:
        app_labels (list): List of Django apps to include in HTML page.
        html_top (str): HTML code to insert above generated table.
        html_bottom (str): HTML code to insert below generated table.

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

                if field["relation"]:
                    data_type = f'{field["db_type"]} ({field["internal_type"]})'
                elif field["type"] == "AutoField":
                    data_type = f'{field["db_type"]} ({field["type"]})'
                else:
                    data_type = f'{field["db_type"]}'

                nullable = "✅" if field["null"] else "❌"
                unique = "✅" if field["unique"] else "❌"

                table_fields.append(
                    [field["name"], data_type, unique, nullable, description]
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
                    foreign_key_text = ""
                    for relation in db_table["relations"]:
                        if relation["type"] == "ForeignKey":
                            foreign_key_text += f'<li>Den Foreign Key <a href="#{relation["target"]}">"{relation["name"]}"</a></li>'
                    if foreign_key_text:
                        info_text += "<p>Diese Tabelle nutzt folgende Foreign Keys:</p>"
                        info_text += "<ul>"
                        info_text += foreign_key_text
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
            f"<h3><a name='{table_infos[2]}'>Database Tabellenname: {table_name}</a></h3>"
            + f"<div class='docstring'>{table_infos[0]}</div>"
            + "\n"
            + tabulate(
                table_infos[1],
                headers=["Name", "Type", "UNIQUE", "NULL", "Beschreibung"],
                tablefmt="html",
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
    print(f"Data written to {filepath}")
