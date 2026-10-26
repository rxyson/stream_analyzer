from collections import Counter
from datetime import datetime

from .models import Event

ERROR_LEVELS = {"ERROR", "CRITICAL"}


def error_rank(item: tuple[str, int]) -> tuple[int, str]:
    """Признак сортировки: больше ошибок — раньше, при равенстве — по имени."""

    source, count = item
    return (-count, source)


class Stats:
    """Класс для хранения статистики по событиям."""

    def __init__(self) -> None:
        self.total = 0
        self.by_level = Counter()
        self.by_source = Counter()
        self.error_sources = Counter()
        self.first_timestamp: datetime | None = None
        self.last_timestamp: datetime | None = None
        self.skipped = 0

    def add(self, event: Event) -> None:
        """Добавляет событие в статистику."""

        self.total += 1
        self.by_level[event.level] += 1
        self.by_source[event.source] += 1

        if event.level in ERROR_LEVELS:
            self.error_sources[event.source] += 1

        if self.first_timestamp is None or event.timestamp < self.first_timestamp:
            self.first_timestamp = event.timestamp

        if self.last_timestamp is None or event.timestamp > self.last_timestamp:
            self.last_timestamp = event.timestamp

    def skip(self) -> None:
        """Учитывает одну пропущенную строку."""

        self.skipped += 1

    def top_error_sources(self, limit: int = 5) -> list[tuple[str, int]]:
        """Возвращает источники с наибольшим числом ошибок, не больше limit штук."""

        ranked = sorted(self.error_sources.items(), key=error_rank)
        return ranked[:limit]
