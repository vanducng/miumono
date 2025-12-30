#!/usr/bin/env python3
"""Demo script to showcase the Miu Code TUI features."""

import os
import sys

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages", "miu_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages", "miu_core"))


def showcase_tui_components():
    """Showcase the TUI components and structure."""
    print("🎯 Miu Code TUI - Terminal User Interface")
    print("=" * 50)

    print("\n📱 TUI Components:")
    print("1. App Framework: Textual-based application (app.py)")
    print("2. Chat Interface: Streaming conversation log (chat.py)")
    print("3. Animated Banner: ASCII art with gradient animation (banner.py)")
    print("4. Loading Spinner: Braille spinner with color wave (loading.py)")
    print("5. Theme System: Brand colors and gradients (theme.py)")

    print("\n🎨 Visual Features:")
    print("- Teal/Cyan brand color scheme (#1ABC9C)")
    print("- Animated ASCII logo with color cascade")
    print("- Real-time streaming chat messages")
    print("- Tool execution indicators")
    print("- Rich markdown rendering")
    print("- Smooth scrolling and animations")

    print("\n⌨️  Key Bindings:")
    print("- Ctrl+C: Quit application")
    print("- Ctrl+N: Start new session")
    print("- Ctrl+L: Clear chat history")
    print("- Enter: Send message")

    print("\n🚀 To run the TUI:")
    print("  uv run python -m miu_code.tui.app")
    print("  # or")
    print("  uv run miu tui")

    # Show the ASCII logo
    print("\n🎨 ASCII Logo:")
    logo = r"""
  _ __ ___ (_)_   _
 | '_ ` _ \| | | | |
 | | | | | | | |_| |
 |_| |_| |_|_|\__,_|
"""
    print(logo)

    print("\n🔧 Technical Stack:")
    print("- Framework: Textual (Rich TUI library)")
    print("- Styling: CSS-like styling with brand colors")
    print("- Animation: Custom gradient and spinner effects")
    print("- Streaming: Real-time text streaming support")
    print("- Agent Integration: CodingAgent with tool execution")


if __name__ == "__main__":
    showcase_tui_components()
