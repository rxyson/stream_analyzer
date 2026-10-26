import json
from pathlib import Path

import pytest

from streamstats.__main__ import analyze_files, main
from streamstats.errors import InvalidEventError

TEST_FILES = Path("tests/test_files")


def run_analyze(output: Path, inputs: list[str], fmt: str = "jsonl", skip: bool = False) -> int:
    """Запускает CLI на файлах из test_files и возвращает код выхода."""

    argv = ["analyze"]
    argv += [str(TEST_FILES / name) for name in inputs]
    argv += ["--format", fmt, "--output", str(output)]
    if skip:
        argv.append("--skip-invalid")
    return main(argv)


def read_report(path: Path) -> dict:
    """Читает JSON-отчёт как словарь."""

    return json.loads(path.read_text(encoding="utf-8"))


"""Проверка корректности данных."""


def test_valid_jsonl_report(tmp_path):
    output = tmp_path / "report.json"

    assert run_analyze(output, ["valid.jsonl"]) == 0

    report = read_report(output)
    assert report["total_events"] == 2
    assert report["skipped_lines"] == 0
    assert report["levels"] == {"ERROR": 1, "INFO": 1}
    assert report["sources"] == {"db": 1, "loader": 1}
    assert report["first_timestamp"] == "2026-10-07T12:00:00+03:00"
    assert report["last_timestamp"] == "2026-10-07T12:00:05+03:00"
    assert report["top_error_sources"] == [{"source": "db", "count": 1}]


def test_valid_csv_report(tmp_path):
    output = tmp_path / "report.json"

    assert run_analyze(output, ["valid.csv"], fmt="csv") == 0
    assert read_report(output)["total_events"] == 2


"""Поврежденные строки в обычном режиме."""


def test_broken_jsonl_stops_code_2(tmp_path):
    output = tmp_path / "report.json"

    assert run_analyze(output, ["broken.jsonl"]) == 2
    assert not output.exists()


def test_broken_jsonl_error():
    with pytest.raises(InvalidEventError, match="broken.jsonl, строка 2"):
        analyze_files([TEST_FILES / "broken.jsonl"], "jsonl", skip_invalid=False)


"""Поврежденные строки с режимом: '--skip-invalid'."""


def test_broken_csv_stops_code_2(tmp_path):
    output = tmp_path / "report.json"

    assert run_analyze(output, ["broken.csv"], fmt="csv") == 2


def test_broken_csv_error():
    with pytest.raises(InvalidEventError, match="broken.csv, строка 3"):
        analyze_files([TEST_FILES / "broken.csv"], "csv", skip_invalid=False)


"""Проверка нескольких файлов."""


def test_multiple_files(tmp_path):
    output = tmp_path / "report.json"

    assert run_analyze(output, ["valid.jsonl", "errors.jsonl"]) == 0

    report = read_report(output)
    assert report["total_events"] == 7
    assert report["top_error_sources"] == [
        {"source": "db", "count": 3},
        {"source": "api", "count": 2},
        {"source": "loader", "count": 1},
    ]
    assert report["first_timestamp"] == "2026-10-07T12:00:00+03:00"
    assert report["last_timestamp"] == "2026-10-07T12:00:05+03:00"


"""Проверка Unicode и пустых файлов."""


def test_unicode_report(tmp_path):
    output = tmp_path / "report.json"

    assert run_analyze(output, ["unicode.jsonl"]) == 0

    text = output.read_text(encoding="utf-8")
    assert "загрузчик" in text


def test_empty_report(tmp_path):
    output = tmp_path / "report.json"

    assert run_analyze(output, ["empty.jsonl"]) == 0

    report = read_report(output)
    assert report["total_events"] == 0
    assert report["first_timestamp"] is None
    assert report["top_error_sources"] == []


"""Ошибка запуска."""


def test_missing_input(tmp_path):
    output = tmp_path / "report.json"
    argv = ["analyze", str(tmp_path / "nope.jsonl"), "--format", "jsonl", "--output", str(output)]

    assert main(argv) == 2


def test_unknown_format(tmp_path):
    with pytest.raises(SystemExit) as exit_info:
        main(["analyze", str(TEST_FILES / "valid.jsonl"), "--format", "xml"])

    assert exit_info.value.code == 2
