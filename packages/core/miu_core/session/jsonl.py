"""JSONL-based session storage implementation."""

import json
import uuid
from pathlib import Path

from miu_core.models import Message
from miu_core.paths import MiuPaths
from miu_core.session.base import SessionStorageBase


class JSONLSessionStorage(SessionStorageBase):
    """JSONL-based session persistence.

    Stores one message per line as JSON for efficient appending and streaming.
    """

    def __init__(
        self,
        session_id: str | None = None,
        base_dir: Path | None = None,
        working_dir: str | None = None,  # Deprecated, kept for backward compat
    ) -> None:
        """Initialize JSONL storage.

        Args:
            session_id: Session ID, auto-generated if None.
            base_dir: Base directory, defaults to MiuPaths.sessions.
            working_dir: Deprecated, ignored. Kept for backward compatibility.
        """
        _ = working_dir  # Suppress unused warning
        sid = session_id or str(uuid.uuid4())[:8]
        bdir = base_dir if base_dir is not None else MiuPaths.get().sessions
        super().__init__(session_id=sid, base_dir=bdir)

    @property
    def session_file(self) -> Path:
        """Path to the JSONL session file."""
        return self.base_dir / f"{self.session_id}.jsonl"

    def load(self) -> list[Message]:
        """Load messages from JSONL file."""
        if not self.exists():
            return []

        messages: list[Message] = []
        try:
            with open(self.session_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        messages.append(Message.model_validate(data))
        except (json.JSONDecodeError, OSError):
            return []

        return messages

    def save(self, messages: list[Message]) -> None:
        """Save messages to JSONL file."""
        self.base_dir.mkdir(parents=True, exist_ok=True)

        with open(self.session_file, "w", encoding="utf-8") as f:
            for msg in messages:
                line = msg.model_dump_json()
                f.write(line + "\n")

    def clear(self) -> None:
        """Clear session file."""
        if self.exists():
            self.session_file.unlink()
