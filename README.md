# Python Analytics - SQL Server Query Runner

A clean, structured Python application for executing queries against SQL Server databases with parameter support, schema definitions, and JSON output.

## 🏗️ Architecture

The project follows a modular architecture with clear separation of concerns:

```
PythonAnalytics/
├── query_runner.py          # Main entry point - handles query execution
├── database.py              # Database connection with read-only sessions
├── parameters.py            # Parameter definition classes and helpers
├── schema.py                # Schema/column definition classes and helpers
├── output.py                # Output formatting (JSON/table)
├── models.py                # SQLAlchemy ORM models
├── config.py                # Configuration management
├── queries/                 # User-defined query modules
│   ├── __init__.py
│   └── get_transactions_summary.py
├── .env                     # Database connection (gitignored)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd PythonAnalytics

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```env
CONNECTION_STRING=mssql+pyodbc://username:password@server:port/database?driver=ODBC+Driver+17+for+SQL+Server
```

### 3. Run Queries

```bash
# List available queries
python query_runner.py --list-queries

# Get query parameters and schema
python query_runner.py --query get_transactions_summary --get-parameters

# Execute query
python query_runner.py --query get_transactions_summary

# Execute query with parameters
python query_runner.py --query get_transactions_summary '{"limit": 10, "startDate": "2024-01-01"}'
```

## 📝 Creating Queries

Queries are Python modules in the `queries/` folder. Each query module must have two functions:

### 1. `define()` - Define parameters and schema

Returns a dictionary with `parameters` and `schema` keys:

```python
from parameters import param_date, param_string, param_number
from schema import col, schema

