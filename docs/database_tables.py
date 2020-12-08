import collections
import django
import os
import sys


from tabulate import tabulate

sys.path.insert(0, os.path.abspath("../"))
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
                table_fields.append([field["name"], field["type"], description])

            if (
                db_table["fields"][0]["name"] == "id"
                and db_table["fields"][0]["type"] == "AutoField"
            ):
                output_table_dict[db_table["db_table_name"]] = [
                    db_table["docstring"],
                    table_fields,
                ]

    # sort dict of database tables alphabetically
    output_sorted = collections.OrderedDict(sorted(output_table_dict.items()))

    # collect HTML items in a string
    html_tables = ""
    for table_name, table_infos in output_sorted.items():
        # embed output table in HTML
        html_tables += (
            f"<h3>Database Tabellenname: {table_name}</h3>"
            + f"<div class='docstring'>{table_infos[0]}</div>"
            + "\n"
            + tabulate(
                table_infos[1],
                headers=["Name", "Type", "Beschreibung"],
                tablefmt="html",
            )
            + "\n"
        )

    return str(html_top + html_tables + html_bottom)


if __name__ == "__main__":

    # generate html page (based on constants from database_tables_config)
    html_page = build_html(APP_LABELS, HTML_TOP, HTML_BOTTOM)

    # write output to file
    with open(FILENAME, "wt") as output_file:
        output_file.write(html_page)
    print(f"Data written to {FILENAME}")
