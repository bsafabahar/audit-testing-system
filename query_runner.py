"""
Query Runner Script
Execute database queries and display results as console tables or JSON.

This is your main script to run queries against your SQL Server database.
"""
import json
import sys
import argparse
from typing import Tuple, Any, Optional, Dict
from database import get_db, db
from output import display_table, display_parameters_only

# Input parameters passed from command line (as JSON string)
INPUT_PARAMETERS: Optional[Dict[str, Any]] = None


def parse_arguments() -> Tuple[str, bool]:
    """
    Parse command line arguments
    
    Returns:
        tuple: (query_name, get_parameters_only)
    """
    global INPUT_PARAMETERS
    
    parser = argparse.ArgumentParser(description='SQL Server Query Runner')
    parser.add_argument('--get-parameters', action='store_true', 
                       help='Get parameter definitions only (for UI generation)')
    parser.add_argument('--query', type=str, default='get_transactions_summary',
                       help='Query name to execute (filename without .py)')
    parser.add_argument('--list-queries', action='store_true',
                       help='List all available queries')
    parser.add_argument('params', nargs='?', default=None,
                       help='JSON string with parameter values')
    
    args = parser.parse_args()
    
    get_parameters_only = args.get_parameters
    
    # Handle list queries
    if args.list_queries:
        list_available_queries()
        sys.exit(0)
    
    if args.params and not get_parameters_only:
        try:
            INPUT_PARAMETERS = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON parameters: {e}"}, ensure_ascii=False))
            sys.exit(1)
    else:
        INPUT_PARAMETERS = {}
    
    return args.query, get_parameters_only


def get_parameter(key: str, default: Any = None) -> Any:
    """
    Get a parameter value by key
    
    Args:
        key: Parameter key to retrieve
        default: Default value if parameter not found
        
    Returns:
        Parameter value or default
    """
    return INPUT_PARAMETERS.get(key, default) if INPUT_PARAMETERS else default


def list_available_queries() -> None:
    """
    List all available query files in the queries folder
    """
    import os
    
    queries_dir = os.path.join(os.path.dirname(__file__), 'queries')
    
    if not os.path.exists(queries_dir):
        print(json.dumps({"queries": []}, ensure_ascii=False))
        return
    
    queries = []
    for file in os.listdir(queries_dir):
        if file.endswith('.py') and not file.startswith('__'):
            query_name = file[:-3]  # Remove .py extension
            queries.append({
                'name': query_name,
                'file': file
            })
    
    print(json.dumps({"queries": queries}, indent=2, ensure_ascii=False))


def load_and_execute_query(query_name: str, get_parameters_only: bool = False) -> None:
    """
    Dynamically load and execute a query from the queries folder
    
    Args:
        query_name: Name of the query file (without .py extension)
        get_parameters_only: If True, only return parameter definitions
    """
    import os
    import importlib.util
    
    queries_dir = os.path.join(os.path.dirname(__file__), 'queries')
    query_file = os.path.join(queries_dir, f'{query_name}.py')
    
    if not os.path.exists(query_file):
        print(json.dumps({
            "error": f"Query '{query_name}' not found. Use --list-queries to see available queries."
        }, ensure_ascii=False))
        sys.exit(1)
    
    try:
        # Load the query module dynamically
        spec = importlib.util.spec_from_file_location(query_name, query_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module spec for {query_name}")
            
        query_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(query_module)
        
        # Get definitions from the module
        definitions = None
        if hasattr(query_module, 'define'):
            definitions = query_module.define()
        
        # If only getting parameters, display and exit
        if get_parameters_only:
            if definitions:
                display_parameters_only(definitions.get('parameters'), definitions.get('schema'))
            else:
                print(json.dumps({"parameters": [], "schema": {"columns": []}}, ensure_ascii=False))
        else:
            # Execute the query
            if hasattr(query_module, 'execute'):
                # Create session and pass to execute
                session = get_db()
                try:
                    # Execute returns data only
                    data = query_module.execute(session)
                    
                    # Runner handles display with schema and parameters from define()
                    display_table(
                        data,
                        schema=definitions.get('schema') if definitions else None,
                        parameters=definitions.get('parameters') if definitions else None
                    )
                except Exception as e:
                    print(json.dumps({"error": str(e)}, ensure_ascii=False))
                finally:
                    session.close()
            else:
                print(json.dumps({
                    "error": f"Query '{query_name}' does not have an execute() function."
                }, ensure_ascii=False))
                sys.exit(1)
            
    except Exception as e:
        print(json.dumps({
            "error": f"Error loading or executing query '{query_name}': {str(e)}"
        }, ensure_ascii=False))
        sys.exit(1)


def main() -> None:
    """
    Main function - Entry point for the script
    """
    # Parse command line arguments and get query name
    query_name, get_parameters_only = parse_arguments()
    
    # If only getting parameters, skip connection test
    if not get_parameters_only:
        # Test database connection first
        if not db.test_connection():
            print(json.dumps({"error": "Cannot connect to database"}, indent=2, ensure_ascii=False))
            return
    
    # Load and execute the specified query
    load_and_execute_query(query_name, get_parameters_only)


if __name__ == "__main__":
    """
    Script entry point
    Run this file directly: python query_runner.py
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
