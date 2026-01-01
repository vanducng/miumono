"""Truncation strategies for memory management."""

from enum import Enum

from miu_core.models import Message


class TruncationStrategy(str, Enum):
    """Strategy for truncating conversation history."""

    FIFO = "fifo"  # First In, First Out - remove oldest messages
    SLIDING = "sliding"  # Keep first + last N messages
    SUMMARIZE = "summarize"  # Placeholder for future summarization


# Model-specific token ratios (chars per token)
# These are empirically derived from tokenizer analysis
TOKEN_RATIOS: dict[str, float] = {
    "claude": 3.5,  # Claude uses ~3.5 chars per token
    "gpt": 4.0,  # GPT-4 uses ~4 chars per token
    "gemini": 3.8,  # Gemini uses ~3.8 chars per token
    "default": 4.0,  # Conservative default
}


def get_token_ratio(model: str | None = None) -> float:
    """Get chars-per-token ratio for a model.

    Args:
        model: Model name or provider prefix (e.g., "claude-3", "gpt-4", "gemini-2.0-flash")

    Returns:
        Chars per token ratio for estimation.
    """
    if model is None:
        return TOKEN_RATIOS["default"]

    model_lower = model.lower()
    for prefix, ratio in TOKEN_RATIOS.items():
        if prefix != "default" and prefix in model_lower:
            return ratio
    return TOKEN_RATIOS["default"]


def estimate_tokens(message: Message, model: str | None = None) -> int:
    """Estimate token count for a message.

    Uses model-specific ratios for improved accuracy.

    Args:
        message: Message to estimate tokens for.
        model: Optional model name for provider-specific ratio.

    Returns:
        Estimated token count.
    """
    content = message.content
    if isinstance(content, str):
        text = content
    else:
        text = " ".join(block.text if hasattr(block, "text") else str(block) for block in content)

    ratio = get_token_ratio(model)
    return int(len(text) / ratio) + 1


def truncate_fifo(messages: list[Message], max_tokens: int) -> tuple[list[Message], int]:
    """Truncate using FIFO strategy.

    Removes oldest messages (except first user message) until under limit.

    Returns: (truncated messages, tokens removed)
    """
    if not messages:
        return messages, 0

    total_tokens = sum(estimate_tokens(m) for m in messages)
    if total_tokens <= max_tokens:
        return messages, 0

    # Keep first message (usually important context)
    result = [messages[0]]
    tokens_kept = estimate_tokens(messages[0])

    # Add messages from end until we hit limit
    for msg in reversed(messages[1:]):
        msg_tokens = estimate_tokens(msg)
        if tokens_kept + msg_tokens <= max_tokens:
            result.insert(1, msg)
            tokens_kept += msg_tokens
        else:
            break

    tokens_removed = total_tokens - tokens_kept
    return result, tokens_removed


def truncate_sliding(
    messages: list[Message], max_tokens: int, keep_first: int = 1, keep_last: int = 10
) -> tuple[list[Message], int]:
    """Truncate using sliding window strategy.

    Keeps first N and last M messages.

    Returns: (truncated messages, tokens removed)
    """
    if len(messages) <= keep_first + keep_last:
        return messages, 0

    total_tokens = sum(estimate_tokens(m) for m in messages)

    # Keep first and last messages
    first = messages[:keep_first]
    last = messages[-keep_last:]
    result = first + last

    tokens_kept = sum(estimate_tokens(m) for m in result)
    tokens_removed = total_tokens - tokens_kept

    return result, tokens_removed
