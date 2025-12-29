#!/usr/bin/env python3
"""Release automation script for miumono.

Usage:
    python scripts/release.py 0.2.0

This script:
1. Bumps version across all packages
2. Commits the version change
3. Creates a git tag
4. Pushes to origin (triggers release workflow)
"""

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command and return result."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def release(version: str) -> None:
    """Create a release for the given version."""
    tag = f"v{version}"

    print(f"\nReleasing {tag}...")

    # Check we're on main branch
    result = run(["git", "branch", "--show-current"], check=False)
    if result.returncode != 0 or result.stdout.strip() != "main":
        print("Error: Must be on main branch to release")
        sys.exit(1)

    # Check for uncommitted changes
    result = run(["git", "status", "--porcelain"], check=False)
    if result.stdout.strip():
        print("Error: Working directory has uncommitted changes")
        sys.exit(1)

    # Check tag doesn't already exist
    result = run(["git", "tag", "-l", tag], check=False)
    if result.stdout.strip():
        print(f"Error: Tag {tag} already exists")
        sys.exit(1)

    # Bump versions
    print("\n1. Bumping versions...")
    bump_script = Path("scripts/bump_version.py")
    if not bump_script.exists():
        print("Error: scripts/bump_version.py not found")
        sys.exit(1)

    result = run([sys.executable, str(bump_script), version])
    if result.returncode != 0:
        print(f"Error: Version bump failed\n{result.stderr}")
        sys.exit(1)

    # Commit
    print("\n2. Committing version bump...")
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", f"chore: release {tag}"])

    # Tag
    print("\n3. Creating tag...")
    run(["git", "tag", "-a", tag, "-m", f"Release {tag}"])

    # Push
    print("\n4. Pushing to origin...")
    run(["git", "push", "origin", "main", "--tags"])

    print(f"\n{tag} release pushed!")
    print("GitHub Actions will now publish to PyPI.")
    print("Monitor at: https://github.com/vanducng/miumono/actions")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/release.py <version>")
        print("Example: python scripts/release.py 0.2.0")
        sys.exit(1)

    version = sys.argv[1]
    if version.startswith("v"):
        version = version[1:]

    release(version)


if __name__ == "__main__":
    main()
