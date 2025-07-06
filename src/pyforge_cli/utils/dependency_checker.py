"""Dependency checker for database backend capabilities."""

import logging
import platform
import subprocess
from typing import Dict, List, Optional, Tuple


class DependencyChecker:
    """Check and validate dependencies for database backends."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def check_java(self) -> Tuple[bool, Optional[str]]:
        """Check if Java runtime is available.

        Returns:
            Tuple of (is_available, version_string)
        """
        try:
            result = subprocess.run(
                ["java", "-version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                # Extract version from stderr (Java outputs version to stderr)
                version_line = (
                    result.stderr.split("\n")[0] if result.stderr else "Unknown"
                )
                return True, version_line
            else:
                return False, None

        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            self.logger.debug(f"Java check failed: {e}")
            return False, None

    def check_jaydebeapi(self) -> Tuple[bool, Optional[str]]:
        """Check if JayDeBeApi is available.

        Returns:
            Tuple of (is_available, version_string)
        """
        try:
            import jaydebeapi

            version = getattr(jaydebeapi, "__version__", "Unknown")
            return True, version
        except ImportError:
            return False, None

    def check_jpype(self) -> Tuple[bool, Optional[str]]:
        """Check if JPype1 is available.

        Returns:
            Tuple of (is_available, version_string)
        """
        try:
            import jpype

            version = getattr(jpype, "__version__", "Unknown")
            return True, version
        except ImportError:
            return False, None

    def check_pyodbc(self) -> Tuple[bool, Optional[str]]:
        """Check if pyodbc is available.

        Returns:
            Tuple of (is_available, version_string)
        """
        try:
            import pyodbc

            version = getattr(pyodbc, "version", "Unknown")
            return True, version
        except ImportError:
            return False, None

    def check_access_odbc_drivers(self) -> Tuple[bool, List[str]]:
        """Check for Microsoft Access ODBC drivers (Windows only).

        Returns:
            Tuple of (drivers_available, list_of_drivers)
        """
        if platform.system() != "Windows":
            return False, []

        try:
            import pyodbc

            # Get all available ODBC drivers
            all_drivers = pyodbc.drivers()

            # Filter for Access drivers
            access_drivers = [d for d in all_drivers if "Microsoft Access Driver" in d]

            return len(access_drivers) > 0, access_drivers

        except ImportError:
            return False, []
        except Exception as e:
            self.logger.debug(f"ODBC driver check failed: {e}")
            return False, []

    def get_ucanaccess_capabilities(self) -> Dict[str, any]:
        """Get UCanAccess backend capabilities.

        Returns:
            Dictionary with capability information
        """
        java_available, java_version = self.check_java()
        jaydebeapi_available, jaydebeapi_version = self.check_jaydebeapi()
        jpype_available, jpype_version = self.check_jpype()

        # Check if UCanAccess JAR is available
        jar_available = False
        jar_info = None

        try:
            from ..backends.jar_manager import UCanAccessJARManager

            jar_manager = UCanAccessJARManager()
            jar_available = jar_manager.ensure_jar_available()
            jar_info = jar_manager.get_jar_info()
        except Exception as e:
            self.logger.debug(f"UCanAccess JAR check failed: {e}")

        return {
            "backend": "UCanAccess",
            "available": java_available and jaydebeapi_available and jpype_available,
            "java": {"available": java_available, "version": java_version},
            "jaydebeapi": {
                "available": jaydebeapi_available,
                "version": jaydebeapi_version,
            },
            "jpype": {"available": jpype_available, "version": jpype_version},
            "jar": {"available": jar_available, "info": jar_info},
            "cross_platform": True,
        }

    def get_pyodbc_capabilities(self) -> Dict[str, any]:
        """Get pyodbc backend capabilities.

        Returns:
            Dictionary with capability information
        """
        pyodbc_available, pyodbc_version = self.check_pyodbc()
        drivers_available, access_drivers = self.check_access_odbc_drivers()

        return {
            "backend": "pyodbc",
            "available": pyodbc_available and drivers_available,
            "pyodbc": {"available": pyodbc_available, "version": pyodbc_version},
            "drivers": {
                "available": drivers_available,
                "access_drivers": access_drivers,
            },
            "platform": platform.system(),
            "windows_only": True,
        }

    def get_mdb_capabilities(self) -> Dict[str, any]:
        """Get comprehensive MDB conversion capabilities.

        Returns:
            Dictionary with all backend capabilities
        """
        ucanaccess_caps = self.get_ucanaccess_capabilities()
        pyodbc_caps = self.get_pyodbc_capabilities()

        # Determine best available backend
        best_backend = None
        if ucanaccess_caps["available"]:
            best_backend = "UCanAccess"
        elif pyodbc_caps["available"]:
            best_backend = "pyodbc"

        return {
            "summary": {
                "any_backend_available": best_backend is not None,
                "best_backend": best_backend,
                "platform": platform.system(),
                "total_backends": sum(
                    [
                        1 if ucanaccess_caps["available"] else 0,
                        1 if pyodbc_caps["available"] else 0,
                    ]
                ),
            },
            "backends": {"ucanaccess": ucanaccess_caps, "pyodbc": pyodbc_caps},
        }

    def get_installation_instructions(self) -> Dict[str, List[str]]:
        """Get installation instructions for missing dependencies.

        Returns:
            Dictionary with installation commands by backend
        """
        capabilities = self.get_mdb_capabilities()
        instructions = {}

        # UCanAccess instructions
        if not capabilities["backends"]["ucanaccess"]["available"]:
            ucanaccess_steps = []

            if not capabilities["backends"]["ucanaccess"]["java"]["available"]:
                ucanaccess_steps.append("Install Java 8 or higher:")
                if platform.system() == "Windows":
                    ucanaccess_steps.append("  - Download from https://adoptium.net/")
                elif platform.system() == "Darwin":  # macOS
                    ucanaccess_steps.append("  - brew install openjdk")
                else:  # Linux
                    ucanaccess_steps.append(
                        "  - sudo apt install openjdk-11-jre (Ubuntu/Debian)"
                    )
                    ucanaccess_steps.append(
                        "  - sudo yum install java-11-openjdk (RHEL/CentOS)"
                    )

            missing_packages = []
            if not capabilities["backends"]["ucanaccess"]["jaydebeapi"]["available"]:
                missing_packages.append("jaydebeapi")
            if not capabilities["backends"]["ucanaccess"]["jpype"]["available"]:
                missing_packages.append("jpype1")

            if missing_packages:
                ucanaccess_steps.append("Install Python packages:")
                ucanaccess_steps.append(f"  pip install {' '.join(missing_packages)}")

            instructions["ucanaccess"] = ucanaccess_steps

        # pyodbc instructions
        if not capabilities["backends"]["pyodbc"]["available"]:
            pyodbc_steps = []

            if platform.system() != "Windows":
                pyodbc_steps.append("pyodbc backend is only available on Windows")
            else:
                if not capabilities["backends"]["pyodbc"]["pyodbc"]["available"]:
                    pyodbc_steps.append("Install pyodbc:")
                    pyodbc_steps.append("  pip install pyodbc")

                if not capabilities["backends"]["pyodbc"]["drivers"]["available"]:
                    pyodbc_steps.append("Install Microsoft Access Database Engine:")
                    pyodbc_steps.append("  - Download from Microsoft's website")
                    pyodbc_steps.append(
                        "  - Choose 32-bit or 64-bit to match your Python installation"
                    )

            instructions["pyodbc"] = pyodbc_steps

        return instructions

    def print_capabilities_report(self):
        """Print a comprehensive capabilities report."""
        capabilities = self.get_mdb_capabilities()

        print("=== MDB Conversion Capabilities Report ===")
        print()

        # Summary
        summary = capabilities["summary"]
        print(f"Platform: {summary['platform']}")
        print(f"Available backends: {summary['total_backends']}")
        print(f"Best backend: {summary['best_backend'] or 'None'}")
        print()

        # UCanAccess details
        ucanaccess = capabilities["backends"]["ucanaccess"]
        print("UCanAccess Backend (Cross-platform):")
        print(
            f"  Overall: {'[OK] Available' if ucanaccess['available'] else '[FAIL] Not Available'}"
        )
        print(
            f"  Java: {'[OK]' if ucanaccess['java']['available'] else '[FAIL]'} {ucanaccess['java']['version'] or 'Not found'}"
        )
        print(
            f"  JayDeBeApi: {'[OK]' if ucanaccess['jaydebeapi']['available'] else '[FAIL]'} {ucanaccess['jaydebeapi']['version'] or 'Not installed'}"
        )
        print(
            f"  JPype1: {'[OK]' if ucanaccess['jpype']['available'] else '[FAIL]'} {ucanaccess['jpype']['version'] or 'Not installed'}"
        )
        print(
            f"  JAR: {'[OK]' if ucanaccess['jar']['available'] else '[FAIL]'} {'Available' if ucanaccess['jar']['available'] else 'Will download on first use'}"
        )
        print()

        # pyodbc details
        pyodbc = capabilities["backends"]["pyodbc"]
        print("pyodbc Backend (Windows only):")
        print(
            f"  Overall: {'[OK] Available' if pyodbc['available'] else '[FAIL] Not Available'}"
        )
        print(
            f"  pyodbc: {'[OK]' if pyodbc['pyodbc']['available'] else '[FAIL]'} {pyodbc['pyodbc']['version'] or 'Not installed'}"
        )
        if pyodbc["drivers"]["available"]:
            print(
                f"  Access Drivers: [OK] {', '.join(pyodbc['drivers']['access_drivers'])}"
            )
        else:
            print("  Access Drivers: [FAIL] Not found")
        print()

        # Installation instructions
        if not summary["any_backend_available"]:
            print("=== Installation Instructions ===")
            instructions = self.get_installation_instructions()

            for backend, steps in instructions.items():
                print(f"\n{backend.upper()}:")
                for step in steps:
                    print(f"  {step}")

        print()


# Convenience functions for CLI usage
def check_mdb_support() -> bool:
    """Quick check if any MDB backend is available."""
    checker = DependencyChecker()
    capabilities = checker.get_mdb_capabilities()
    return capabilities["summary"]["any_backend_available"]


def get_best_mdb_backend() -> Optional[str]:
    """Get the name of the best available MDB backend."""
    checker = DependencyChecker()
    capabilities = checker.get_mdb_capabilities()
    return capabilities["summary"]["best_backend"]
