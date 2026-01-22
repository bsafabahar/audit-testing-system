# Command Line Usage Guide

## Overview

This Python script queries SQL Server database and returns results as JSON. It supports a two-step workflow: first get parameter definitions, then execute the query with user-provided values.

## Prerequisites

- Python 3.8+
- Working directory: `D:\Projects\PythonAnalytics`
- Virtual environment activated (if using one)

## Command Syntax

### Step 1: Get Parameter Definitions

```bash
python query_runner.py --get-parameters
```

**Returns:** JSON with parameter definitions (no database connection required)

**Output Format:**
```json
{
  "parameters": [
    {
      "key": "startDate",
      "displayName": "تاریخ شروع",
      "type": "date",
      "required": false,
      "defaultValue": null
    },
    {
      "key": "endDate",
      "displayName": "تاریخ پایان",
      "type": "date",
      "required": false,
      "defaultValue": null
    },
    {
      "key": "accountCode",
      "displayName": "کد حساب",
      "type": "string",
      "required": false,
      "defaultValue": null
    },
    {
      "key": "limit",
      "displayName": "تعداد رکورد",
      "type": "number",
      "required": false,
      "defaultValue": 20
    }
  ]
}
```

### Step 2: Execute Query with Parameters

**PowerShell:**
```powershell
$params = '{"startDate": "2025-01-01", "endDate": "2025-12-31", "accountCode": "1001", "limit": 50}'
python query_runner.py $params
```

**CMD:**
```cmd
python query_runner.py "{\"startDate\": \"2025-01-01\", \"endDate\": \"2025-12-31\", \"accountCode\": \"1001\", \"limit\": 50}"
```

**Bash/Linux:**
```bash
python query_runner.py '{"startDate": "2025-01-01", "endDate": "2025-12-31", "accountCode": "1001", "limit": 50}'
```

## Parameter Types

### Supported Types
- `string` - Text value (e.g., "1001", "description")
- `number` - Numeric value (e.g., 50, 100.5)
- `date` - ISO date format (e.g., "2025-01-01")
- `datetime` - ISO datetime format (e.g., "2025-01-01T10:30:00")
- `boolean` - Boolean value (e.g., true, false)
- `select` - One of predefined options (e.g., "debit", "credit")

## Output Format

### Success Response

```json
{
  "parameters": [
    {
      "key": "startDate",
      "displayName": "تاریخ شروع",
      "type": "date",
      "required": false,
      "defaultValue": null
    }
  ],
  "schema": {
    "columns": [
      {
        "key": "Id",
        "displayName": "شناسه"
      },
      {
        "key": "DocumentDate",
        "displayName": "تاریخ سند"
      },
      {
        "key": "AccountCode",
        "displayName": "کد حساب"
      }
    ]
  },
  "data": [
    {
      "Id": 1,
      "DocumentDate": "2025-01-15",
      "AccountCode": "1001",
      "Debit": 1500.0,
      "Credit": 0.0
    },
    {
      "Id": 2,
      "DocumentDate": "2025-01-16",
      "AccountCode": "1001",
      "Debit": 0.0,
      "Credit": 2000.0
    }
  ]
}
```

### Error Response

```json
{
  "error": "Error message description"
}
```

## Usage Examples

### Example 1: Get Parameters Only

```powershell
python query_runner.py --get-parameters
```

Parse the returned JSON to build a UI form for users.

### Example 2: Execute with All Parameters

```powershell
$params = @{
    startDate = "2025-01-01"
    endDate = "2025-12-31"
    accountCode = "1001"
    limit = 50
} | ConvertTo-Json -Compress

python query_runner.py $params
```

### Example 3: Execute with Partial Parameters

```powershell
$params = '{"limit": 100}'
python query_runner.py $params
```

Only `limit` is provided; other parameters use their default values.

### Example 4: Execute with No Parameters

```powershell
python query_runner.py '{}'
```

All parameters use their default values.

## Integration with Other Applications

### C# / .NET

