"""Shared fixtures for studio package tests."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from miu_studio.main import create_app
from miu_studio.services.chat_service import ChatService
from miu_studio.services.session_manager import SessionManager


@pytest.fixture
def temp_session_dir() -> Path:
    """Create temporary directory for sessions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def session_manager(temp_session_dir: Path) -> SessionManager:
    """Create session manager with temp directory."""
    return SessionManager(session_dir=str(temp_session_dir))


@pytest.fixture
def chat_service(session_manager: SessionManager) -> ChatService:
    """Create chat service with test session manager."""
    return ChatService(session_manager=session_manager)


@pytest.fixture
def client(session_manager: SessionManager) -> TestClient:
    """Create test client with injected session manager."""
    with patch("miu_studio.api.routes.sessions._session_manager", session_manager):
        app = create_app()
        yield TestClient(app)


@pytest.fixture
def client_with_chat(
    session_manager: SessionManager,
    chat_service: ChatService,
) -> TestClient:
    """Create test client with both session and chat services."""
    with (
        patch("miu_studio.api.routes.sessions._session_manager", session_manager),
        patch("miu_studio.api.routes.chat._chat_service", chat_service),
    ):
        app = create_app()
        yield TestClient(app)


@pytest.fixture
def session_id(client: TestClient) -> str:
    """Create a session and return its ID."""
    response = client.post("/api/v1/sessions/", json={"name": "Test Session"})
    return response.json()["id"]


@pytest.fixture
def session_with_messages(client: TestClient, session_id: str) -> str:
    """Create session with some messages and return its ID."""
    # Add messages through the session manager directly if needed
    return session_id


@pytest.fixture
def valid_uuid() -> str:
    """Return a valid UUID that doesn't exist."""
    return "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def invalid_uuids() -> list[str]:
    """Return list of invalid UUID formats."""
    return [
        "invalid-id",
        "12345",
        "not-a-uuid",
        "../etc/passwd",
        "a" * 36,
        "00000000-0000-0000-0000-00000000000g",
    ]
