from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque


@dataclass
class Inventory:
    counts: dict[str, int] = field(default_factory=dict)
    _history: deque[str] = field(default_factory=lambda: deque(maxlen=30))

    def add(self, item_id: str, amount: int = 1) -> None:
        if amount <= 0:
            return
        self.counts[item_id] = self.counts.get(item_id, 0) + amount
        for _ in range(min(amount, 3)):
            self._history.append(item_id)

    def has(self, item_id: str) -> bool:
        return self.count(item_id) > 0

    def count(self, item_id: str) -> int:
        return self.counts.get(item_id, 0)

    def remove(self, item_id: str, amount: int = 1) -> bool:
        if amount <= 0:
            return True
        current = self.count(item_id)
        if current < amount:
            return False
        remaining = current - amount
        if remaining <= 0:
            self.counts.pop(item_id, None)
        else:
            self.counts[item_id] = remaining
        return True

    def snapshot_for_ui(self, max_items: int = 6) -> str:
        if not self.counts:
            return ""

        recent: list[str] = []
        seen: set[str] = set()
        for item_id in reversed(self._history):
            if item_id in self.counts and item_id not in seen:
                recent.append(item_id)
                seen.add(item_id)
            if len(recent) >= max_items:
                break

        if not recent:
            recent = sorted(self.counts.keys())[:max_items]

        return ", ".join(f"{item_id}x{self.count(item_id)}" for item_id in recent)
