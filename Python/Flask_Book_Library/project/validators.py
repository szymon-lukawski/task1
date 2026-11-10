import re
from datetime import date


# Allowed characters for free-text fields: unicode letters and digits, space
# and a small set of punctuation. Everything else (e.g. < > " / ; = ` { })
# is rejected, so HTML/JS payloads cannot be stored in the database.
TEXT_PATTERN = re.compile(r"^[\w .,'&():!?-]+$")

BOOK_TYPES = ('2days', '5days', '10days')


def validate_text(field, value, max_length=64):
    if not isinstance(value, str):
        raise ValueError(f'{field} must be a string')
    value = value.strip()
    if not value:
        raise ValueError(f'{field} must not be empty')
    if len(value) > max_length:
        raise ValueError(f'{field} must be at most {max_length} characters long')
    if not TEXT_PATTERN.match(value):
        raise ValueError(f'{field} contains forbidden characters')
    return value


def validate_int(field, value, min_value, max_value):
    # Form data arrives as strings, JSON may carry ints - accept both, but not bools/floats
    if isinstance(value, bool):
        raise ValueError(f'{field} must be an integer')
    if isinstance(value, str) and re.fullmatch(r'\s*-?\d+\s*', value):
        value = int(value)
    if not isinstance(value, int):
        raise ValueError(f'{field} must be an integer')
    if not min_value <= value <= max_value:
        raise ValueError(f'{field} must be between {min_value} and {max_value}')
    return value


def validate_year(field, value):
    return validate_int(field, value, 1, date.today().year)


def validate_age(field, value):
    return validate_int(field, value, 1, 120)


def validate_book_type(field, value):
    if value not in BOOK_TYPES:
        raise ValueError(f'{field} must be one of: {", ".join(BOOK_TYPES)}')
    return value
