from typing import Any, Optional


class LayoutCache:
    def __init__(self):
        self._cache = {}

    def get(self, key) -> Optional[dict[Any, tuple[float, float]]]:
        return self._cache.get(key)

    def set(self, key, value) -> None:
        self._cache[key] = value

    def clear(self) -> None:
        """Clear all cached layouts"""
        self._cache.clear()