```csharp
using System.Diagnostics;
using System.Text.Json;

// Step 1: Get parameters
var getParamsProcess = new Process
{
    StartInfo = new ProcessStartInfo
    {
        FileName = "python",
        Arguments = "query_runner.py --get-parameters",
        WorkingDirectory = @"D:\Projects\PythonAnalytics",
        RedirectStandardOutput = true,
        UseShellExecute = false,
        CreateNoWindow = true
    }
};

getParamsProcess.Start();
string parametersJson = getParamsProcess.StandardOutput.ReadToEnd();
getParamsProcess.WaitForExit();

// Step 2: Execute with parameters
var parameters = new
{
    startDate = "2025-01-01",
    endDate = "2025-12-31",
    accountCode = "1001",
    limit = 50
};

string paramsJson = JsonSerializer.Serialize(parameters);

var executeProcess = new Process
{
    StartInfo = new ProcessStartInfo
    {
        FileName = "python",
        Arguments = $"query_runner.py \"{paramsJson.Replace("\"", "\\\"")}\"",
        WorkingDirectory = @"D:\Projects\PythonAnalytics",
        RedirectStandardOutput = true,
        UseShellExecute = false,
        CreateNoWindow = true
    }
};

executeProcess.Start();
string resultJson = executeProcess.StandardOutput.ReadToEnd();
executeProcess.WaitForExit();

// Parse result
var result = JsonSerializer.Deserialize<QueryResult>(resultJson);
```

### Python

```python
import subprocess
import json

# Step 1: Get parameters
result = subprocess.run(
    ['python', 'query_runner.py', '--get-parameters'],
    cwd='D:/Projects/PythonAnalytics',
    capture_output=True,
    text=True
)
parameters = json.loads(result.stdout)

# Step 2: Execute with parameters
params = {
    'startDate': '2025-01-01',
    'endDate': '2025-12-31',
    'accountCode': '1001',
    'limit': 50
}

result = subprocess.run(
    ['python', 'query_runner.py', json.dumps(params)],
    cwd='D:/Projects/PythonAnalytics',
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
```

### Node.js

```javascript
const { spawn } = require('child_process');

// Step 1: Get parameters
const getParams = spawn('python', ['query_runner.py', '--get-parameters'], {
    cwd: 'D:/Projects/PythonAnalytics'
});

let parametersOutput = '';
getParams.stdout.on('data', (data) => {
    parametersOutput += data.toString();
});

getParams.on('close', (code) => {
    const parameters = JSON.parse(parametersOutput);
    console.log('Parameters:', parameters);
});

// Step 2: Execute with parameters
const params = JSON.stringify({
    startDate: '2025-01-01',
    endDate: '2025-12-31',
    accountCode: '1001',
    limit: 50
});

const execute = spawn('python', ['query_runner.py', params], {
    cwd: 'D:/Projects/PythonAnalytics'
});

let resultOutput = '';
execute.stdout.on('data', (data) => {
    resultOutput += data.toString();
});

execute.on('close', (code) => {
    const result = JSON.parse(resultOutput);
    console.log('Result:', result);
});
```

## Exit Codes

- `0` - Success
- `1` - Error (invalid parameters, database connection failed, query error)

## Error Handling

Always check the output for an `error` property:

```javascript
const result = JSON.parse(output);
if (result.error) {
    console.error('Query failed:', result.error);
} else {
    console.log('Success:', result.data);
}
```

## Notes

- All JSON output uses UTF-8 encoding with `ensure_ascii=False` for proper Persian/Unicode character support
- Empty/null parameters are valid and will use default values
- Parameter keys are case-sensitive
- Date format must be ISO 8601: `YYYY-MM-DD`
- DateTime format must be ISO 8601: `YYYY-MM-DDTHH:MM:SS`
- Numbers can be integers or decimals
- Boolean values must be lowercase: `true` or `false`

## Troubleshooting

### Invalid JSON Parameters Error
- Ensure JSON is properly formatted
- In PowerShell, use single quotes around JSON or escape double quotes
- In CMD, escape double quotes with backslash: `\"`

### Database Connection Error
- Verify `.env` file exists and contains valid connection string
- Check network connectivity to SQL Server
- Verify SQL Server credentials

### Empty Output
- Check if query returned no results
- Verify parameter values match data in database
- Check console for error messages
