from typing import NamedTuple


class Token(NamedTuple):
    name: str
    value: str
    column: int
    row: int
