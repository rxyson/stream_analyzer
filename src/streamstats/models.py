from dataclasses import dataclass
from datetime import datetime

from .errors import InvalidEventError, InvalidTimestampError

LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
REQUIRED_FIELDS = ("timestamp", "level", "source", "message")


@dataclass
class Event:
    """Представление события в потоке данных."""

    timestamp: datetime
    level: str
    source: str
    message: str


def parse_event(record: dict) -> Event:
    """Превращает словарь записи в Event или вызывает InvalidEventError."""

    for field in REQUIRED_FIELDS:
        if field not in record:
            raise InvalidEventError(f"Отсутствует поле {field!r} в событии.")
        if not isinstance(record[field], str):
            raise InvalidEventError(f"Поле {field!r} должно быть строкой.")

    level = record["level"]
    if level not in LEVELS:
        raise InvalidEventError(f"Недопустимый уровень события: {level!r}.")

    source = record["source"]
    if not source.strip():
        raise InvalidEventError("Поле 'source' не может быть пустым.")

    raw_timestamp = record["timestamp"]
    try:
        timestamp = datetime.fromisoformat(raw_timestamp)
    except ValueError as error:
        raise InvalidTimestampError(
            f"{raw_timestamp!r} не является корректным временем."
        ) from error

    if timestamp.tzinfo is None:
        raise InvalidTimestampError(f"{raw_timestamp!r} не содержит информации о часовом поясе.")

    return Event(timestamp=timestamp, level=level, source=source, message=record["message"])