def define():
    """Define parameters and schema"""
    parameters = [
        param_date('startDate', 'Start Date'),
        param_date('endDate', 'End Date'),
        param_string('accountCode', 'Account Code'),
        param_number('limit', 'Record Limit', default_value=20)
    ]
    
    result_schema = schema(
        col('Id', 'ID', 'integer'),
        col('Date', 'Date', 'date'),
        col('Amount', 'Amount', 'currency'),
        col('Description', 'Description', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }
```

### 2. `execute(session)` - Execute query and return data

Receives a read-only session and returns data as list of dictionaries:

```python
from models import Transaction
from query_runner import get_parameter

def execute(session):
    """Execute query and return data"""
    # Get input parameters
    limit = get_parameter('limit', 20)
    start_date = get_parameter('startDate')
    
    # Build and execute query
    query = session.query(Transaction)
    if start_date:
        query = query.filter(Transaction.DocumentDate >= start_date)
    
    results = query.limit(limit).all()
    
    # Return data as list of dictionaries
    data = []
    for t in results:
        row = {
            'Id': t.Id,
            'Date': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
            'Amount': float(t.Amount) if t.Amount else 0.0,
            'Description': t.Description
        }
        data.append(row)
    
    return data
```

See `CLI_USAGE.md` and `parameter_helpers_guide.md` for complete documentation.

## 🔧 Core Modules

### parameters.py

Defines query input parameters:

- `param_string(key, display_name, required, default_value)`
- `param_number(key, display_name, required, default_value)`
- `param_date(key, display_name, required, default_value)`
- `param_datetime(key, display_name, required, default_value)`
- `param_boolean(key, display_name, default_value)`
- `param_select(key, display_name, options, required, default_value)`

### schema.py

Defines result column schema:

- `col(key, display_name, col_type)` - Define a column
- `schema(*columns)` - Create schema from multiple columns

**Supported types:** `string`, `number`, `integer`, `decimal`, `date`, `datetime`, `boolean`, `currency`

### database.py

Manages database connections with **read-only sessions**:

- Sessions wrapped in `ReadOnlySession` class
- Only SELECT queries allowed
- Write operations raise `PermissionError`
- Runner manages session lifecycle

### output.py

Handles output formatting:

- JSON format with schema, parameters, and data
- Table format for console (optional)
- Automatic data type serialization

## 🔐 Security

- **Read-Only Sessions**: All query sessions are read-only by design
- **No Direct Database Access**: Users never manage sessions directly  
- **Parameter Validation**: Input parameters validated before execution
- **Connection String**: Stored in `.env` file (not committed to git)

## 📊 JSON Output Format

```json
{
  "schema": {
    "columns": [
      {"key": "Id", "displayName": "ID", "type": "integer"},
      {"key": "Amount", "displayName": "Amount", "type": "currency"}
    ]
  },
  "data": [
    {"Id": 1, "Amount": 1000.00}
  ],
  "parameters": [
    {
      "key": "limit",
      "displayName": "Record Limit",
      "type": "number",
      "required": false,
      "defaultValue": 20
    }
  ]
}
```

## 🛠️ How It Works

### Two-Step Workflow

1. **Get Parameters** (`--get-parameters`):
   - Frontend calls with `--get-parameters` flag
   - Runner calls `define()` function
   - Returns parameters and schema for UI generation
   - No database connection needed

2. **Execute Query**:
   - Frontend sends query name + parameter values
   - Runner calls `define()` to get schema
   - Runner creates read-only session
   - Runner calls `execute(session)` to get data
   - Runner formats output with schema + parameters
   - Runner closes session automatically

### Execution Flow

```
User Request → query_runner.py
    ↓
Load query module from queries/
    ↓
Call define() → Get parameters & schema
    ↓
[If --get-parameters: display and exit]
    ↓
Create read-only session
    ↓
Call execute(session) → Get data
    ↓
Format output (output.py)
    ↓
Display JSON result
    ↓
Close session automatically
```

## 🎯 Benefits

- **Clean Architecture**: Separated concerns
- **Easy to Use**: Simple API for query authors
- **Type Safety**: Strongly typed parameters and columns
- **Security**: Read-only sessions prevent data modification
- **Automatic Session Management**: No manual session handling
- **JSON Output**: Perfect for frontend integration
- **Multi-language Support**: Display names in any language

## 📦 Dependencies

- `sqlalchemy>=2.0.0` - ORM and database toolkit
- `pyodbc>=5.0.0` - SQL Server ODBC driver
- `python-dotenv>=1.0.0` - Environment variable management
- `pandas>=2.0.0` - Data manipulation
- `tabulate>=0.9.0` - Table formatting

## 🤝 Contributing

To add a new query:

1. Create file in `queries/` folder (e.g., `my_query.py`)
2. Implement `define()` function to define parameters and schema
3. Implement `execute(session)` function to query and return data
4. Test: `python query_runner.py --query my_query --get-parameters`
5. Run: `python query_runner.py --query my_query`

## 📄 License

MIT License - Feel free to use and modify as needed.

### Module Import Errors

```bash
pip install -r requirements.txt --upgrade
```

## 📋 Available Audit Tests

This system includes **69 comprehensive audit tests** organized into 23 categories. For a complete list:

- **[لیست آزمون‌های حسابرسی (Persian)](./لیست_آزمون‌های_حسابرسی.md)** - Complete documentation in Persian
- **[Test List Summary (English)](./TEST_LIST_SUMMARY.md)** - Quick reference guide

Categories include: Benford's Law, Threshold Analysis, Duplicate Detection, Statistical Tests, Fraud Detection, AI/ML Tests, and many more.

## 🤖 AI-Powered Test Generator

The system now includes an intelligent test generator that automatically creates audit test files using AI (OpenAI GPT or Anthropic Claude).

### Features:
- 🚀 Automatic Python code generation
- 📋 Follows project standards and conventions
- 🔧 Supports OpenAI (GPT-4, GPT-3.5) and Anthropic (Claude)
- 💾 Automatic saving to queries folder
- 🌐 User-friendly Persian interface

### Quick Start:
1. Access the test generator from the main page (🤖 آزمون‌ساز button)
2. Describe your test requirements in Persian or English
3. Select AI provider and enter your API key
4. Click generate and the test file will be created automatically

For detailed instructions, see **[Test Generator Guide](./TEST_GENERATOR_GUIDE.md)**

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PyODBC Documentation](https://github.com/mkleehammer/pyodbc/wiki)
- [Tabulate Documentation](https://github.com/astanin/python-tabulate)

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Feel free to add your own query functions and enhance the project as needed!
