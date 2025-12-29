"""No-op tracer implementation for when OpenTelemetry is not installed."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any


class NoOpSpan:
    """No-op span that does nothing."""

    def set_attribute(self, key: str, value: Any) -> None:
        """No-op set attribute."""
        pass

    def set_status(self, status: Any) -> None:
        """No-op set status."""
        pass

    def record_exception(self, exception: BaseException) -> None:
        """No-op record exception."""
        pass

    def end(self) -> None:
        """No-op end."""
        pass

    def __enter__(self) -> "NoOpSpan":
        """Context manager enter."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        pass


class NoOpTracer:
    """No-op tracer that returns no-op spans."""

    @contextmanager
    def start_as_current_span(
        self, name: str, **kwargs: Any
    ) -> Iterator[NoOpSpan]:
        """Return a no-op span context manager."""
        yield NoOpSpan()

    def start_span(self, name: str, **kwargs: Any) -> NoOpSpan:
        """Return a no-op span."""
        return NoOpSpan()
