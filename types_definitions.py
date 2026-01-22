"""
Type definitions for the query runner.
Provides TypedDict classes for structured data validation.
"""
from typing import TypedDict, List, Optional, Literal, Union


# Parameter Types
ParameterType = Literal['string', 'number', 'date', 'datetime', 'boolean', 'select']


class OptionDict(TypedDict):
    """Select parameter option"""
    value: Union[str, int, float]
    label: str


class ParameterDict(TypedDict, total=False):
    """Parameter definition dictionary"""
    key: str
    displayName: str
    type: ParameterType
    required: bool
    defaultValue: Optional[Union[str, int, float, bool]]
    options: List[OptionDict]  # Only for select type


# Schema Types
ColumnType = Literal['string', 'number', 'integer', 'decimal', 'date', 'datetime', 'boolean', 'currency']


class ColumnDict(TypedDict):
    """Column definition dictionary"""
    key: str
    displayName: str
    type: ColumnType


class SchemaDict(TypedDict):
    """Schema definition dictionary"""
    columns: List[ColumnDict]


# Query Definition
class QueryDefinition(TypedDict):
    """Complete query definition returned by define()"""
    parameters: List[ParameterDict]
    schema: List[ColumnDict]


# Output Types
class OutputSchema(TypedDict):
    """Output schema wrapper"""
    columns: List[ColumnDict]


class QueryOutput(TypedDict, total=False):
    """Complete query output JSON"""
    schema: OutputSchema
    data: List[dict]
    parameters: List[ParameterDict]


class ErrorOutput(TypedDict):
    """Error output JSON"""
    error: str


# Input Types
InputValue = Union[str, int, float, bool, None]
ParametersInput = dict[str, InputValue]
