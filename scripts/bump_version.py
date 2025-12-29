#!/usr/bin/env python3
"""Bump version across all packages in the monorepo.

Usage:
    python scripts/bump_version.py 0.2.0
"""

import re
import sys
from pathlib import Path


def bump_version(new_version: str) -> None:
    """Update version in all package pyproject.toml files."""
    packages_dir = Path("packages")

    if not packages_dir.exists():
        print("Error: packages/ directory not found")
        sys.exit(1)

    updated = 0
    for pkg_dir in packages_dir.iterdir():
        if not pkg_dir.is_dir():
            continue

        pyproject = pkg_dir / "pyproject.toml"
        if not pyproject.exists():
            continue

        content = pyproject.read_text()
        new_content = re.sub(
            r'version = "[^"]+"',
            f'version = "{new_version}"',
            content,
        )

        if content != new_content:
            pyproject.write_text(new_content)
            print(f"Updated {pkg_dir.name} to {new_version}")
            updated += 1

    if updated == 0:
        print("No packages updated")
    else:
        print(f"\nUpdated {updated} packages to version {new_version}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py <version>")
        print("Example: python scripts/bump_version.py 0.2.0")
        sys.exit(1)

    version = sys.argv[1]

    # Basic version validation
    if not re.match(r"^\d+\.\d+\.\d+", version):
        print(f"Error: Invalid version format: {version}")
        print("Expected format: X.Y.Z (e.g., 0.2.0)")
        sys.exit(1)

    bump_version(version)


if __name__ == "__main__":
    main()
