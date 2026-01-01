"""Session storage using JSONL.

This module re-exports JSONLSessionStorage from miu_core for backward compatibility.
New code should import directly from miu_core.session.
"""

from miu_core.session import JSONLSessionStorage

# Backward compatibility alias
SessionStorage = JSONLSessionStorage
