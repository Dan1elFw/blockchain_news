def compact(value: str) -> str:
    """Remove useless trailing zeros from a numeric string."""
    if not value or not _is_numeric(value):
        return value
    if '.' in value:
        integer_part, decimal_part = value.split('.', 1)
        index = len(decimal_part) - 1
        while index >= 0 and decimal_part[index] == '0':
            index -= 1
        if index == -1:
            return integer_part
        return f'{integer_part}.{decimal_part[:index + 1]}'
    return value


def format_percent(value: str) -> str:
    """Format a numeric string as a percentage with sign, 2 decimal places."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return '--'
    sign = '+' if num > 0 else ''
    return f'{sign}{num:.2f}%'


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
