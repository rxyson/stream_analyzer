import json
from datetime import datetime
from pathlib import Path

from .analysis import Stats


def format_time(value: datetime | None) -> str | None:
    """Возвращает время, как строку, а если его нет, то пустоту."""

    if value is None:
        return None
    return value.isoformat()


def build_report(stats: Stats) -> dict:
    """Сбор отчета в виде словаря для JSON файла."""

    top = []
    for source, count in stats.top_error_sources():
        top.append({"source": source, "count": count})

    return {
        "total_events": stats.total,
        "skipped_lines": stats.skipped,
        "first_timestamp": format_time(stats.first_timestamp),
        "last_timestamp": format_time(stats.last_timestamp),
        "levels": dict(sorted(stats.by_level.items())),
        "sources": dict(sorted(stats.by_source.items())),
        "top_error_sources": top,
    }


def write_report(report: dict, path: Path) -> None:
    """Записывает отчёт в файл как JSON с отступами и кириллицей без кодов."""

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
        file.write("\n")
