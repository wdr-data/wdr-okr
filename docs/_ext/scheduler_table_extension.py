"""Custom Sphinx extension to inject the APScheduler's schedule into a ReST document."""

import inspect
import os
import pathlib
import sys

import django

from docutils import nodes
from docutils.parsers.rst import Directive
from operator import itemgetter

from apscheduler.job import Job
from tabulate import tabulate


CURRENT_DIR = pathlib.Path(__file__).parent.absolute()
BASE_DIR = str(CURRENT_DIR.parents[1].absolute())

sys.path.insert(0, BASE_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from okr.scrapers import scheduler


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


def parse_job_info_schedule(job: Job) -> str:
    """Parse information about scheduled time in Job object for further processing.

    Args:
        job (Job): Job object to parse

    Raises:
        NotImplementedError: So far, only daily intervals with hours and minute
            information are used. Other intervals are not yet supported.
        ValueError: Every Job object's trigger must contain at least hour and minute
            information to be valid.

    Returns:
        str: Parsed method information based on Job object.
    """

    # convert trigger objects into lists
    days = str(job.trigger.fields[-4]).split(",")
    hours = str(job.trigger.fields[-3]).split(",")
    minutes = str(job.trigger.fields[-2]).split(",")
    seconds = str(job.trigger.fields[-1]).split(",")

    scheduled_times = ""

    if days == ["*"]:
        scheduled_times += "Jeden Tag"
    else:
        raise NotImplementedError(
            f"Parsing for individual days not yet implemented {job.trigger}!"
        )

    if len(minutes) == 1 and minutes != ["*"]:
        minutes_formatted = minutes[0].zfill(2)
    elif len(minutes) > 1:
        minutes_formatted = ", ".join(minutes[:-1]) + " und " + minutes[-1]
    elif minutes == ["*"]:
        raise NotImplementedError(
            f"Parsing for intervals of seconds not yet implemented {job.trigger}!"
        )
    else:
        raise ValueError(f"Trigger does not contain minute information {job.trigger}!")

    if hours == ["*"]:
        scheduled_times += (
            f", jeweils {minutes_formatted} Minuten nach jeder vollen Stunde"
        )
    elif len(hours) == 1:
        if len(minutes) == 1:
            scheduled_times += f" um {hours[0].zfill(2)}:{minutes_formatted} Uhr"
        elif len(minutes) > 1:
            minutes_list = []
            for minute in minutes:
                minutes_list.append(f"{hours[0].zfill(2)}:{minute.zfill(2)}")
            scheduled_times += f" um "
            scheduled_times += ", ".join(minutes_list[:-1])
            scheduled_times += f" und {minutes_list[-1]} Uhr"
    elif len(hours) > 1:
        if len(minutes) == 1:
            hours_list = []
            for hour in hours:
                hours_list.append(f"{hour.zfill(2)}:{minutes_formatted}")
            scheduled_times += " um "
            scheduled_times += ", ".join(hours_list[:-1])
            scheduled_times += f" und {hours_list[-1]} Uhr"
        elif len(minutes) > 1:
            hours_minutes_list = []
            for hour in hours:
                for minute in minutes:
                    hours_minutes_list.append(f"{hour.zfill(2)}:{minute.zfill(2)}")
            scheduled_times += " um "
            scheduled_times += ", ".join(hours_minutes_list[:-1])
            scheduled_times += f" und {hours_minutes_list[-1]} Uhr"
    else:
        raise ValueError(f"Trigger does not contain hour information {job.trigger}!")

    return scheduled_times


def build_schedule_html(html_top: str = "<div>", html_bottom: str = "</div>") -> str:
    """Create a basic HTML table with the currently scheduled jobs.

    Args:
        html_top (str, optional): HTML to go before the table. Defaults to "<div>".
        html_bottom (str, optional): HTML to go at hte end of the table. Defaults to
        "</div>".

    Returns:
        str: HTML code.
    """

    # make sure DEBUG is off and retrieve scheduled jobs from okr/scrapers/scheduler.py
    debug_original = django.conf.settings.DEBUG
    django.conf.settings.DEBUG = False
    jobs_list = scheduler.start()
    django.conf.settings.DEBUG = debug_original

    # parse and convert job information into list
    table_lines = []
    for job in jobs_list:
        table_lines.append([parse_job_info_method(job), parse_job_info_schedule(job)])

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
