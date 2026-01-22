"""
Output formatting helpers for displaying query results.
Handles JSON and table output formatting.
"""
import json
from decimal import Decimal
from datetime import datetime, date
from typing import List, Any, Optional
import pandas as pd
from tabulate import tabulate
from types_definitions import ColumnDict, ParameterDict


# Global output format
OUTPUT_FORMAT = 'json'  # 'table' or 'json'


def json_serializer(obj: Any) -> Any:
    """
    JSON serializer for objects not serializable by default
    
    Args:
        obj: Object to serialize
        
    Returns:
        Serialized version of the object
        
    Raises:
        TypeError: If object type is not serializable
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if pd.isna(obj):
        return None
    raise TypeError(f"Type {type(obj)} not serializable")


def display_parameters_only(parameters: List[ParameterDict], schema: Optional[List[ColumnDict]] = None) -> None:
    """
    Display only parameters and schema (for --get-parameters flag)
    
    Args:
        parameters: List of parameter definitions
        schema: Optional schema definition
    """
    output: dict = {"parameters": parameters or []}
    if schema:
        output["schema"] = {"columns": schema}
    print(json.dumps(output, indent=2, ensure_ascii=False))


def display_table(
    data: List[Any],
    schema: Optional[List[ColumnDict]] = None,
    parameters: Optional[List[ParameterDict]] = None,
    headers: Optional[List[str]] = None,
    title: Optional[str] = None,
    output_format: Optional[str] = None
) -> None:
    """
    Display query results as a formatted console table or JSON
    
    Args:
        data: List of tuples or list of dictionaries containing query results
        schema: List of dicts with 'key' and 'displayName' for columns  
        parameters: List of parameter definitions
        headers: Column headers (for table output, optional)
        title: Table title (optional)
        output_format: 'table' or 'json' (if None, uses global OUTPUT_FORMAT)
    """
    format_to_use = output_format if output_format else OUTPUT_FORMAT
    
    if not data:
        if format_to_use == 'json':
            output: dict = {
                "schema": {"columns": schema or []},
                "data": []
            }
            if parameters:
                output["parameters"] = parameters
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print("No results found.")
        return
    
    if format_to_use == 'json':
        # Convert to pandas DataFrame for easier manipulation
        if schema and data:
            # Use schema keys as column names
            keys = [col['key'] for col in schema]
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
            else:
                # Map tuple data to schema keys
                df = pd.DataFrame(data, columns=keys)
            
            # Convert DataFrame to list of dicts with proper serialization
            json_data = json.loads(df.to_json(orient='records', date_format='iso', default_handler=str))
            
            # Build output with schema and data
            output = {
                "schema": {
                    "columns": schema
                },
                "data": json_data
            }
            if parameters:
                output["parameters"] = parameters
        else:
            # Fallback: no schema provided
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame(data, columns=headers if headers else None)
            
            json_data = json.loads(df.to_json(orient='records', date_format='iso', default_handler=str))
            
            # Generate schema from DataFrame columns
            auto_schema = [{"key": str(col), "displayName": str(col)} for col in df.columns]
            output = {
                "schema": {
                    "columns": auto_schema
                },
                "data": json_data
            }
            if parameters:
                output["parameters"] = parameters
        
        # Output JSON to console
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        # Display as table
        if title:
            print(f"\n{'=' * 80}")
            print(f"{title:^80}")
            print(f"{'=' * 80}")
        
        # Use display names from schema if provided
        display_headers = headers
        if schema:
            display_headers = [col['displayName'] for col in schema]
        
        print(tabulate(data, headers=display_headers, tablefmt="grid"))
        print(f"\nTotal rows: {len(data)}\n")
