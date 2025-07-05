"""
Smart Converter Selection Logic for Databricks Extension

This module implements intelligent converter selection based on environment,
file characteristics, and available resources.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cache_manager import get_cache_manager
from .classic_detector import ClassicDetector
from .environment import DatabricksEnvironment
from .runtime_version import RuntimeVersionDetector
from .serverless_detector import ServerlessDetector


class ConverterType(Enum):
    """Available converter types."""

    SPARK = "spark"
    PANDAS = "pandas"
    PYARROW = "pyarrow"
    NATIVE = "native"  # PyForge's native converters


@dataclass
class FileCharacteristics:
    """Characteristics of a file that influence converter selection."""

    size_bytes: int
    format: str
    row_estimate: Optional[int] = None
    column_count: Optional[int] = None
    has_nested_data: Optional[bool] = None
    encoding: Optional[str] = None
    compression: Optional[str] = None


@dataclass
class ConverterRecommendation:
    """Converter recommendation with reasoning."""

    converter_type: ConverterType
    confidence: float  # 0.0 to 1.0
    reasons: List[str]
    estimated_performance: str  # "fast", "medium", "slow"
    memory_requirement: str  # "low", "medium", "high"
    fallback_options: List[ConverterType]


class ConverterSelector:
    """
    Intelligent converter selection for Databricks environments.

    Selects the optimal converter based on:
    - Environment type (serverless, classic, local)
    - File characteristics (size, format, complexity)
    - Available resources (memory, cores)
    - Runtime capabilities
    """

    # Size thresholds for converter selection
    SMALL_FILE_THRESHOLD = 10 * 1024 * 1024  # 10 MB
    MEDIUM_FILE_THRESHOLD = 100 * 1024 * 1024  # 100 MB
    LARGE_FILE_THRESHOLD = 1024 * 1024 * 1024  # 1 GB

    # Format support by converter
    FORMAT_SUPPORT = {
        ConverterType.SPARK: {
            "csv",
            "json",
            "parquet",
            "orc",
            "avro",
            "xml",
            "delta",
            "text",
        },
        ConverterType.PANDAS: {
            "csv",
            "json",
            "parquet",
            "excel",
            "xlsx",
            "xls",
            "feather",
            "hdf",
            "stata",
        },
        ConverterType.PYARROW: {"parquet", "feather", "csv", "json", "orc"},
        ConverterType.NATIVE: {
            "csv",
            "json",
            "parquet",
            "excel",
            "xml",
            "yaml",
            "toml",
            "avro",
        },
    }

    def __init__(self):
        """Initialize the converter selector."""
        self.logger = logging.getLogger("pyforge.extensions.databricks.selector")
        self.environment = DatabricksEnvironment()
        self.serverless_detector = ServerlessDetector()
        self.classic_detector = ClassicDetector()
        self.runtime_detector = RuntimeVersionDetector()
        self.cache = get_cache_manager()

    def select_converter(
        self, input_file: Path, output_format: str, options: Dict[str, Any]
    ) -> ConverterRecommendation:
        """
        Select the optimal converter for a conversion task.

        Args:
            input_file: Input file path
            output_format: Target output format
            options: Conversion options

        Returns:
            ConverterRecommendation: Recommended converter with reasoning
        """
        # Check cache first
        cache_key = f"converter_selection:{input_file}:{output_format}:{hash(str(sorted(options.items())))}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Analyze file characteristics
        file_chars = self._analyze_file(input_file)

        # Get environment information
        env_info = self._get_environment_context()

        # Make selection
        recommendation = self._make_selection(
            file_chars, output_format, env_info, options
        )

        # Log selection reasoning
        self.logger.info(
            f"Selected {recommendation.converter_type.value} converter "
            f"(confidence: {recommendation.confidence:.2f}) for "
            f"{file_chars.format} -> {output_format} conversion"
        )
        for reason in recommendation.reasons:
            self.logger.debug(f"  - {reason}")

        # Cache the result
        self.cache.set(cache_key, recommendation, ttl=300)  # 5 minutes

        return recommendation

    def _analyze_file(self, file_path: Path) -> FileCharacteristics:
        """Analyze file characteristics."""
        try:
            stat = file_path.stat()
            size_bytes = stat.st_size

            # Determine format
            format_str = file_path.suffix.lower().lstrip(".")
            if not format_str:
                format_str = self._detect_format_from_content(file_path)

            # Estimate characteristics based on format and size
            characteristics = FileCharacteristics(
                size_bytes=size_bytes, format=format_str
            )

            # Quick sampling for structured formats
            if format_str in ["csv", "tsv"]:
                sample_info = self._sample_csv_file(file_path)
                characteristics.row_estimate = sample_info.get("row_estimate")
                characteristics.column_count = sample_info.get("column_count")
                characteristics.encoding = sample_info.get("encoding")

            elif format_str in ["json", "jsonl"]:
                characteristics.has_nested_data = self._check_json_nesting(file_path)

            elif format_str in ["xml"]:
                characteristics.has_nested_data = True  # XML is always nested

            # Check compression
            if file_path.suffix.lower() in [".gz", ".bz2", ".xz", ".zip"]:
                characteristics.compression = file_path.suffix.lower().lstrip(".")

            return characteristics

        except Exception as e:
            self.logger.warning(f"Error analyzing file: {e}")
            # Return minimal characteristics
            return FileCharacteristics(
                size_bytes=0, format=file_path.suffix.lower().lstrip(".") or "unknown"
            )

    def _get_environment_context(self) -> Dict[str, Any]:
        """Get current environment context."""
        context = {
            "is_databricks": self.environment.is_databricks_environment(),
            "compute_type": self.environment.get_compute_type(),
            "runtime_version": self.runtime_detector.get_runtime_version(),
            "features": {},
            "resources": {},
        }

        if context["is_databricks"]:
            # Get detailed environment info
            if context["compute_type"] == "serverless":
                context["features"] = self.serverless_detector.get_serverless_features()
                context["resources"] = {
                    "memory": "auto-scaled",
                    "cores": "auto-scaled",
                    "has_gpu": False,
                }
            elif context["compute_type"] == "classic":
                cluster_features = self.classic_detector.get_cluster_features()
                context["features"] = cluster_features
                context["resources"] = self.classic_detector.get_cluster_resources()

            # Get runtime features
            runtime_features = self.runtime_detector.get_feature_availability()
            context["features"].update(runtime_features)
        else:
            # Local environment
            context["resources"] = self._get_local_resources()

        return context

    def _make_selection(
        self,
        file_chars: FileCharacteristics,
        output_format: str,
        env_context: Dict[str, Any],
        options: Dict[str, Any],
    ) -> ConverterRecommendation:
        """Make converter selection based on all factors."""
        reasons = []
        scores = {
            ConverterType.SPARK: 0.0,
            ConverterType.PANDAS: 0.0,
            ConverterType.PYARROW: 0.0,
            ConverterType.NATIVE: 0.0,
        }

        # Rule 1: Format support
        for converter_type, supported_formats in self.FORMAT_SUPPORT.items():
            if (
                file_chars.format in supported_formats
                and output_format in supported_formats
            ):
                scores[converter_type] += 0.2
            elif (
                file_chars.format in supported_formats
                or output_format in supported_formats
            ):
                scores[converter_type] += 0.1

        # Rule 2: File size considerations
        if file_chars.size_bytes <= self.SMALL_FILE_THRESHOLD:
            # Small files: prefer pandas/native for speed
            scores[ConverterType.PANDAS] += 0.3
            scores[ConverterType.NATIVE] += 0.3
            scores[ConverterType.PYARROW] += 0.2
            reasons.append("Small file size favors in-memory processing")

        elif file_chars.size_bytes <= self.MEDIUM_FILE_THRESHOLD:
            # Medium files: balanced approach
            if env_context["is_databricks"]:
                scores[ConverterType.SPARK] += 0.2
                scores[ConverterType.PANDAS] += 0.2
            else:
                scores[ConverterType.PANDAS] += 0.3
                scores[ConverterType.PYARROW] += 0.2
            reasons.append("Medium file size allows flexible converter choice")

        else:
            # Large files: strongly prefer Spark in Databricks
            if env_context["is_databricks"]:
                scores[ConverterType.SPARK] += 0.5
                reasons.append("Large file size requires distributed processing")
            else:
                scores[ConverterType.PYARROW] += 0.3
                scores[ConverterType.NATIVE] += 0.2
                reasons.append("Large file size benefits from streaming processing")

        # Rule 3: Environment-specific optimizations
        if env_context["compute_type"] == "serverless":
            scores[ConverterType.SPARK] += 0.3
            reasons.append("Serverless compute optimized for Spark")

            if env_context["features"].get("photon_acceleration"):
                scores[ConverterType.SPARK] += 0.2
                reasons.append("Photon acceleration available")

        elif env_context["compute_type"] == "classic":
            if env_context["resources"].get("total_cores", 0) > 8:
                scores[ConverterType.SPARK] += 0.2
                reasons.append("Multiple cores available for parallel processing")

        # Rule 4: Format-specific optimizations
        if file_chars.format == "excel" or file_chars.format in ["xlsx", "xls"]:
            scores[ConverterType.PANDAS] += 0.3
            scores[ConverterType.SPARK] += 0.2  # Spark can use pandas API
            reasons.append("Excel format well-supported by pandas")

        elif file_chars.format == "xml":
            if file_chars.has_nested_data:
                scores[ConverterType.SPARK] += 0.3
                reasons.append("Complex XML benefits from Spark's schema inference")

        elif file_chars.format == "parquet":
            scores[ConverterType.PYARROW] += 0.2
            scores[ConverterType.SPARK] += 0.2
            reasons.append("Parquet format natively supported")

        # Rule 5: User preferences
        if options.get("force_spark"):
            scores[ConverterType.SPARK] += 1.0
            reasons.append("User requested Spark converter")

        elif options.get("force_pandas"):
            scores[ConverterType.PANDAS] += 1.0
            reasons.append("User requested pandas converter")

        # Rule 6: Memory constraints
        available_memory = self._estimate_available_memory(env_context)
        required_memory = self._estimate_memory_requirement(file_chars)

        if required_memory > available_memory * 0.8:
            # Memory constrained - prefer streaming/distributed
            scores[ConverterType.SPARK] += 0.3
            scores[ConverterType.PYARROW] += 0.2
            scores[ConverterType.PANDAS] -= 0.3
            reasons.append("Memory constraints favor distributed/streaming processing")

        # Select converter with highest score
        best_converter = max(scores.items(), key=lambda x: x[1])[0]
        confidence = min(
            (
                scores[best_converter] / sum(scores.values())
                if sum(scores.values()) > 0
                else 0.0
            ),
            1.0,
        )

        # Determine performance characteristics
        estimated_performance = self._estimate_performance(
            best_converter, file_chars, env_context
        )
        memory_requirement = self._estimate_memory_class(best_converter, file_chars)

        # Determine fallback options
        fallback_options = sorted(
            [c for c in scores.keys() if c != best_converter and scores[c] > 0],
            key=lambda c: scores[c],
            reverse=True,
        )

        return ConverterRecommendation(
            converter_type=best_converter,
            confidence=confidence,
            reasons=reasons,
            estimated_performance=estimated_performance,
            memory_requirement=memory_requirement,
            fallback_options=fallback_options,
        )

    def _detect_format_from_content(self, file_path: Path) -> str:
        """Detect format from file content."""
        try:
            with open(file_path, "rb") as f:
                header = f.read(1024)

            # Check for common format signatures
            if header.startswith(b"PK"):
                return "excel"  # Excel files are zip archives
            elif header.startswith(b"PAR1"):
                return "parquet"
            elif header.startswith(b"ORC"):
                return "orc"
            elif header.startswith(b"Obj\x01"):
                return "avro"
            elif b"<?xml" in header:
                return "xml"
            elif header.startswith(b"{") or header.startswith(b"["):
                return "json"
            else:
                # Assume CSV for text files
                return "csv"

        except Exception:
            return "unknown"

    def _sample_csv_file(self, file_path: Path) -> Dict[str, Any]:
        """Quick sampling of CSV file characteristics."""
        try:
            sample_size = 1024 * 1024  # 1MB sample
            with open(file_path, "rb") as f:
                sample = f.read(sample_size)

            # Detect encoding
            import chardet

            encoding_info = chardet.detect(sample)
            encoding = encoding_info["encoding"] or "utf-8"

            # Count lines and estimate total
            sample_lines = sample.count(b"\n")
            if sample_lines > 0:
                file_size = file_path.stat().st_size
                row_estimate = int((file_size / sample_size) * sample_lines)
            else:
                row_estimate = None

            # Count columns from first line
            try:
                first_line = sample.split(b"\n")[0].decode(encoding)
                column_count = len(first_line.split(","))
            except:
                column_count = None

            return {
                "row_estimate": row_estimate,
                "column_count": column_count,
                "encoding": encoding,
            }

        except Exception:
            return {}

    def _check_json_nesting(self, file_path: Path) -> bool:
        """Check if JSON file has nested structures."""
        try:
            import json

            with open(file_path) as f:
                # Read first few objects
                sample = f.read(10240)  # 10KB

            # Try to parse
            if file_path.suffix.lower() == ".jsonl":
                # JSON Lines format
                for line in sample.split("\n"):
                    if line.strip():
                        obj = json.loads(line)
                        if self._is_nested_structure(obj):
                            return True
            else:
                # Regular JSON
                obj = json.loads(sample)
                return self._is_nested_structure(obj)

        except Exception:
            pass

        return False

    def _is_nested_structure(
        self, obj: Any, depth: int = 0, max_depth: int = 3
    ) -> bool:
        """Check if object has nested structure."""
        if depth >= max_depth:
            return True

        if isinstance(obj, dict):
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    return self._is_nested_structure(value, depth + 1, max_depth)
        elif isinstance(obj, list) and obj:
            return self._is_nested_structure(obj[0], depth + 1, max_depth)

        return False

    def _get_local_resources(self) -> Dict[str, Any]:
        """Get local system resources."""
        try:
            import psutil

            return {
                "total_cores": os.cpu_count() or 1,
                "total_memory": f"{psutil.virtual_memory().total / (1024**3):.1f}GB",
                "available_memory_gb": psutil.virtual_memory().available / (1024**3),
            }
        except:
            return {
                "total_cores": os.cpu_count() or 1,
                "total_memory": "unknown",
                "available_memory_gb": 4.0,  # Conservative estimate
            }

    def _estimate_available_memory(self, env_context: Dict[str, Any]) -> float:
        """Estimate available memory in GB."""
        if env_context["compute_type"] == "serverless":
            return 100.0  # Serverless has flexible memory

        resources = env_context.get("resources", {})
        available = resources.get("available_memory_gb")

        if available:
            return float(available)

        # Parse total memory string
        total_memory = resources.get("total_memory", "")
        if isinstance(total_memory, str) and "GB" in total_memory:
            try:
                # Extract number from strings like "16GB" or "Driver: 8g, Executors: 4x4g"
                import re

                numbers = re.findall(r"(\d+(?:\.\d+)?)\s*[gG]", total_memory)
                if numbers:
                    total_gb = sum(float(n) for n in numbers)
                    return total_gb * 0.7  # Assume 70% available
            except:
                pass

        return 4.0  # Conservative default

    def _estimate_memory_requirement(self, file_chars: FileCharacteristics) -> float:
        """Estimate memory requirement in GB."""
        # Basic estimate: file size * multiplier based on format
        multipliers = {
            "csv": 3.0,  # String parsing overhead
            "json": 4.0,  # Object overhead
            "xml": 5.0,  # DOM parsing
            "parquet": 1.5,  # Columnar efficiency
            "orc": 1.5,
            "avro": 2.0,
            "excel": 3.5,
        }

        multiplier = multipliers.get(file_chars.format, 2.5)
        return (file_chars.size_bytes / (1024**3)) * multiplier

    def _estimate_performance(
        self,
        converter: ConverterType,
        file_chars: FileCharacteristics,
        env_context: Dict[str, Any],
    ) -> str:
        """Estimate performance as fast/medium/slow."""
        if converter == ConverterType.SPARK and env_context["is_databricks"]:
            if env_context["compute_type"] == "serverless":
                return "fast"
            elif file_chars.size_bytes > self.LARGE_FILE_THRESHOLD:
                return "fast"
            else:
                return "medium"  # Spark overhead for small files

        elif converter == ConverterType.PANDAS:
            if file_chars.size_bytes <= self.SMALL_FILE_THRESHOLD:
                return "fast"
            elif file_chars.size_bytes <= self.MEDIUM_FILE_THRESHOLD:
                return "medium"
            else:
                return "slow"

        elif converter == ConverterType.PYARROW:
            if file_chars.format in ["parquet", "feather"]:
                return "fast"
            else:
                return "medium"

        else:  # NATIVE
            if file_chars.size_bytes <= self.MEDIUM_FILE_THRESHOLD:
                return "medium"
            else:
                return "slow"

    def _estimate_memory_class(
        self, converter: ConverterType, file_chars: FileCharacteristics
    ) -> str:
        """Estimate memory requirement as low/medium/high."""
        if converter == ConverterType.SPARK:
            return "low"  # Distributed processing

        required_gb = self._estimate_memory_requirement(file_chars)

        if required_gb < 1.0:
            return "low"
        elif required_gb < 8.0:
            return "medium"
        else:
            return "high"
