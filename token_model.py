from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()

    INTEGER = auto()
    FLOAT = auto()
    CHAR = auto()
    STRING = auto()

    ARITHMETIC_OPERATOR = auto()
    RELATIONAL_OPERATOR = auto()
    LOGICAL_OPERATOR = auto()
    ASSIGNMENT_OPERATOR = auto()

    DELIMITER = auto()

    ERROR = auto()
    EOF = auto()


@dataclass
class Token:
    token_type: TokenType
    lexeme: str
    line: int
    column: int
    attribute: object | None = None

    def type_name(self) -> str:
        return self.token_type.name
