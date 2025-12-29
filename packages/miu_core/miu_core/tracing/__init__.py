"""OpenTelemetry tracing integration for miu-core.

Install with: pip install miu-core[tracing]
"""

from miu_core.tracing.types import SpanKind, TracingConfig

__all__ = ["SpanKind", "TracingConfig", "get_tracer", "setup_tracing"]


def get_tracer(name: str = "miu") -> object:
    """Get a tracer instance.

    Returns a no-op tracer if OpenTelemetry is not installed.
    """
    try:
        from miu_core.tracing.otel import get_tracer as _get_tracer

        return _get_tracer(name)
    except ImportError:
        from miu_core.tracing.noop import NoOpTracer

        return NoOpTracer()  # type: ignore[return-value]


def setup_tracing(config: TracingConfig | None = None) -> object:
    """Setup OpenTelemetry tracing.

    Args:
        config: Tracing configuration. Uses defaults if not provided.

    Returns:
        Configured tracer instance.

    Raises:
        ImportError: If OpenTelemetry packages are not installed.
    """
    try:
        from miu_core.tracing.otel import setup_tracing as _setup

        return _setup(config)
    except ImportError as e:
        raise ImportError(
            "OpenTelemetry packages not installed. "
            "Install with: pip install miu-core[tracing]"
        ) from e
