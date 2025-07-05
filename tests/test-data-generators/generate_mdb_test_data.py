#!/usr/bin/env python
"""
Generate MDB test files with various edge cases for comprehensive testing.

Note: This generates mock MDB file headers and structures for testing file detection.
Creating actual MDB files requires Microsoft Access or specialized libraries.
"""

import random
import struct
from pathlib import Path


class MDBTestGenerator:
    """Generate test MDB/ACCDB file headers and structures."""

    # MDB/ACCDB file signatures
    MDB_JET3_SIGNATURE = b"\x00\x01\x00\x00Standard Jet DB\x00"
    MDB_JET4_SIGNATURE = b"\x00\x01\x00\x00Standard Jet DB\x00"
    ACCDB_ACE12_SIGNATURE = b"\x00\x01\x00\x00Standard ACE DB\x00"
    ACCDB_ACE14_SIGNATURE = b"\x00\x01\x00\x00Standard ACE DB\x00"

    @staticmethod
    def generate_mdb_header(version="jet4"):
        """Generate a valid MDB file header."""
        headers = {
            "jet3": MDBTestGenerator.MDB_JET3_SIGNATURE,
            "jet4": MDBTestGenerator.MDB_JET4_SIGNATURE,
            "ace12": MDBTestGenerator.ACCDB_ACE12_SIGNATURE,
            "ace14": MDBTestGenerator.ACCDB_ACE14_SIGNATURE,
        }

        header = bytearray(2048)  # MDB files have 2KB headers
        signature = headers.get(version, headers["jet4"])
        header[0 : len(signature)] = signature

        # Add version-specific bytes
        if version == "jet3":
            header[0x14] = 0x00  # Jet 3.x
        elif version == "jet4":
            header[0x14] = 0x01  # Jet 4.x
        elif version.startswith("ace"):
            header[0x14] = 0x02  # ACE 12.0+

        # Add some realistic header data
        header[0x3C:0x40] = struct.pack("<I", 0x400)  # Page size
        header[0x5A] = 0x01  # Valid database

        return bytes(header)

    @staticmethod
    def generate_corrupted_mdb():
        """Generate a corrupted MDB header for testing."""
        header = bytearray(2048)
        # Start with valid signature but corrupt other parts
        header[0:20] = b"\x00\x01\x00\x00Standard Jet DB\x00"
        # Corrupt the version byte
        header[0x14] = 0xFF
        # Add random data
        for i in range(100, 200):
            header[i] = random.randint(0, 255)
        return bytes(header)

    @staticmethod
    def generate_encrypted_mdb():
        """Generate an encrypted MDB header."""
        header = MDBTestGenerator.generate_mdb_header("jet4")
        header = bytearray(header)
        # Set encryption flag
        header[0x42] = 0x01
        # Add encrypted marker pattern
        for i in range(0x100, 0x200):
            header[i] = (i * 7 + 13) % 256
        return bytes(header)

    @staticmethod
    def generate_partial_mdb():
        """Generate a partial/truncated MDB file."""
        # Only 1KB instead of minimum 2KB
        header = MDBTestGenerator.generate_mdb_header("jet4")
        return header[:1024]

    @staticmethod
    def generate_empty_mdb():
        """Generate an empty but valid MDB structure."""
        header = MDBTestGenerator.generate_mdb_header("jet4")
        # Just header, no data pages
        return header

    @staticmethod
    def generate_large_mdb_header():
        """Generate header for a large MDB file."""
        header = bytearray(MDBTestGenerator.generate_mdb_header("jet4"))
        # Set file size indicators
        header[0x3C:0x40] = struct.pack("<I", 0x1000)  # Larger page size
        # Add table count
        header[0x200:0x204] = struct.pack("<I", 50)  # 50 tables
        return bytes(header)


def generate_mdb_test_files():
    """Generate various MDB test files."""
    output_dir = Path(__file__).parent.parent / "data" / "mdb"
    output_dir.mkdir(parents=True, exist_ok=True)

    test_cases = [
        # Valid MDB files
        ("jet3_database.mdb", MDBTestGenerator.generate_mdb_header("jet3")),
        ("jet4_database.mdb", MDBTestGenerator.generate_mdb_header("jet4")),
        ("access_2007.accdb", MDBTestGenerator.generate_mdb_header("ace12")),
        ("access_2010.accdb", MDBTestGenerator.generate_mdb_header("ace14")),
        # Edge cases
        ("corrupted.mdb", MDBTestGenerator.generate_corrupted_mdb()),
        ("encrypted.mdb", MDBTestGenerator.generate_encrypted_mdb()),
        ("truncated.mdb", MDBTestGenerator.generate_partial_mdb()),
        ("empty_valid.mdb", MDBTestGenerator.generate_empty_mdb()),
        ("large_structure.mdb", MDBTestGenerator.generate_large_mdb_header()),
        # Invalid files
        ("not_mdb.txt", b"This is not an MDB file"),
        ("wrong_header.mdb", b"WRONGHEADER" + b"\x00" * 2038),
        ("zero_bytes.mdb", b"\x00" * 2048),
    ]

    for filename, content in test_cases:
        filepath = output_dir / filename
        filepath.write_bytes(content)
        print(f"Created: {filepath} ({len(content)} bytes)")

    # Create a file that looks like MDB but isn't
    fake_mdb = output_dir / "fake_mdb.mdb"
    fake_content = b"MDB" + b"\x00" * 2045
    fake_mdb.write_bytes(fake_content)
    print(f"Created: {fake_mdb} (fake MDB)")

    print(f"\nGenerated {len(test_cases) + 1} MDB test files in {output_dir}")


