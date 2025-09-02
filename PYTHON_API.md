# MerlinDB Python API

MerlinDB provides both CLI and programmatic Python interfaces for working with Microsoft Access Database (.mdb) files used by GeniSys lighting control software.

## Installation

```bash
pip install merlin-db
# or with uv
uv add merlin-db
```

## Quick Start

### Basic Usage

```python
import merlindb

# Load a database
db = merlindb.load_database("database.mdb")

# List all tables
tables = db.list_tables()
print(f"Found {len(tables)} tables: {tables[:5]}...")

# Get data from a specific table
config_data = db.get_table("Config")
print(f"Config table has {len(config_data)} columns")

# Export all tables to JSON
result = db.export_json("output.json")
print(f"Exported {result['tables_exported']} tables")
```

### Context Manager Usage

```python
import merlindb

# Automatic cleanup with context manager
with merlindb.load_database("database.mdb") as db:
    tables = db.list_tables()
    config = db.get_table("Config")
    db.export_json("all_data.json")
```

## API Reference

### Main Classes

#### `MerlinDB`

The main interface for working with MDB files.

```python
# Initialize
db = merlindb.MerlinDB("database.mdb")
# or
db = merlindb.load_database("database.mdb")
```

**Methods:**

- `list_tables() -> list[str]` - Get all table names
- `get_table(table_name, validate=False) -> dict` - Get table data
- `table_exists(table_name) -> bool` - Check if table exists
- `get_table_info(table_name) -> dict` - Get table metadata
- `get_database_summary() -> dict` - Get database overview

**Export Methods:**

- `export_json(output_path, tables=None, separate_files=False)`
- `export_yaml(output_path, tables=None, separate_files=False)`
- `export_csv(output_path, tables=None, separate_files=False)`
- `export(output_path, format="json", tables=None, separate_files=False)`

### Data Access Examples

#### Working with Tables

```python
import merlindb

db = merlindb.load_database("database.mdb")

# Check if table exists
if db.table_exists("Config"):
    # Get raw data
    config_data = db.get_table("Config")
    print(f"Columns: {list(config_data.keys())}")
    
    # Get validated data (if Pydantic model exists)
    validated_data = db.get_table("Config", validate=True)
    
    # Get table metadata
    info = db.get_table_info("Config")
    print(f"Table has {info['record_count']} records")
```

#### Database Summary

```python
import merlindb

db = merlindb.load_database("database.mdb")
summary = db.get_database_summary()

print(f"""
Database Summary:
- File: {summary['file_path']}
- Total Tables: {summary['total_tables']}
- Tables with Data: {summary['tables_with_data']}
- Total Records: {summary['total_records']}
- Pydantic Model Coverage: {summary['model_coverage']}
""")
```

### Export Examples

#### JSON Export

```python
import merlindb

db = merlindb.load_database("database.mdb")

# Export all tables to single JSON file
result = db.export_json("all_data.json")

# Export specific tables
result = db.export_json("config_data.json", tables=["Config", "Events"])

# Export to separate files per table
result = db.export_json("data.json", separate_files=True)

# Export with wildcards
result = db.export_json("genisys_data.json", tables=["GeniSys*"])

print(f"Export result: {result}")
```

#### YAML Export

```python
import merlindb

db = merlindb.load_database("database.mdb")

# Export to YAML format
result = db.export_yaml("data.yaml")

# Export specific tables with patterns
result = db.export_yaml("lighting.yaml", tables=["*Light*", "Area*"])
```

#### CSV Export

```python
import merlindb

db = merlindb.load_database("database.mdb")

# Export single table to CSV
result = db.export_csv("config.csv", tables=["Config"])

# Export all tables to separate CSV files
result = db.export_csv("data.csv", separate_files=True)
```

### Convenience Functions

#### Quick Operations

```python
import merlindb

# Quick table listing
tables = merlindb.list_tables("database.mdb")

# Quick database info
info = merlindb.get_database_info("database.mdb")

# Quick export
result = merlindb.quick_export(
    "database.mdb", 
    "output.json", 
    format="json",
    tables=["Config", "Events"]
)
```

## Advanced Usage

### Data Processing

