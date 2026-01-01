"""Abstract base class for session storage."""

from abc import ABC, abstractmethod
from pathlib import Path

from miu_core.models import Message


class SessionStorageBase(ABC):
    """Abstract base for session storage implementations.

    Subclasses must implement load, save, clear, and exists methods.
    """

    def __init__(self, session_id: str, base_dir: Path) -> None:
        """Initialize storage with session ID and base directory.

        Args:
            session_id: Unique session identifier
            base_dir: Base directory for session files
        """
        self.session_id = session_id
        self.base_dir = base_dir

    @property
    @abstractmethod
    def session_file(self) -> Path:
        """Path to the session file."""
        ...

    @abstractmethod
    def load(self) -> list[Message]:
        """Load messages from storage.

        Returns:
            List of messages, empty if session doesn't exist.
        """
        ...

    @abstractmethod
    def save(self, messages: list[Message]) -> None:
        """Save messages to storage.

        Args:
            messages: List of messages to save.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear session data."""
        ...

    def exists(self) -> bool:
        """Check if session file exists."""
        return self.session_file.exists()
