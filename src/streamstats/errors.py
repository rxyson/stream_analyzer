class StreamStatsError(Exception):
    """Базовые ошибки для всех ошибок streamstats."""


class UnsupportedFormatError(StreamStatsError):
    """Ошибка, возникающая при попытке использовать неподдерживаемый формат."""


class InvalidEventError(StreamStatsError):
    """Событие из входного файла не прошло проверку: нет поля или значение недопустимо."""


class InvalidTimestampError(InvalidEventError):
    """Значение timestamp нельзя разобрать как время в формате ISO 8601."""


class CLIConfigError(StreamStatsError):
    """Аргументы командной строки нельзя выполнить."""
