"""Provide some custom types."""

from typing import Any, List, Mapping, Union

# Source for custom JSON-Type:
# https://gist.github.com/BMDan/ede923f733dfdf5ed3f6c9634a3e281f

# Values for JSON that aren't nested
JSON_v = Union[str, int, float, bool, None]

# If MyPy ever permits recursive definitions, just uncomment this:
# JSON = Union[List['JSON'], Mapping[str, 'JSON'], JSON_v]

# Until then, here's a multi-layer way to represent any (reasonable) JSON we
# might send or receive.  It terminates at JSON_4, so the maximum depth of
# the JSON is 5 dicts/lists, like: {'a': {'b': {'c': {'d': {'e': 'f'}}}}}.

JSON_5 = JSON_v
JSON_4 = Union[JSON_v, List[JSON_5], Mapping[str, JSON_5]]
JSON_3 = Union[JSON_v, List[JSON_4], Mapping[str, JSON_4]]
JSON_2 = Union[JSON_v, List[JSON_3], Mapping[str, JSON_3]]
JSON_1 = Union[JSON_v, List[JSON_2], Mapping[str, JSON_2]]
JSON = Union[JSON_v, List[JSON_1], Mapping[str, JSON_1]]

# To allow deeper nesting, you can of course expand the JSON definition above,
# or you can keep typechecking for the first levels but skip typechecking
# at the deepest levels by using UnsafeJSON:

UnsafeJSON_5 = Union[JSON_v, List[Any], Mapping[str, Any]]
UnsafeJSON_4 = Union[JSON_v, List[UnsafeJSON_5], Mapping[str, UnsafeJSON_5]]
UnsafeJSON_3 = Union[JSON_v, List[UnsafeJSON_4], Mapping[str, UnsafeJSON_4]]
UnsafeJSON_2 = Union[JSON_v, List[UnsafeJSON_3], Mapping[str, UnsafeJSON_3]]
UnsafeJSON_1 = Union[JSON_v, List[UnsafeJSON_2], Mapping[str, UnsafeJSON_2]]
UnsafeJSON = Union[JSON_v, List[UnsafeJSON_1], Mapping[str, UnsafeJSON_1]]
