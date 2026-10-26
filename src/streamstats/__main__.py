import argparse
import logging
import sys
from pathlib import Path

from .analysis import Stats
from .errors import CLIConfigError, InvalidEventError, StreamStatsError
from .parsers import FORMATS, get_format
from .report import build_report, write_report

logger = logging.getLogger("streamstats")


def build_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""

    parser = argparse.ArgumentParser(
        prog="streamstats",
        description="Потоковый анализатор событий из CSV и JSONL.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Анализировать входные файлы.",
    )

    analyze_parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="Пути к входным файлам.",
    )

    analyze_parser.add_argument(
        "--format",
        required=True,
        choices=sorted(FORMATS),
        help="Формат входных данных.",
    )

    analyze_parser.add_argument(
        "--output",
        type=Path,
        default=Path("report.json"),
        help="Путь для JSON-отчёта (по умолчанию report.json).",
    )

    analyze_parser.add_argument(
        "--skip-invalid",
        action="store_true",
        help="Пропускать некорректные записи вместо остановки.",
    )

    return parser


def check_paths(inputs: list[Path], output: Path) -> None:
    """Проверяет, что входные файлы существуют и папка для отчёта есть."""

    for path in inputs:
        if not path.is_file():
            raise CLIConfigError(f"Входной файл не найден: {path}")

    if not output.parent.is_dir():
        raise CLIConfigError(f"Папка для отчёта не существует: {output.parent}")


def analyze_files(inputs: list[Path], fmt: str, skip_invalid: bool) -> Stats:
    """Обрабатывает файлы по очереди и копит общую статистику."""

    reader, to_event = get_format(fmt)
    stats = Stats()

    for path in inputs:
        for line_number, raw_record in reader(path):
            try:
                event = to_event(raw_record)
            except InvalidEventError as error:
                if skip_invalid:
                    logger.warning(f"{path}, строка {line_number} пропущена: {error}")
                    stats.skip()
                    continue
                raise InvalidEventError(f"{path}, строка {line_number}: {error}") from error

            stats.add(event)

    return stats


def main(argv: list[str] | None = None) -> int:
    """Разбирает аргументы, анализирует файлы, пишет отчёт."""

    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="{levelname}: {message}",
        style="{",
    )

    try:
        check_paths(args.inputs, args.output)
        stats = analyze_files(args.inputs, args.format, args.skip_invalid)
    except StreamStatsError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2

    write_report(build_report(stats), args.output)
    logger.info(f"Отчёт сохранён: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
