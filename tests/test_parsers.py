from pathlib import Path

import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError, UnsupportedFormatError
from streamstats.models import parse_event
from streamstats.parsers import get_format, parse_jsonl_line, read_csv_rows, read_jsonl_lines

TEST_FILES = Path("tests/test_files")


"""Тесты JSONL."""


def test_read_jsonl_skips_empty_lines_and_keeps_numbers():
    numbers = [number for number, line in read_jsonl_lines(TEST_FILES / "valid.jsonl")]

    assert numbers == [1, 3]


def test_parse_jsonl_line_returns_event():
    lines = list(read_jsonl_lines(TEST_FILES / "valid.jsonl"))
    _number, line = lines[0]
    event = parse_jsonl_line(line)

    assert event.level == "INFO"
    assert event.source == "loader"
    assert event.message == "Начало"


def test_parse_jsonl_broken_json():
    with pytest.raises(InvalidEventError):
        parse_jsonl_line("qwerty")


def test_parse_jsonl_non_object():
    with pytest.raises(InvalidEventError):
        parse_jsonl_line("[1, 2, 3]")


def test_parse_jsonl_time_without_timezone():
    line = (
        '{"timestamp": "2026-10-07T12:00:00", "level": "INFO", '
        '"source": "loader", "message": "Начало"}'
    )
    with pytest.raises(InvalidTimestampError):
        parse_jsonl_line(line)


def test_broken_jsonl_by_number():
    bad_numbers = []
    for number, line in read_jsonl_lines(TEST_FILES / "broken.jsonl"):
        try:
            parse_jsonl_line(line)
        except InvalidEventError:
            bad_numbers.append(number)

    assert bad_numbers == [2]


"""Тесты CSV."""


def test_read_csv_rows_numbers():
    rows = list(read_csv_rows(TEST_FILES / "valid.csv"))

    assert [number for number, row in rows] == [2, 4]
    assert rows[0][1]["message"] == "Начало, шаг 1"


def test_csv_row_becomes_event():
    rows = list(read_csv_rows(TEST_FILES / "valid.csv"))
    _number, row = rows[0]
    event = parse_event(row)

    assert event.source == "loader"
    assert event.message == "Начало, шаг 1"


def test_broken_csv_row():
    rows = list(read_csv_rows(TEST_FILES / "broken.csv"))
    number, row = rows[1]

    assert number == 3
    with pytest.raises(InvalidEventError):
        parse_event(row)


"""Проверка форматов."""


def test_get_format():
    assert get_format("jsonl") == (read_jsonl_lines, parse_jsonl_line)
    assert get_format("csv") == (read_csv_rows, parse_event)


def test_get_format_unknown():
    with pytest.raises(UnsupportedFormatError):
        get_format("xml")


"""Проверка пустых файлов и Unicode."""


def test_empty_jsonl():
    assert list(read_jsonl_lines(TEST_FILES / "empty.jsonl")) == []


def test_empty_csv():
    assert list(read_csv_rows(TEST_FILES / "empty.csv")) == []


def test_csv_with_only_header():
    assert list(read_csv_rows(TEST_FILES / "header_only.csv")) == []


def test_unicode_source_and_message():
    lines = list(read_jsonl_lines(TEST_FILES / "unicode.jsonl"))
    _number, line = lines[0]
    event = parse_jsonl_line(line)

    assert event.source == "загрузчик"
    assert event.message == "Файл «отчёт.csv» не найден"
