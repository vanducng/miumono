"""Base agent interface."""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from miu_core.models import Message, Response
from miu_core.providers.base import LLMProvider
from miu_core.tools.registry import ToolRegistry


class AgentConfig(BaseModel):
    """Agent configuration."""

    system_prompt: str = "You are a helpful AI assistant."
    max_iterations: int = 10


class Memory:
    """Simple message memory."""

    def __init__(self) -> None:
        self._messages: list[Message] = []

    @property
    def messages(self) -> list[Message]:
        return self._messages.copy()

    def add(self, message: Message) -> None:
        self._messages.append(message)

    def clear(self) -> None:
        self._messages.clear()


class Agent(ABC):
    """Abstract base class for agents."""

    def __init__(
        self,
        provider: LLMProvider,
        tools: ToolRegistry | None = None,
        config: AgentConfig | None = None,
    ) -> None:
        self.provider = provider
        self.tools = tools or ToolRegistry()
        self.config = config or AgentConfig()
        self.memory = Memory()

    @abstractmethod
    async def run(self, query: str) -> Response:
        """Process a query and return response."""
        ...
