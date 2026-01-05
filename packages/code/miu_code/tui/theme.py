"""Miu brand theme colors and utilities."""

# Miu brand palette (muted forest green - dark mode friendly)
MIU_COLORS = {
    "primary": "#1B7B42",  # muted forest green (main brand color)
    "primary_light": "#1E8449",  # soft green
    "secondary": "#166534",  # dark forest green
    "accent": "#14532D",  # deep forest
    "highlight": "#22A055",  # subtle highlight (not too bright)
}

# Gradient sequence for animations
GRADIENT_SEQUENCE = [
    "#22A055",  # subtle highlight
    "#1E8449",  # soft green
    "#1B7B42",  # muted forest green
    "#166534",  # dark forest green
    "#14532D",  # deep forest
]

# Semantic colors
SEMANTIC_COLORS = {
    "user": "#3498DB",  # blue for user
    "assistant": "#1B7B42",  # muted green for agent
    "system": "#7F8C8D",  # gray for system
    "error": "#E74C3C",  # red for errors
    "accent": "#1B7B42",  # muted green accent
    "thinking": "#1E8449",  # soft green for thinking
}

# Alias for backward compatibility
VIBE_COLORS = {
    "gold": "#22A055",  # subtle highlight
    "orange_gold": "#1E8449",  # soft green
    "orange": "#1B7B42",  # muted forest green
    "orange_red": "#166534",  # dark forest green
    "red": "#14532D",  # deep forest
}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def interpolate_color(color1: str, color2: str, t: float) -> str:
    """Interpolate between two hex colors. t: 0.0 to 1.0."""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)

    return rgb_to_hex(r, g, b)


def get_gradient_color(progress: float) -> str:
    """Get color from gradient based on progress (0.0 to 1.0)."""
    if progress <= 0:
        return GRADIENT_SEQUENCE[0]
    if progress >= 1:
        return GRADIENT_SEQUENCE[-1]

    # Calculate position in gradient
    segment_count = len(GRADIENT_SEQUENCE) - 1
    segment = int(progress * segment_count)
    segment = min(segment, segment_count - 1)

    local_progress = (progress * segment_count) - segment

    return interpolate_color(
        GRADIENT_SEQUENCE[segment], GRADIENT_SEQUENCE[segment + 1], local_progress
    )