def generate_mdb_table_structures():
    """Generate JSON files describing table structures for testing."""
    import json

    output_dir = Path(__file__).parent.parent / "data" / "mdb" / "structures"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Simple structure
    simple_structure = {
        "tables": {
            "Customers": {
                "columns": ["ID", "Name", "Email", "Phone"],
                "rows": 100,
                "primary_key": "ID",
            }
        }
    }

    # Complex structure
    complex_structure = {
        "tables": {
            "Customers": {
                "columns": [
                    "CustomerID",
                    "FirstName",
                    "LastName",
                    "Email",
                    "Phone",
                    "Address",
                    "City",
                    "State",
                    "ZipCode",
                    "Country",
                    "DateJoined",
                ],
                "rows": 1000,
                "primary_key": "CustomerID",
            },
            "Orders": {
                "columns": [
                    "OrderID",
                    "CustomerID",
                    "OrderDate",
                    "ShipDate",
                    "Total",
                    "Status",
                    "PaymentMethod",
                ],
                "rows": 5000,
                "primary_key": "OrderID",
                "foreign_keys": {"CustomerID": "Customers.CustomerID"},
            },
            "OrderDetails": {
                "columns": [
                    "DetailID",
                    "OrderID",
                    "ProductID",
                    "Quantity",
                    "UnitPrice",
                    "Discount",
                ],
                "rows": 15000,
                "primary_key": "DetailID",
                "foreign_keys": {
                    "OrderID": "Orders.OrderID",
                    "ProductID": "Products.ProductID",
                },
            },
            "Products": {
                "columns": [
                    "ProductID",
                    "ProductName",
                    "CategoryID",
                    "UnitPrice",
                    "UnitsInStock",
                    "Discontinued",
                ],
                "rows": 200,
                "primary_key": "ProductID",
                "foreign_keys": {"CategoryID": "Categories.CategoryID"},
            },
            "Categories": {
                "columns": ["CategoryID", "CategoryName", "Description"],
                "rows": 20,
                "primary_key": "CategoryID",
            },
        },
        "relationships": [
            {
                "from": "Orders.CustomerID",
                "to": "Customers.CustomerID",
                "type": "many-to-one",
            },
            {
                "from": "OrderDetails.OrderID",
                "to": "Orders.OrderID",
                "type": "many-to-one",
            },
            {
                "from": "OrderDetails.ProductID",
                "to": "Products.ProductID",
                "type": "many-to-one",
            },
            {
                "from": "Products.CategoryID",
                "to": "Categories.CategoryID",
                "type": "many-to-one",
            },
        ],
    }

    # Edge case structures
    edge_cases = {
        "empty_tables": {
            "tables": {
                "EmptyTable": {"columns": ["ID", "Name"], "rows": 0},
                "AnotherEmpty": {"columns": ["Col1"], "rows": 0},
            }
        },
        "special_names": {
            "tables": {
                "Table With Spaces": {
                    "columns": ["Column With Space", "Normal_Column"],
                    "rows": 10,
                },
                "Special!@#$%^&*()": {"columns": ["ID", "Data"], "rows": 5},
                "日本語テーブル": {"columns": ["識別子", "データ"], "rows": 3},
            }
        },
        "many_columns": {
            "tables": {
                "WideTable": {
                    "columns": [f"Column_{i:03d}" for i in range(255)],  # Max columns
                    "rows": 10,
                }
            }
        },
        "many_tables": {
            "tables": {
                f"Table_{i:03d}": {
                    "columns": ["ID", "Data"],
                    "rows": random.randint(0, 100),
                }
                for i in range(100)  # 100 tables
            }
        },
    }

    # Save all structures
    structures = [
        ("simple_structure.json", simple_structure),
        ("complex_structure.json", complex_structure),
        ("empty_tables.json", edge_cases["empty_tables"]),
        ("special_names.json", edge_cases["special_names"]),
        ("many_columns.json", edge_cases["many_columns"]),
        ("many_tables.json", edge_cases["many_tables"]),
    ]

    for filename, structure in structures:
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        print(f"Created: {filepath}")

    print(f"\nGenerated {len(structures)} MDB structure files in {output_dir}")


if __name__ == "__main__":
    generate_mdb_test_files()
    generate_mdb_table_structures()
