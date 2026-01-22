"""
Schema definition helpers for query result columns.
Provides classes and helper functions to define result schema.
"""
from typing import List
from types_definitions import ColumnDict, ColumnType


class Column:
    """Column definition for result schema"""
    
    def __init__(self, key: str, display_name: str, col_type: ColumnType = 'string') -> None:
        """
        Initialize column definition
        
        Args:
            key: Column key (matches data key)
            display_name: Display name for the column
            col_type: Data type (string, number, integer, decimal, date, datetime, boolean, currency)
        """
        self.key = key
        self.display_name = display_name
        self.col_type = col_type
    
    def to_dict(self) -> ColumnDict:
        """Convert column to dictionary"""
        return {
            'key': self.key,
            'displayName': self.display_name,
            'type': self.col_type
        }


class Schema:
    """Schema definition for query results"""
    
    def __init__(self, *columns: ColumnDict) -> None:
        """
        Initialize schema with columns
        
        Args:
            *columns: Variable number of Column dictionaries
        """
        self.columns = columns
    
    def to_list(self) -> List[ColumnDict]:
        """Convert schema to list of column dictionaries"""
        return list(self.columns)


# Helper functions for easier schema creation

def col(key: str, display_name: str, col_type: ColumnType = 'string') -> ColumnDict:
    """
    Create a column definition
    
    Args:
        key: Column key (matches data key)
        display_name: Display name for the column
        col_type: Data type (default: 'string')
                  Supported: 'string', 'number', 'integer', 'decimal', 
                            'date', 'datetime', 'boolean', 'currency'
    
    Returns:
        dict: Column definition
    """
    return Column(key, display_name, col_type).to_dict()


def schema(*columns: ColumnDict) -> List[ColumnDict]:
    """
    Create a schema from multiple columns
    
    Args:
        *columns: Variable number of column definitions (from col() function)
    
    Returns:
        list: Schema definition (list of column dicts)
    
    Example:
        schema(
            col('Id', 'شناسه', 'integer'),
            col('Name', 'نام', 'string'),
            col('Amount', 'مبلغ', 'currency'),
            col('Date', 'تاریخ', 'date')
        )
    """
    return list(columns)

