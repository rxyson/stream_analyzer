import csv
import json
from collections.abc import Iterator
from pathlib import Path

from .errors import InvalidEventError, UnsupportedFormatError
from .models import Event, parse_event


def read_jsonl_lines(path: str | Path) -> Iterator[tuple[int, str]]:
    """Читает строки из файла JSONL и возвращает их как кортежи (номер строки, строка)."""

    file_path = Path(path)

    with file_path.open(encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            yield number, line


def parse_jsonl_line(line: str) -> Event:
    """Делает словарь из JSONL и превращает его в Event или вызывает InvalidEventError."""

    try:
        record = json.loads(line)
    except json.JSONDecodeError as error:
        raise InvalidEventError(f"Ошибка JSON: {line!r}") from error

    if not isinstance(record, dict):
        raise InvalidEventError(f"JSON не является объектом: {line!r}")

    return parse_event(record)


def read_csv_rows(path: Path) -> Iterator[tuple[int, dict]]:
    """Читает строки из CSV и возвращает их как кортежи (номер строки, словарь)."""

    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield reader.line_num, row


FORMATS = {"csv": (read_csv_rows, parse_event), "jsonl": (read_jsonl_lines, parse_jsonl_line)}


def get_format(name: str) -> tuple:
    """Возвращает пару (читатель, превращатель) для формата или возбуждает UnsupportedFormatError."""

    try:
        return FORMATS[name]
    except KeyError as error:
        raise UnsupportedFormatError(
            f"Формат {name!r} не поддерживается. Доступные: {', '.join(sorted(FORMATS))}"
        ) from error
