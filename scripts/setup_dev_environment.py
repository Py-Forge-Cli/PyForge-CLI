#!/usr/bin/env python3
"""
Development Environment Setup Script for PyForge CLI

This script sets up a consistent development environment following Python best practices.
It handles virtual environment creation, dependency installation, and pre-commit hooks.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Optional, List, Tuple


class Colors:
    """Terminal color codes for pretty output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message: str) -> None:
    """Print a formatted header message"""
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")


def print_success(message: str) -> None:
    """Print a success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str) -> None:
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message: str) -> None:
    """Print an info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def print_warning(message: str) -> None:
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def run_command(cmd: List[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a command and handle errors gracefully"""
    try:
        if capture_output:
            return subprocess.run(cmd, check=check, capture_output=True, text=True)
        else:
            return subprocess.run(cmd, check=check)
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        print_error(f"Error: {e}")
        if capture_output and e.stderr:
            print_error(f"Stderr: {e.stderr}")
        raise


def check_python_version() -> Tuple[int, int]:
    """Check if Python version meets requirements"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8 or higher is required")
        sys.exit(1)
    
    # Warn about Databricks compatibility
    if version.major == 3 and version.minor == 11:
        print_warning("Python 3.11 detected. For Databricks Serverless V1 compatibility, Python 3.10 is recommended.")
        print_info("Databricks Runtime 14.3 LTS uses Python 3.10.12")
    elif version.major == 3 and version.minor >= 12:
        print_warning(f"Python {version.major}.{version.minor} detected. For best compatibility, Python 3.10 is recommended.")
    
    return version.major, version.minor


def find_python_executable() -> str:
    """Find the appropriate Python executable"""
    # Check for python3.10 first (recommended for Databricks)
    if shutil.which("python3.10"):
        print_success("Found Python 3.10 - recommended for Databricks compatibility")
        return "python3.10"
    
    # Check for python3 first, then python
    for cmd in ["python3", "python"]:
        if shutil.which(cmd):
            return cmd
    
    print_error("No Python executable found")
    sys.exit(1)


def check_java_installation() -> bool:
    """Check if Java is installed (required for PySpark tests)"""
    try:
        result = run_command(["java", "-version"], capture_output=True)
        print_success("Java is installed (required for PySpark 3.5.0)")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Java is not installed - PySpark tests will be skipped")
        print_info("Java 8 or 11 is required for PySpark 3.5.0")
        return False


def check_existing_venv(venv_path: Path) -> bool:
    """Check if virtual environment already exists"""
    if venv_path.exists():
        # Check if it's a valid venv
        activate_script = venv_path / "bin" / "activate" if platform.system() != "Windows" else venv_path / "Scripts" / "activate.bat"
        if activate_script.exists():
            return True
    return False


def create_virtual_environment(venv_name: str = ".venv") -> Path:
    """Create a virtual environment"""
    venv_path = Path.cwd() / venv_name
    
    if check_existing_venv(venv_path):
        print_info(f"Virtual environment '{venv_name}' already exists")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response != 'y':
            print_info("Using existing virtual environment")
            return venv_path
        else:
            print_info("Removing existing virtual environment...")
            shutil.rmtree(venv_path)
    
    print_info(f"Creating virtual environment '{venv_name}'...")
    python_exe = find_python_executable()
    run_command([python_exe, "-m", "venv", str(venv_path)])
    print_success(f"Virtual environment created at {venv_path}")
    
    return venv_path


def get_pip_command(venv_path: Path) -> List[str]:
    """Get the pip command for the virtual environment"""
    if platform.system() == "Windows":
        return [str(venv_path / "Scripts" / "python.exe"), "-m", "pip"]
    else:
        return [str(venv_path / "bin" / "python"), "-m", "pip"]


def upgrade_pip(venv_path: Path) -> None:
    """Upgrade pip to the latest version"""
    print_info("Upgrading pip...")
    pip_cmd = get_pip_command(venv_path)
    run_command(pip_cmd + ["install", "--upgrade", "pip"])
    print_success("pip upgraded successfully")


def install_dependencies(venv_path: Path, extras: List[str] = None) -> None:
    """Install project dependencies"""
    pip_cmd = get_pip_command(venv_path)
    
    # Install the project in editable mode with extras
    print_info("Installing project dependencies...")
    if extras:
        extras_str = ",".join(extras)
        run_command(pip_cmd + ["install", "-e", f".[{extras_str}]"])
    else:
        run_command(pip_cmd + ["install", "-e", "."])
    
    print_success("Project dependencies installed")
    
    # Install additional dev dependencies if they exist
    if Path("requirements-dev.txt").exists():
        print_info("Installing development dependencies...")
        run_command(pip_cmd + ["install", "-r", "requirements-dev.txt"])
        print_success("Development dependencies installed")


def setup_pre_commit(venv_path: Path) -> None:
    """Set up pre-commit hooks"""
    if not Path(".pre-commit-config.yaml").exists():
        print_warning("No .pre-commit-config.yaml found, skipping pre-commit setup")
        return
    
    print_info("Setting up pre-commit hooks...")
    if platform.system() == "Windows":
        pre_commit_cmd = [str(venv_path / "Scripts" / "pre-commit")]
    else:
        pre_commit_cmd = [str(venv_path / "bin" / "pre-commit")]
    
    try:
        run_command(pre_commit_cmd + ["install"])
        print_success("Pre-commit hooks installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Could not install pre-commit hooks")


def create_env_file() -> None:
    """Create a .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        print_info("Creating .env file...")
        env_file.write_text("""# PyForge CLI Environment Variables
# Copy this file to .env and update with your values

# Development settings
DEBUG=true
LOG_LEVEL=DEBUG

# Test settings
PYTEST_WORKERS=auto
PYTEST_TIMEOUT=300

# Java settings (for PySpark 3.5.0)
# JAVA_HOME=/path/to/java  # Java 8 or 11 required

# Databricks settings (optional)
# DATABRICKS_HOST=https://your-workspace.databricks.com
# DATABRICKS_TOKEN=your-token
""")
        print_success(".env file created (update with your settings)")
    else:
        print_info(".env file already exists")


def print_activation_instructions(venv_name: str) -> None:
    """Print instructions for activating the virtual environment"""
    print_header("Setup Complete!")
    
    print(f"{Colors.BOLD}To activate the virtual environment, run:{Colors.ENDC}\n")
    
    if platform.system() == "Windows":
        print(f"    {Colors.OKGREEN}{venv_name}\\Scripts\\activate{Colors.ENDC}")
    else:
        print(f"    {Colors.OKGREEN}source {venv_name}/bin/activate{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}To deactivate, run:{Colors.ENDC}")
    print(f"    {Colors.OKGREEN}deactivate{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}To run tests:{Colors.ENDC}")
    print(f"    {Colors.OKGREEN}pytest{Colors.ENDC}")
    print(f"    {Colors.OKGREEN}pytest -v --cov=pyforge_cli{Colors.ENDC}  # With coverage")
    print(f"    {Colors.OKGREEN}pytest -k 'not slow'{Colors.ENDC}  # Skip slow tests")
    
    print(f"\n{Colors.BOLD}To run linting:{Colors.ENDC}")
    print(f"    {Colors.OKGREEN}ruff check src tests{Colors.ENDC}")
    print(f"    {Colors.OKGREEN}black --check src tests{Colors.ENDC}")
    print(f"    {Colors.OKGREEN}mypy src{Colors.ENDC}")


def main():
    """Main setup function"""
    print_header("PyForge CLI Development Environment Setup")
    
    # Check Python version
    py_major, py_minor = check_python_version()
    print_success(f"Python {py_major}.{py_minor} detected")
    
    # Check Java installation
    has_java = check_java_installation()
    
    # Determine virtual environment name
    venv_name = ".venv"
    if len(sys.argv) > 1:
        venv_name = sys.argv[1]
        print_info(f"Using custom virtual environment name: {venv_name}")
    
    # Create virtual environment
    venv_path = create_virtual_environment(venv_name)
    
    # Upgrade pip
    upgrade_pip(venv_path)
    
    # Install dependencies
    extras = ["dev", "test", "all"]
    if has_java:
        extras.append("databricks")
    install_dependencies(venv_path, extras)
    
    # Setup pre-commit
    setup_pre_commit(venv_path)
    
    # Create .env file
    create_env_file()
    
    # Print activation instructions
    print_activation_instructions(venv_name)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)