# Потоковый анализатор файлов

Потоковый анализатор событий из файлов CSV и JSONL. Читает файлы построчно,
не загружая их в память целиком, проверяет каждое событие и строит JSON-отчёт.

## Возможности

- **Потоковая обработка.** Файлы читаются построчно.
- **Два формата.** CSV с заголовком и JSONL.
- **Проверка событий.** Для каждой записи проверяются наличие и тип всех
  обязательных полей, допустимый уровень, непустой источник и корректное
  время ISO 8601 с часовым поясом.
- **Статистика:**
  - общее число событий;
  - количество событий каждого уровня;
  - количество событий каждого источника;
  - top-5 источников ошибок уровня `ERROR` и `CRITICAL`;
  - первая и последняя временная метка с учётом часовых поясов;
  - число пропущенных строк.
- **Несколько файлов.** Статистика по всем файлам объединяется в один отчёт.
- **JSON-отчёт.** Читаемый отчёт с отступами, кириллица сохраняется.
- **Два режима для некорректных строк:**
  - по умолчанию останавливается на ошибке с кодом выхода `2`;
  - с `--skip-invalid` строка пропускается, пишется предупреждение,
    число пропусков попадает в отчёт.
- **Понятные ошибки.** Неизвестный формат, отсутствующий входной файл
  или несуществующая папка для отчёта дают сообщение и код с выходом `2`.
- **Тесты.** Unit-тесты парсеров, тесты командной строки, включая пустые файлы, повреждённые строки и Unicode.

## Замечания

- **Регистр:** `info` — некорректное событие.
- **`source` из одних пробелов** считается пустым.
- **Время без часового пояса** — некорректное событие.
- **Top-5 при равенстве** упорядочен по алфавиту.

## Требования

- Python 3.11+

## Процесс установки

1) Клонируйте репозиторий
```shell
git clone https://github.com/rxyson/stream_analyzer
cd stream_analyzer
```

2) Создайте виртуальное окружение

MacOs / Linux
```shell
python3 -m venv .venv
source .venv/bin/activate
```

Windows (Powershell)
```shell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows (Command Promt / cmd)
```shell
py -m venv .venv
.venv\Scripts\activate.bat
```

3) Установите пакет с зависимостями

```shell
python -m pip install -e ".[dev]"
```

## Запуск

```bash
python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl [--output REPORT.json] [--skip-invalid]
```

- `INPUT` — один или несколько файлов, статистика по ним объединяется;
- `--format` — формат входных файлов: `csv` (с заголовком) или `jsonl`;
- `--output` — путь к отчёту, по умолчанию `report.json`;
- `--skip-invalid` — пропускать некорректные строки вместо остановки.

Просмотр справки
```bash
python -m streamstats --help
```

Просмотр справки команды "analyze"
```bash
python -m streamstats analyze --help
```

## Модель события

| Поле | Требование |
|---|---|
| `timestamp` | время ISO 8601 **с часовым поясом**|
| `level` | `DEBUG`, `INFO`, `WARNING`, `ERROR` или `CRITICAL` |
| `source` | непустая строка |
| `message` | строка |

## Отчёт

```json
{
  "total_events": 7,
  "skipped_lines": 0,
  "first_timestamp": "2026-10-07T12:00:00+03:00",
  "last_timestamp": "2026-10-07T12:00:05+03:00",
  "levels": {"CRITICAL": 2, "ERROR": 4, "INFO": 1},
  "sources": {"api": 2, "db": 3, "loader": 2},
  "top_error_sources": [
    {"source": "db", "count": 3},
    {"source": "api", "count": 2},
    {"source": "loader", "count": 1}
  ]
}
```

## Пример:

```bash
python -m streamstats analyze tests/test_files/valid.jsonl tests/test_files/errors.jsonl --format jsonl --output report.json
```

## Пример: файл с повреждённой строкой

В файле `tests/test_files/broken.jsonl` вторая строка не является JSON:

```
{"timestamp": "2026-10-07T12:00:00+03:00", "level": "INFO", "source": "loader", "message": "Начало"}
qwerty
{"timestamp": "2026-10-07T12:00:05+03:00", "level": "ERROR", "source": "db", "message": "Нет связи"}
```

### Режим по умолчанию: остановка

```bash
python -m streamstats analyze tests/test_files/broken.jsonl --format jsonl --output report.json
```

```
Ошибка: tests/test_files/broken.jsonl, строка 2: Ошибка JSON: 'qwerty'
```

### Режим `--skip-invalid`: пропуск

```bash
python -m streamstats analyze tests/test_files/broken.jsonl --format jsonl --output report.json --skip-invalid
```

```
WARNING: tests/test_files/broken.jsonl, строка 2 пропущена: Ошибка JSON: 'qwerty'
INFO: Отчёт сохранён: report.json
```

Плохая строка пропущена, остальные учтены. В отчёте `report.json`:

```json
{
  "total_events": 2,
  "skipped_lines": 1,
  "first_timestamp": "2026-10-07T12:00:00+03:00",
  "last_timestamp": "2026-10-07T12:00:05+03:00",
  "levels": {
    "ERROR": 1,
    "INFO": 1
  },
  "sources": {
    "db": 1,
    "loader": 1
  },
  "top_error_sources": [
    {
      "source": "db",
      "count": 1
    }
  ]
}
```

## Структура проекта

<pre>

stream_analyzer/
├── src/
│   └── streamstats/
│       ├── __init__.py
│       ├── __main__.py
│       ├── analysis.py
│       ├── errors.py
│       ├── models.py
│       ├── parsers.py
│       └── report.py
├── tests/
│   ├── test_files/
│   │   ├── broken.csv
│   │   ├── broken.jsonl
│   │   ├── empty.csv
│   │   ├── empty.jsonl
│   │   ├── errors.jsonl
│   │   ├── header_only.csv
│   │   ├── unicode.jsonl
│   │   ├── valid.csv
│   │   └── valid.jsonl
│   ├── test_cli.py
│   └── test_parsers.py
├── .gitignore
├── pyproject.toml
└── README.md

</pre>

## Назначение модулей

- errors.py – иерархия ошибок.
- models.py – модель события Event и функция parse_event, которая проверяет запись и превращает её в событие.
- parsers.py – генераторы построчного чтения CSV и JSONL и выбор формата через get_format.
- analysis.py – класс Stats, который собирает статистику.
- report.py – сборка итогового отчёта и его запись в JSON-файл.
- `__main__.py` – командный интерфейс приложения.
- tests/ – автоматические тесты парсеров и CLI.
- tests/test_files/ – тестовые входные файлы: корректные, повреждённые, пустые и с кириллицей.
- pyproject.toml – метаданные проекта и настройки инструментов разработки.
- .gitignore – список файлов и папок, которые не попадают в репозиторий.

## Тестирование

Команды запускаются из корня проекта: тесты ищут данные по пути
`tests/test_files`.

```bash
python -m pytest
ruff check .
```

## Автор

Цыганков Никита Эдуардович | М8О-105БВ-26