"""
Fallback Manager for Databricks Extension

This module manages fallback strategies when primary converters fail,
ensuring robust conversion with seamless fallback to alternative converters.
"""

import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .converter_selector import ConverterRecommendation, ConverterType


class FallbackReason(Enum):
    """Reasons for fallback."""

    CONVERTER_NOT_AVAILABLE = "converter_not_available"
    INITIALIZATION_FAILED = "initialization_failed"
    CONVERSION_ERROR = "conversion_error"
    MEMORY_ERROR = "memory_error"
    TIMEOUT = "timeout"
    FORMAT_NOT_SUPPORTED = "format_not_supported"
    USER_REQUESTED = "user_requested"


@dataclass
class FallbackAttempt:
    """Record of a fallback attempt."""

    converter_type: ConverterType
    reason: FallbackReason
    error_message: str
    timestamp: datetime
    duration_seconds: float
    stack_trace: Optional[str] = None


@dataclass
class FallbackResult:
    """Result of fallback execution."""

    success: bool
    final_converter: Optional[ConverterType]
    attempts: List[FallbackAttempt]
    total_duration: float
    output_path: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)


class FallbackManager:
    """
    Manages fallback strategies for converter failures.

    Provides automatic fallback to alternative converters when the
    primary converter fails, with comprehensive error tracking and
    recovery strategies.
    """

    # Maximum number of fallback attempts
    MAX_FALLBACK_ATTEMPTS = 3

    # Timeout for each converter attempt (seconds)
    CONVERTER_TIMEOUT = {
        ConverterType.SPARK: 600,  # 10 minutes
        ConverterType.PANDAS: 300,  # 5 minutes
        ConverterType.PYARROW: 300,  # 5 minutes
        ConverterType.NATIVE: 300,  # 5 minutes
    }

    def __init__(self):
        """Initialize the fallback manager."""
        self.logger = logging.getLogger("pyforge.extensions.databricks.fallback")
        self._converter_registry: Dict[ConverterType, Optional[Callable]] = {}
        self._initialization_status: Dict[ConverterType, bool] = {}
        self._failure_history: List[FallbackAttempt] = []

    def register_converter(
        self, converter_type: ConverterType, converter_callable: Callable
    ) -> None:
        """
        Register a converter implementation.

        Args:
            converter_type: Type of converter
            converter_callable: Callable that performs conversion
        """
        self._converter_registry[converter_type] = converter_callable
        self.logger.debug(f"Registered {converter_type.value} converter")

    def execute_with_fallback(
        self,
        input_file: Path,
        output_file: Path,
        recommendation: ConverterRecommendation,
        options: Dict[str, Any],
    ) -> FallbackResult:
        """
        Execute conversion with automatic fallback.

        Args:
            input_file: Input file path
            output_file: Output file path
            recommendation: Converter recommendation
            options: Conversion options

        Returns:
            FallbackResult: Result of conversion with fallback history
        """
        start_time = time.time()
        attempts = []
        warnings = []

        # Build fallback chain
        fallback_chain = self._build_fallback_chain(recommendation)

        self.logger.info(
            f"Starting conversion with fallback chain: "
            f"{[c.value for c in fallback_chain]}"
        )

        # Try each converter in the chain
        for i, converter_type in enumerate(fallback_chain):
            if i >= self.MAX_FALLBACK_ATTEMPTS:
                warnings.append(
                    f"Reached maximum fallback attempts ({self.MAX_FALLBACK_ATTEMPTS})"
                )
                break

            attempt_start = time.time()

            try:
                # Check if converter is available
                if not self._is_converter_available(converter_type):
                    attempt = FallbackAttempt(
                        converter_type=converter_type,
                        reason=FallbackReason.CONVERTER_NOT_AVAILABLE,
                        error_message=f"{converter_type.value} converter not available",
                        timestamp=datetime.now(),
                        duration_seconds=time.time() - attempt_start,
                    )
                    attempts.append(attempt)
                    self.logger.warning(
                        f"Converter {converter_type.value} not available"
                    )
                    continue

                # Initialize converter if needed
                if not self._initialize_converter(converter_type):
                    attempt = FallbackAttempt(
                        converter_type=converter_type,
                        reason=FallbackReason.INITIALIZATION_FAILED,
                        error_message=f"Failed to initialize {converter_type.value}",
                        timestamp=datetime.now(),
                        duration_seconds=time.time() - attempt_start,
                    )
                    attempts.append(attempt)
                    self.logger.warning(f"Failed to initialize {converter_type.value}")
                    continue

                # Execute conversion
                self.logger.info(f"Attempting conversion with {converter_type.value}")

                success = self._execute_conversion(
                    converter_type, input_file, output_file, options
                )

                if success:
                    # Success!
                    duration = time.time() - attempt_start
                    self.logger.info(
                        f"Successfully converted with {converter_type.value} "
                        f"in {duration:.2f} seconds"
                    )

                    return FallbackResult(
                        success=True,
                        final_converter=converter_type,
                        attempts=attempts,
                        total_duration=time.time() - start_time,
                        output_path=output_file,
                        warnings=warnings,
                    )
                else:
                    # Conversion returned False (not an exception)
                    attempt = FallbackAttempt(
                        converter_type=converter_type,
                        reason=FallbackReason.CONVERSION_ERROR,
                        error_message="Conversion returned False",
                        timestamp=datetime.now(),
                        duration_seconds=time.time() - attempt_start,
                    )
                    attempts.append(attempt)

            except MemoryError as e:
                attempt = FallbackAttempt(
                    converter_type=converter_type,
                    reason=FallbackReason.MEMORY_ERROR,
                    error_message=str(e),
                    timestamp=datetime.now(),
                    duration_seconds=time.time() - attempt_start,
                    stack_trace=traceback.format_exc(),
                )
                attempts.append(attempt)
                self.logger.error(f"Memory error with {converter_type.value}: {e}")

            except TimeoutError as e:
                attempt = FallbackAttempt(
                    converter_type=converter_type,
                    reason=FallbackReason.TIMEOUT,
                    error_message=str(e),
                    timestamp=datetime.now(),
                    duration_seconds=time.time() - attempt_start,
                    stack_trace=traceback.format_exc(),
                )
                attempts.append(attempt)
                self.logger.error(f"Timeout with {converter_type.value}: {e}")

            except Exception as e:
                # General conversion error
                error_msg = str(e)
                stack_trace = traceback.format_exc()

                # Classify the error
                reason = self._classify_error(e, error_msg)

                attempt = FallbackAttempt(
                    converter_type=converter_type,
                    reason=reason,
                    error_message=error_msg,
                    timestamp=datetime.now(),
                    duration_seconds=time.time() - attempt_start,
                    stack_trace=stack_trace,
                )
                attempts.append(attempt)
                self._failure_history.append(attempt)

                self.logger.error(
                    f"Error with {converter_type.value}: {error_msg}\n"
                    f"Stack trace:\n{stack_trace}"
                )

        # All converters failed
        self.logger.error("All converters in fallback chain failed")

        return FallbackResult(
            success=False,
            final_converter=None,
            attempts=attempts,
            total_duration=time.time() - start_time,
            warnings=warnings,
        )

    def get_failure_report(self) -> Dict[str, Any]:
        """
        Get comprehensive failure report.

        Returns:
            Dict[str, Any]: Failure statistics and patterns
        """
        if not self._failure_history:
            return {"total_failures": 0}

        # Analyze failure patterns
        by_converter = {}
        by_reason = {}

        for attempt in self._failure_history:
            # By converter
            conv_key = attempt.converter_type.value
            if conv_key not in by_converter:
                by_converter[conv_key] = []
            by_converter[conv_key].append(attempt)

            # By reason
            reason_key = attempt.reason.value
            if reason_key not in by_reason:
                by_reason[reason_key] = []
            by_reason[reason_key].append(attempt)

        # Calculate statistics
        report = {
            "total_failures": len(self._failure_history),
            "by_converter": {
                conv: {
                    "count": len(attempts),
                    "reasons": self._summarize_reasons(attempts),
                    "avg_duration": sum(a.duration_seconds for a in attempts)
                    / len(attempts),
                }
                for conv, attempts in by_converter.items()
            },
            "by_reason": {
                reason: {
                    "count": len(attempts),
                    "converters": list({a.converter_type.value for a in attempts}),
                    "recent_errors": [a.error_message for a in attempts[-3:]],
                }
                for reason, attempts in by_reason.items()
            },
            "recent_failures": [
                {
                    "converter": attempt.converter_type.value,
                    "reason": attempt.reason.value,
                    "error": attempt.error_message,
                    "timestamp": attempt.timestamp.isoformat(),
                }
                for attempt in self._failure_history[-10:]
            ],
        }

        return report

    def clear_failure_history(self) -> None:
        """Clear the failure history."""
        self._failure_history.clear()
        self.logger.info("Cleared failure history")

    # Private helper methods

    def _build_fallback_chain(
        self, recommendation: ConverterRecommendation
    ) -> List[ConverterType]:
        """Build fallback chain from recommendation."""
        chain = [recommendation.converter_type]

        # Add recommended fallbacks
        chain.extend(recommendation.fallback_options)

        # Add default fallbacks if not already present
        default_fallbacks = [
            ConverterType.NATIVE,  # Always try native as last resort
            ConverterType.PANDAS,  # Pandas is widely compatible
        ]

        for fallback in default_fallbacks:
            if fallback not in chain:
                chain.append(fallback)

        # Remove duplicates while preserving order
        seen = set()
        unique_chain = []
        for converter in chain:
            if converter not in seen:
                seen.add(converter)
                unique_chain.append(converter)

        return unique_chain

    def _is_converter_available(self, converter_type: ConverterType) -> bool:
        """Check if converter is available."""
        # Check if registered
        if converter_type not in self._converter_registry:
            return False

        # Check dependencies
        if converter_type == ConverterType.SPARK:
            try:
                import pyspark

                return True
            except ImportError:
                return False

        elif converter_type == ConverterType.PANDAS:
            try:
                import pandas

                return True
            except ImportError:
                return False

        elif converter_type == ConverterType.PYARROW:
            try:
                import pyarrow

                return True
            except ImportError:
                return False

        # NATIVE should always be available
        return True

    def _initialize_converter(self, converter_type: ConverterType) -> bool:
        """Initialize converter if needed."""
        # Check cache
        if converter_type in self._initialization_status:
            return self._initialization_status[converter_type]

        try:
            # Converter-specific initialization
            if converter_type == ConverterType.SPARK:
                # Initialize Spark session
                from pyspark.sql import SparkSession

                SparkSession.builder.getOrCreate()
                self._initialization_status[converter_type] = True
                return True

            else:
                # Other converters don't need special initialization
                self._initialization_status[converter_type] = True
                return True

        except Exception as e:
            self.logger.error(f"Failed to initialize {converter_type.value}: {e}")
            self._initialization_status[converter_type] = False
            return False

    def _execute_conversion(
        self,
        converter_type: ConverterType,
        input_file: Path,
        output_file: Path,
        options: Dict[str, Any],
    ) -> bool:
        """Execute conversion with a specific converter."""
        converter = self._converter_registry.get(converter_type)

        if not converter:
            raise ValueError(f"No converter registered for {converter_type.value}")

        # Add timeout handling
        self.CONVERTER_TIMEOUT.get(converter_type, 300)

        # For now, execute directly (timeout handling would require threading)
        # In production, use concurrent.futures or asyncio
        return converter(input_file, output_file, options)

    def _classify_error(self, exception: Exception, error_msg: str) -> FallbackReason:
        """Classify an error to determine fallback reason."""
        error_msg_lower = error_msg.lower()

        # Check for specific error patterns
        if "memory" in error_msg_lower or "heap" in error_msg_lower:
            return FallbackReason.MEMORY_ERROR

        elif "timeout" in error_msg_lower or "timed out" in error_msg_lower:
            return FallbackReason.TIMEOUT

        elif "format" in error_msg_lower or "unsupported" in error_msg_lower:
            return FallbackReason.FORMAT_NOT_SUPPORTED

        elif "initialize" in error_msg_lower or "startup" in error_msg_lower:
            return FallbackReason.INITIALIZATION_FAILED

        # Default to general conversion error
        return FallbackReason.CONVERSION_ERROR

    def _summarize_reasons(self, attempts: List[FallbackAttempt]) -> Dict[str, int]:
        """Summarize failure reasons."""
        reasons = {}
        for attempt in attempts:
            reason = attempt.reason.value
            reasons[reason] = reasons.get(reason, 0) + 1
        return reasons
