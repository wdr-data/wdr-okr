import sys
import os
import django

from tabulate import tabulate

sys.path.insert(0, os.path.abspath("../"))
os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from django_extensions.management.modelviz import generate_graph_data


def build_html(app_labels: list, html_top: str, html_bottom: str) -> str:
    """Create an HTML page with a series of html tables for each table in the database.

    Args:
        app_labels (list): List of Django apps to include in HTML page.
        html_top (str): HTML code to insert above generated table.
        html_bottom (str): HTML code to insert below generated table.

    Returns:
        str: HTML page.
    """

    # create empty string to collect HTML items
    html_tables = ""

    # data = generate_graph_data(app_labels)

    # # print(data)
    # for app in data:
    #     # print(app)

    for label in app_labels:
        data = generate_graph_data([label])

        for db_table in data["graphs"][0]["models"]:
            # generate output table
            output_table = []
            for field in db_table["fields"]:
                if field["help_text"]:
                    description = field["help_text"]
                else:
                    description = field["verbose_name"]
                output_table.append([field["name"], field["type"], description])

            # embedd output table in HTML
            html_tables += (
                f'<h1>Database Tabellenname: {db_table["db_table_name"]}</h1>'
                + "\n"
                + tabulate(
                    output_table,
                    headers=["Name", "Type", "Beschreibung"],
                    tablefmt="html",
                )
                + "\n\n"
            )

    return str(html_top + html_tables + html_bottom)


if __name__ == "__main__":

    # set constants for manual run

    # which apps to include
    # APP_LABELS = ["okr", "admin"]
    APP_LABELS = ["okr"]

    # HTML above generated tables
    HTML_TOP = """
<!doctype html>

<html lang="de">
<head>
<meta charset="utf-8">

<title>Datenbank-Tabellen WDR OKR</title>

<link rel="stylesheet" href="css/styles.css">

</head>

<body>

<div id="main">
    """

    # HTML below generated table
    HTML_BOTTOM = """
</div>

</body>
</html>
    """

    # set name for completed html file
    FILENAME = "index.html"

    # generate html page
    html_page = build_html(APP_LABELS, HTML_TOP, HTML_BOTTOM)

    # write output to file
    with open(FILENAME, "wt") as output_file:
        output_file.write(html_page)

    print(f"Data written to {FILENAME}")
