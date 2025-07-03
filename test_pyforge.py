#!/usr/bin/env python3
"""
Comprehensive PyForge CLI Testing Suite
"""
import os
import sys
import subprocess
import json
import pandas as pd
from pathlib import Path
import pytest
from typing import Dict, List, Tuple
import time


class PyForgeTestSuite:
    """Comprehensive test suite for PyForge CLI commands"""
    
    def __init__(self, test_env_path: str = "./test_env"):
        self.test_env = test_env_path
        self.test_data_dir = Path("test_data")
        self.sample_data_dir = Path("sample-datasets")
        self.test_output_dir = Path("test_output")
        self.results = []
        
        # Known issues in current version
        self.known_issues = {
            "convert_command_bug": "TypeError: ConverterRegistry.get_converter() takes 2 positional arguments but 3 were given",
            "missing_dependencies": ["fitz", "requests"]
        }
        
        # Ensure directories exist
        self.test_data_dir.mkdir(exist_ok=True)
        self.test_output_dir.mkdir(exist_ok=True)
        
    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a command and return success status, stdout, stderr"""
        try:
            # Activate virtual environment and run command
            full_cmd = f"source {self.test_env}/bin/activate && " + " ".join(cmd)
            
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", f"Command failed with exception: {str(e)}"
    
    def test_basic_commands(self) -> Dict:
        """Test basic PyForge commands"""
        tests = {
            "version": ["pyforge", "--version"],
            "help": ["pyforge", "--help"],
            "formats": ["pyforge", "formats"],
        }
        
        results = {}
        for test_name, cmd in tests.items():
            success, stdout, stderr = self.run_command(cmd)
            results[test_name] = {
                "success": success,
                "stdout": stdout[:500],  # Truncate for readability
                "stderr": stderr[:500],
                "command": " ".join(cmd)
            }
            
        return results
    
    def test_file_info_commands(self) -> Dict:
        """Test file info and validation commands"""
        test_files = [
            "sample-datasets/csv/small/sample_data.csv",
            "sample-datasets/xml/small/sample_data.xml"
        ]
        
        results = {}
        for file_path in test_files:
            if Path(file_path).exists():
                # Test info command
                info_success, info_out, info_err = self.run_command(["pyforge", "info", file_path])
                
                # Test validate command
                validate_success, validate_out, validate_err = self.run_command(["pyforge", "validate", file_path])
                
                results[file_path] = {
                    "info": {
                        "success": info_success,
                        "stdout": info_out[:300],
                        "stderr": info_err[:300]
                    },
                    "validate": {
                        "success": validate_success,
                        "stdout": validate_out[:300],
                        "stderr": validate_err[:300]
                    }
                }
        
        return results
    
    def test_conversion_commands(self) -> Dict:
        """Test file conversion commands - Note: Contains known bugs in v1.0.7"""
        conversion_tests = [
            {
                "input": "sample-datasets/csv/small/sample_data.csv",
                "output": "test_output/sample_csv_converted.txt",
                "format": None,  # Test default format
                "description": "CSV to TXT (default)"
            },
            {
                "input": "sample-datasets/xml/small/sample_data.xml",
                "output": "test_output/sample_xml_converted.txt",
                "format": None,  # Test default format  
                "description": "XML to TXT (default)"
            },
            {
                "input": "sample-datasets/csv/small/sample_data.csv",
                "output": "test_output/sample_csv_to_parquet.parquet",
                "format": "parquet",
                "description": "CSV to Parquet (known to fail in v1.0.7)"
            },
            {
                "input": "sample-datasets/xml/small/sample_data.xml",
                "output": "test_output/sample_xml_to_parquet.parquet",
                "format": "parquet",
                "description": "XML to Parquet (known to fail in v1.0.7)"
            }
        ]
        
        results = {}
        for test in conversion_tests:
            input_file = test["input"]
            output_file = test["output"]
            
            if not Path(input_file).exists():
                results[input_file] = {
                    "success": False,
                    "error": "Input file does not exist"
                }
                continue
            
            # Clean up output file if it exists
            if Path(output_file).exists():
                Path(output_file).unlink()
            
            # Build conversion command
            cmd = ["pyforge", "convert", input_file, output_file]
            if test["format"]:
                cmd.extend(["--format", test["format"]])
            
            # Run conversion
            success, stdout, stderr = self.run_command(cmd)
            
            # Check if output file was created
            output_created = Path(output_file).exists()
            
            # Check for known issues
            is_known_issue = "ConverterRegistry.get_converter()" in stderr
            
            results[input_file] = {
                "success": success and output_created,
                "command": " ".join(cmd),
                "description": test["description"],
                "stdout": stdout[:300],
                "stderr": stderr[:300],
                "output_created": output_created,
                "output_size": Path(output_file).stat().st_size if output_created else 0,
                "known_issue": is_known_issue,
                "expected_to_fail": test["format"] == "parquet"  # Known bug with format flag
            }
        
        return results
    
    def test_advanced_options(self) -> Dict:
        """Test advanced command options"""
        if not Path("sample-datasets/csv/small/sample_data.csv").exists():
            return {"error": "Sample dataset not found"}
            
        advanced_tests = [
            {
                "name": "force_overwrite",
                "cmd": ["pyforge", "convert", "sample-datasets/csv/small/sample_data.csv", "test_output/force_test.txt", "--force"]
            },
            {
                "name": "compression_test_known_to_fail", 
                "cmd": ["pyforge", "convert", "sample-datasets/csv/small/sample_data.csv", "test_output/compressed_test.parquet", "--compression", "gzip"],
                "expected_failure": True
            }
        ]
        
        results = {}
        for test in advanced_tests:
            success, stdout, stderr = self.run_command(test["cmd"])
            is_known_issue = "ConverterRegistry.get_converter()" in stderr
            expected_failure = test.get("expected_failure", False)
            
            results[test["name"]] = {
                "success": success,
                "command": " ".join(test["cmd"]),
                "stdout": stdout[:300],
                "stderr": stderr[:300],
                "known_issue": is_known_issue,
                "expected_failure": expected_failure
            }
            
        return results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        print("🧪 Running PyForge CLI Test Suite...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": {},
            "summary": {}
        }
        
        # Run all test categories
        test_categories = [
            ("basic_commands", self.test_basic_commands),
            ("file_info", self.test_file_info_commands), 
            ("conversions", self.test_conversion_commands),
            ("advanced_options", self.test_advanced_options),
            ("sample_datasets", self.test_sample_datasets)
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for category_name, test_func in test_categories:
            print(f"📋 Testing {category_name}...")
            
            try:
                category_results = test_func()
                report["test_results"][category_name] = category_results
                
                # Count successes in this category
                category_total, category_passed = self.count_successes(category_results)
                total_tests += category_total
                passed_tests += category_passed
                
                print(f"✅ {category_name}: {category_passed}/{category_total} passed")
                
            except Exception as e:
                report["test_results"][category_name] = {"error": str(e)}
                print(f"❌ {category_name}: Failed with error - {str(e)}")
        
        # Generate summary
        known_issues_count = self.count_known_issues(report["test_results"])
        
        report["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "known_issues": known_issues_count,
            "success_rate": round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0,
            "pyforge_version": "1.0.7",
            "test_environment": "Python virtual environment",
            "major_bugs_found": {
                "convert_command": "TypeError in ConverterRegistry.get_converter()",
                "missing_pdf_support": "No module named 'fitz'"
            }
        }
        
        # Add known issues summary
        report["known_issues"] = self.known_issues
        
        return report
    
    def count_successes(self, results) -> Tuple[int, int]:
        """Count successful tests in results dict"""
        total = 0
        passed = 0
        
        def count_recursive(obj):
            nonlocal total, passed
            if isinstance(obj, dict):
                if "success" in obj:
                    total += 1
                    if obj["success"]:
                        passed += 1
                else:
                    for value in obj.values():
                        count_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_recursive(item)
        
        count_recursive(results)
        return total, passed
    
    def count_known_issues(self, results) -> int:
        """Count tests that failed due to known issues"""
        count = 0
        
        def count_recursive(obj):
            nonlocal count
            if isinstance(obj, dict):
                if "known_issue" in obj and obj["known_issue"]:
                    count += 1
                else:
                    for value in obj.values():
                        count_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    count_recursive(item)
        
        count_recursive(results)
        return count
    
    def test_sample_datasets(self) -> Dict:
        """Test that sample datasets were installed correctly"""
        results = {}
        
        # Check if sample datasets directory exists
        if not self.sample_data_dir.exists():
            return {"error": "Sample datasets not found"}
        
        # Test dataset files
        expected_files = [
            "csv/small/sample_data.csv",
            "xml/small/sample_data.xml"
        ]
        
        for file_path in expected_files:
            full_path = self.sample_data_dir / file_path
            file_exists = full_path.exists()
            
            if file_exists:
                # Test info command on the file
                success, stdout, stderr = self.run_command(["pyforge", "info", str(full_path)])
                results[file_path] = {
                    "file_exists": True,
                    "info_command_success": success,
                    "file_size": full_path.stat().st_size,
                    "success": success
                }
            else:
                results[file_path] = {
                    "file_exists": False,
                    "success": False,
                    "error": "File not found"
                }
        
        return results
    
    def save_report(self, report: Dict, filename: str = "test_reports/pyforge_test_report.json"):
        """Save test report to file"""
        Path("test_reports").mkdir(exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to {filename}")
    
    def print_summary(self, report: Dict):
        """Print test summary to console"""
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("🏆 PYFORGE CLI TEST RESULTS SUMMARY")
        print("="*60)
        print(f"📅 Timestamp: {report['timestamp']}")
        print(f"🧪 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"🐛 Known Issues: {summary['known_issues']}")
        print(f"📊 Success Rate: {summary['success_rate']}%")
        print(f"🔧 PyForge Version: {summary['pyforge_version']}")
        print("="*60)
        
        # Show major bugs found
        if "major_bugs_found" in summary:
            print("\n🚨 MAJOR BUGS IDENTIFIED:")
            for bug_name, bug_desc in summary["major_bugs_found"].items():
                print(f"  • {bug_name}: {bug_desc}")
            print("="*60)


def main():
    """Main test execution function"""
    test_suite = PyForgeTestSuite()
    
    # Generate and save report
    report = test_suite.generate_report()
    test_suite.save_report(report)
    test_suite.print_summary(report)
    
    return report["summary"]["success_rate"] == 100.0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)