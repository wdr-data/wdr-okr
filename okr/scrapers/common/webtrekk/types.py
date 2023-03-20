"""Classes for requesting custom analyses through Webtrekk's "getAnalysisData"
method."""

from typing import (
    Any,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)
from dataclasses import dataclass
import datetime as dt

import inflection

from okr.scrapers.common.types import JSON


class WebtrekkType:
    """Base class for dataclasses for requesting custom analyses. Converts
    types of all values in dict to correct JSON string format.
    """

    @classmethod
    def _format_value(cls, value: Any) -> JSON:
        if isinstance(value, str):
            return value

        elif isinstance(value, WebtrekkType):
            return dict(value)

        elif isinstance(value, dt.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")

        elif isinstance(value, dt.date):
            return value.isoformat()

        elif isinstance(value, bool):
            return 1 if value else 0

        elif isinstance(value, Iterable):
            return [cls._format_value(item) for item in value]

        return str(value)

    def __iter__(self) -> Tuple[str, JSON]:
        for key, value in self.__dict__.items():
            if value is None:
                continue

            key = inflection.camelize(key, uppercase_first_letter=False)
            value = self.__class__._format_value(value)

            yield key, value


AnalysisComparator = Literal["=", "!="]
MetricComparator = Literal["=", "<", ">", "between"]


@dataclass
class AnalysisObject(WebtrekkType):
    """Class reflecting "analysisObject" of Webtrekk API."""

    title: str
    sort_order: Optional[Literal["asc", "desc", ""]] = None
    alias: Optional[str] = None
    row_limit: Optional[int] = None


@dataclass
class FilterRule(WebtrekkType):
    """Class reflecting "filterRule" of Webtrekk API."""

    object_title: str
    comparator: Union[AnalysisComparator, MetricComparator]
    filter: str
    filter2: Optional[str] = None
    link: Optional[Literal["and", "or", ""]] = None
    case_sens: Optional[bool] = None
    scope: Optional[Literal["visitor", "visit", "page", "action", ""]] = None


@dataclass
class Filter(WebtrekkType):
    """Class reflecting "filter" of Webtrekk API."""

    filter_rules: List[FilterRule]


@dataclass
class Metric(WebtrekkType):
    """Class reflecting "metric" of Webtrekk API."""

    title: str
    sort_order: Optional[Literal["asc", "desc", ""]] = None
    metric_filter: Optional[Filter] = None
    object_scope: Optional[bool] = None


@dataclass
class AnalysisConfig(WebtrekkType):
    """Class reflecting "analysisConfig" of Webtrekk API."""

    analysis_objects: List[AnalysisObject]
    metrics: Optional[List[Metric]] = None
    analysis_filter: Optional[Filter] = None
    start_time: Optional[Union[dt.date, dt.datetime]] = None
    stop_time: Optional[Union[dt.date, dt.datetime]] = None
    start_row: Optional[int] = None
    row_limit: Optional[int] = None
    hide_footers: Optional[bool] = None
    footer_identifier: Optional[str] = None
    force_raw_data: Optional[bool] = None
    scope: Optional[Literal["auto", "visit", "strong"]] = None
