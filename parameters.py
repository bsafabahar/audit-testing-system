"""
Parameter definition helpers for query input parameters.
Provides classes and helper functions to define query parameters.
"""
from typing import List, Optional, Union
from types_definitions import ParameterDict, OptionDict


class Parameter:
    """Base class for parameter definitions"""
    
    def __init__(
        self, 
        key: str, 
        display_name: str, 
        required: bool = False, 
        default_value: Optional[Union[str, int, float, bool]] = None
    ) -> None:
        self.key = key
        self.display_name = display_name
        self.required = required
        self.default_value = default_value
    
    def to_dict(self) -> ParameterDict:
        """Convert parameter to dictionary"""
        return {
            'key': self.key,
            'displayName': self.display_name,
            'type': self.get_type(),
            'required': self.required,
            'defaultValue': self.default_value
        }
    
    def get_type(self) -> str:
        """Get parameter type (override in subclasses)"""
        return 'string'


class StringParameter(Parameter):
    """String parameter"""
    def get_type(self) -> str:
        return 'string'


class NumberParameter(Parameter):
    """Number parameter"""
    def get_type(self) -> str:
        return 'number'


class DateParameter(Parameter):
    """Date parameter"""
    def get_type(self) -> str:
        return 'date'


class DateTimeParameter(Parameter):
    """DateTime parameter"""
    def get_type(self) -> str:
        return 'datetime'


class BooleanParameter(Parameter):
    """Boolean parameter"""
    def get_type(self) -> str:
        return 'boolean'


class SelectParameter(Parameter):
    """Select/dropdown parameter with options"""
    
    def __init__(
        self, 
        key: str, 
        display_name: str, 
        options: List[OptionDict], 
        required: bool = False, 
        default_value: Optional[Union[str, int, float]] = None
    ) -> None:
        super().__init__(key, display_name, required, default_value)
        self.options = options
    
    def get_type(self) -> str:
        return 'select'
    
    def to_dict(self) -> ParameterDict:
        """Convert parameter to dictionary with options"""
        result = super().to_dict()
        result['options'] = self.options
        return result


# Helper functions for easier parameter creation

def param_string(
    key: str, 
    display_name: str, 
    required: bool = False, 
    default_value: Optional[str] = None
) -> ParameterDict:
    """Create a string parameter"""
    return StringParameter(key, display_name, required, default_value).to_dict()


def param_number(
    key: str, 
    display_name: str, 
    required: bool = False, 
    default_value: Optional[Union[int, float]] = None
) -> ParameterDict:
    """Create a number parameter"""
    return NumberParameter(key, display_name, required, default_value).to_dict()


def param_date(
    key: str, 
    display_name: str, 
    required: bool = False, 
    default_value: Optional[str] = None
) -> ParameterDict:
    """Create a date parameter"""
    return DateParameter(key, display_name, required, default_value).to_dict()


def param_datetime(
    key: str, 
    display_name: str, 
    required: bool = False, 
    default_value: Optional[str] = None
) -> ParameterDict:
    """Create a datetime parameter"""
    return DateTimeParameter(key, display_name, required, default_value).to_dict()


def param_boolean(
    key: str, 
    display_name: str, 
    required: bool = False, 
    default_value: bool = False
) -> ParameterDict:
    """Create a boolean parameter"""
    return BooleanParameter(key, display_name, required, default_value).to_dict()


def param_select(
    key: str, 
    display_name: str, 
    options: List[OptionDict], 
    required: bool = False, 
    default_value: Optional[Union[str, int, float]] = None
) -> ParameterDict:
    """
    Create a select/dropdown parameter
    
    Args:
        key: Parameter key
        display_name: Display name
        options: List of dicts with 'value' and 'label' keys
        required: Whether parameter is required
        default_value: Default value
    """
    return SelectParameter(key, display_name, options, required, default_value).to_dict()


def option(value: Union[str, int, float], label: str) -> OptionDict:
    """Helper to create an option for select parameters"""
    return {'value': value, 'label': label}

