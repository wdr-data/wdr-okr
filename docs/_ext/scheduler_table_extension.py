"""Custom Sphinx extension to inject the APScheduler's schedule into a ReST document."""

import inspect
import os
import pathlib
import sys

import django

from docutils import nodes
from docutils.parsers.rst import Directive
from operator import itemgetter
from cron_descriptor import get_description, Options
from apscheduler.job import Job
from tabulate import tabulate


CURRENT_DIR = pathlib.Path(__file__).parent.absolute()
BASE_DIR = str(CURRENT_DIR.parents[1].absolute())

sys.path.insert(0, BASE_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from okr.scrapers import scheduler  # noqa: E402


def parse_job_info_method(job: Job) -> str:
    """Parse information about methods in Job object for further processing.

    Args:
        job (Job): Job object to parse

    Returns:
        str: Parsed method information based on Job object.
    """
    # read full path of method
    method_string = inspect.getmodule(job.func).__name__ + "." + job.func.__name__

    # add arguments to method_string (if any)
    args = ", ".join(map(repr, job.args))
    kwargs = ", ".join(f"{key}={repr(value)}" for key, value in job.kwargs.items())

    method_string = f"{method_string}({args}{', ' + kwargs if kwargs else ''})"

    return method_string


def build_schedule_html(html_top: str = "<div>", html_bottom: str = "</div>") -> str:
    """Create a basic HTML table with the currently scheduled jobs.

    Args:
        html_top (str, optional): HTML to go before the table. Defaults to "<div>".
        html_bottom (str, optional): HTML to go at hte end of the table. Defaults to
        "</div>".

    Returns:
        str: HTML code.
    """

    # Ensure scheduler is shut down, then re-add jobs and retrieve scheduled jobs from okr/scrapers/scheduler.py
    scheduler.scheduler.shutdown()
    scheduler.add_jobs()
    jobs_list = scheduler.scheduler.get_jobs()

    options = Options()
    options.locale_code = "de_DE"
    options.use_24hour_time_format = True

    # parse and convert job information into list
    table_lines = []
    for job in jobs_list:
        cron_expression = " ".join(map(str, reversed(job.trigger.fields[1:])))
        table_lines.append(
            [
                parse_job_info_method(job),
                get_description(cron_expression, options=options),
            ]
        )

    # sort list by module and reformat to a module.method format (instead of library.module.method)
    formatted_list = sorted(table_lines, key=itemgetter(0))
    for entry in formatted_list:
        args_idx = entry[0].index("(")
        path = entry[0][:args_idx]
        rest = entry[0][args_idx:]

        path = ".".join(path.split(".")[-2:])
        entry[0] = f"{path}{rest}"

    # convert jobs list into HTML table
    table_contents = tabulate(
        formatted_list,
        headers=["Aufgerufene Methode", "Zeitschema"],
        tablefmt="html",
    )

    return str(html_top + table_contents + html_bottom)


class ScheduleTable(Directive):
    def run(self):
        schedule_table_html = build_schedule_html(
            html_top='<div id="schedule_table">',
            html_bottom="</div>",
        )
        paragraph_node = nodes.raw("", schedule_table_html, format="html")

        return [paragraph_node]


def setup(app):
    app.add_directive("schedule_table", ScheduleTable)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
