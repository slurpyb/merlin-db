#!/usr/bin/env python3
"""Example usage of the MerlinDB Python API."""

import merlindb
from pathlib import Path


def main():
    """Demonstrate MerlinDB API usage."""
    # Replace with path to your MDB file
    mdb_file = "test.mdb"
    
    if not Path(mdb_file).exists():
        print(f"❌ MDB file '{mdb_file}' not found")
        print("Please update the mdb_file variable with the path to your MDB file")
        return
    
    print("🔍 Loading MerlinDB...")
    
    # Method 1: Direct class instantiation
    db = merlindb.MerlinDB(mdb_file)
    
    # Method 2: Convenience function (equivalent)
    # db = merlindb.load_database(mdb_file)
    
    # Method 3: Context manager (automatically handles cleanup)
    # with merlindb.load_database(mdb_file) as db:
    #     # work with db here
    #     pass
    
    print(f"✅ Loaded database: {db}")
    
    # Get database summary
    print("\n📊 Database Summary:")
    summary = db.get_database_summary()
    print(f"   File: {summary['file_path']}")
    print(f"   Total Tables: {summary['total_tables']}")
    print(f"   Tables with Data: {summary['tables_with_data']}")
    print(f"   Total Records: {summary['total_records']:,}")
    print(f"   Pydantic Model Coverage: {summary['model_coverage']}")
    
    # List all tables
    print("\n📋 Available Tables:")
    tables = db.list_tables()
    print(f"   Found {len(tables)} tables")
    for i, table in enumerate(tables[:10], 1):  # Show first 10
        print(f"   {i:2d}. {table}")
    if len(tables) > 10:
        print(f"   ... and {len(tables) - 10} more tables")
    
    # Get information about specific tables
    print("\n🔍 Table Information:")
    interesting_tables = ["Config", "GeniSysObjects", "Events", "DeviceTypes"]
    
    for table_name in interesting_tables:
        if db.table_exists(table_name):
            info = db.get_table_info(table_name)
            validation_status = "✓ Validated" if info['has_pydantic_model'] else "○ Raw only"
            print(f"   {table_name}:")
            print(f"     Records: {info['record_count']:,}")
            print(f"     Columns: {info['column_count']}")
            print(f"     Validation: {validation_status}")
    
    # Get data from a specific table
    print("\n📄 Table Data Example:")
    if db.table_exists("Config"):
        config_data = db.get_table("Config")
        print(f"   Config table columns: {list(config_data.keys())}")
        
        # Get validated data (if model exists)
        try:
            validated_config = db.get_table("Config", validate=True)
            print(f"   ✓ Pydantic validation successful")
        except Exception as e:
            print(f"   ○ Validation not available: {e}")
    
    # Export examples
    print("\n💾 Export Examples:")
    
    # Export single table to JSON
    result = db.export_json("config_export.json", tables=["Config"])
    print(f"   ✓ Exported {result['tables_exported']} table to JSON")
    
    # Export multiple tables to YAML
    result = db.export_yaml("lighting_export.yaml", tables=["GeniSys*", "Config"])
    print(f"   ✓ Exported {result['tables_exported']} tables to YAML")
    
    # Export to CSV with separate files
    result = db.export_csv("data_export.csv", tables=["Config", "Events"], separate_files=True)
    print(f"   ✓ Exported {result['tables_exported']} tables to separate CSV files")
    
    # Generic export method
    result = db.export("all_data.json", format="json")
    print(f"   ✓ Exported all {result['tables_exported']} tables to JSON")
    
    print(f"\n📁 Output Files:")
    for output_file in result['output_files'][:3]:  # Show first few files
        file_path = Path(output_file)
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f"   {file_path.name}: {size_kb:.1f} KB")
    if len(result['output_files']) > 3:
        print(f"   ... and {len(result['output_files']) - 3} more files")
    
    print("\n🚀 API Usage Complete!")


def convenience_functions_example():
    """Show convenience function usage."""
    print("\n🛠 Convenience Functions Example:")
    
    # Quick operations without creating MerlinDB instance
    mdb_file = "test.mdb"
    
    if not Path(mdb_file).exists():
        print(f"   Skipping - {mdb_file} not found")
        return
    
    # Quick table listing
    tables = merlindb.list_tables(mdb_file)
    print(f"   Quick list: {len(tables)} tables found")
    
    # Quick database info
    info = merlindb.get_database_info(mdb_file)
    print(f"   Quick info: {info['total_records']:,} records in {info['total_tables']} tables")
    
    # Quick export
    result = merlindb.quick_export(mdb_file, "quick_export.json", format="json", tables=["Config"])
    print(f"   Quick export: {result['tables_exported']} table exported")


if __name__ == "__main__":
    main()
    convenience_functions_example()