#!/usr/bin/env python
"""Test script for UCanAccess subprocess backend."""

import logging
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pyforge_cli.backends.ucanaccess_subprocess_backend import UCanAccessSubprocessBackend

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

def test_subprocess_backend():
    """Test the subprocess backend."""
    print("=" * 80)
    print("Testing UCanAccess Subprocess Backend")
    print("=" * 80)
    
    backend = UCanAccessSubprocessBackend()
    
    # Check availability
    print("\n1. Checking backend availability...")
    if backend.is_available():
        print("✓ Backend is available")
    else:
        print("✗ Backend is not available")
        return
    
    # Test with a sample MDB file
    test_file = "/Volumes/cortex_dev_catalog/0000_santosh/volume_sandbox/sample-datasets/access/small/access_sakila.mdb"
    
    print(f"\n2. Testing connection to: {test_file}")
    
    try:
        if backend.connect(test_file):
            print("✓ Connection successful")
            
            # List tables
            print("\n3. Listing tables...")
            tables = backend.list_tables()
            print(f"✓ Found {len(tables)} tables: {tables}")
            
            # Read a table (if any exist)
            if tables:
                table_name = tables[0]
                print(f"\n4. Reading table '{table_name}'...")
                df = backend.read_table(table_name)
                print(f"✓ Read {len(df)} rows, {len(df.columns)} columns")
                print(f"   Columns: {list(df.columns)}")
                print(f"   First few rows:")
                print(df.head())
            
            # Get connection info
            print("\n5. Connection info:")
            info = backend.get_connection_info()
            for key, value in info.items():
                print(f"   {key}: {value}")
            
        else:
            print("✗ Connection failed")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        backend.close()
        print("\n✓ Backend closed")
    
    print("=" * 80)

if __name__ == "__main__":
    test_subprocess_backend()