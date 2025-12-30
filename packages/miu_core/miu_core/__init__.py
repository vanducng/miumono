"""miu-core: Core framework library for miu AI agent."""

from miu_core.version import get_version

__version__ = get_version()

# Lazy imports to avoid circular dependencies
__all__ = [
    "AgentMode",
    "ModeManager",
    "Orchestrator",
    "OrchestratorConfig",
    "Pipeline",
    "PipelineConfig",
    "Router",
    "RouterConfig",
    "UsageStats",
    "UsageTracker",
    "__version__",
]


def __getattr__(name: str) -> object:
    """Lazy import modules."""
    if name in (
        "Orchestrator",
        "OrchestratorConfig",
        "Pipeline",
        "PipelineConfig",
        "Router",
        "RouterConfig",
    ):
        from miu_core import patterns

        return getattr(patterns, name)

    if name in ("UsageStats", "UsageTracker"):
        from miu_core import usage

        return getattr(usage, name)

    if name in ("AgentMode", "ModeManager"):
        from miu_core import modes

        return getattr(modes, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