```python
import merlindb
import pandas as pd

db = merlindb.load_database("database.mdb")

# Get table data and convert to DataFrame
config_data = db.get_table("Config")
if config_data:
    # Convert column-based data to records
    columns = list(config_data.keys())
    records = []
    if columns:
        for i in range(len(config_data[columns[0]])):
            record = {col: config_data[col][i] for col in columns}
            records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    print(df.head())
```

### Error Handling

```python
import merlindb

try:
    db = merlindb.load_database("database.mdb")
except FileNotFoundError:
    print("Database file not found")
except ValueError as e:
    print(f"Failed to load database: {e}")

try:
    data = db.get_table("NonExistentTable")
except ValueError as e:
    print(f"Table error: {e}")
```

### Batch Processing

```python
import merlindb
from pathlib import Path

# Process multiple MDB files
mdb_files = Path(".").glob("*.mdb")

for mdb_file in mdb_files:
    try:
        with merlindb.load_database(mdb_file) as db:
            summary = db.get_database_summary()
            print(f"{mdb_file.name}: {summary['total_tables']} tables, {summary['total_records']} records")
            
            # Export each database
            output_file = f"{mdb_file.stem}_export.json"
            db.export_json(output_file)
            
    except Exception as e:
        print(f"Error processing {mdb_file}: {e}")
```

## Data Validation

MerlinDB includes Pydantic models for data validation:

```python
import merlindb

db = merlindb.load_database("database.mdb")

# Check which tables have validation models
for table_name in db.list_tables():
    info = db.get_table_info(table_name)
    if info['has_pydantic_model']:
        print(f"✓ {table_name} - has validation model")
        
        # Get validated data
        try:
            validated_data = db.get_table(table_name, validate=True)
            print(f"  Validated {info['record_count']} records")
        except Exception as e:
            print(f"  Validation error: {e}")
```

## Performance Considerations

### Large Databases

```python
import merlindb

# For large databases, use table filtering
db = merlindb.load_database("large_database.mdb")

# Export only specific tables to reduce memory usage
critical_tables = ["Config", "Events", "Schedules"]
db.export_json("critical_data.json", tables=critical_tables)

# Use separate files for large exports
db.export_json("all_data.json", separate_files=True)
```

### Memory Management

```python
import merlindb

# Use context managers for automatic cleanup
with merlindb.load_database("database.mdb") as db:
    # Process data within context
    for table_name in db.list_tables()[:10]:  # Limit processing
        try:
            data = db.get_table(table_name)
            # Process data immediately, don't store all in memory
            print(f"Processed {table_name}")
        except Exception as e:
            print(f"Skipped {table_name}: {e}")
# Database automatically cleaned up here
```

## Integration Examples

### Web API Integration

```python
from flask import Flask, jsonify
import merlindb

app = Flask(__name__)

@app.route("/api/tables")
def list_database_tables():
    try:
        tables = merlindb.list_tables("database.mdb")
        return jsonify({"tables": tables})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/table/<table_name>")
def get_table_data(table_name):
    try:
        with merlindb.load_database("database.mdb") as db:
            data = db.get_table(table_name, validate=True)
            return jsonify({"table": table_name, "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Data Analysis Workflow

```python
import merlindb
import pandas as pd
import matplotlib.pyplot as plt

# Load and analyze lighting data
with merlindb.load_database("lighting_system.mdb") as db:
    # Get area configuration
    areas = db.get_table("AreaNames")
    
    # Get lighting levels
    levels = db.get_table("AreaChannelLoads")
    
    # Convert to DataFrames for analysis
    areas_df = pd.DataFrame([
        {col: areas[col][i] for col in areas.keys()}
        for i in range(len(areas[list(areas.keys())[0]]))
    ])
    
    # Perform analysis
    print(f"Total areas: {len(areas_df)}")
    print("Area distribution:", areas_df['Area'].value_counts())
```

## Error Reference

Common exceptions and their meanings:

- `FileNotFoundError`: MDB file doesn't exist
- `ValueError`: Invalid table name, format, or database corruption
- `ImportError`: Missing optional dependencies
- `PermissionError`: File access denied

## See Also

- [CLI Documentation](README.md) - Command-line interface
- [API Reference](src/merlindb/api.py) - Full API source
- [Examples](examples/) - More usage examples