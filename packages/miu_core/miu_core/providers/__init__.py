"""LLM providers."""

from miu_core.providers.base import LLMProvider, ToolSchema

__all__ = ["LLMProvider", "ToolSchema"]


# Lazy imports for optional providers
def __getattr__(name: str) -> type:
    if name == "AnthropicProvider":
        from miu_core.providers.anthropic import AnthropicProvider

        return AnthropicProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
