from typing import Optional

from buffer import TwoBufferReader
from symbol_table import SymbolTable
from token_model import Token, TokenType


KEYWORDS = {
    "abstract", "assert", "boolean", "break", "byte", "case", "catch",
    "char", "class", "const", "continue", "default", "do", "double",
    "else", "enum", "extends", "final", "finally", "float", "for", "if",
    "implements", "import", "instanceof", "int", "interface", "long",
    "native", "new", "package", "private", "protected", "public", "return",
    "short", "static", "strictfp", "super", "switch", "synchronized", "this",
    "throw", "throws", "transient", "try", "void", "volatile", "while",
}

DELIMITERS = {";", ",", ".", "(", ")", "{", "}", "[", "]"}
ARITHMETIC_OPERATORS = {"+", "-", "*", "/", "%"}
RELATIONAL_OPERATORS = {"==", "!=", "<", "<=", ">", ">="}
LOGICAL_OPERATORS = {"&&", "||", "!"}
ASSIGNMENT_OPERATORS = {"=", "+=", "-=", "*=", "/=", "%="}

VALID_ESCAPES = {
    "n": "\n",
    "t": "\t",
    "r": "\r",
    "b": "\b",
    "f": "\f",
    "\\": "\\",
    "'": "'",
    '"': '"',
    "0": "\0",
}


class Lexer:
    def __init__(
        self,
        source: str,
        buffer_size: int = 32,
    ) -> None:
        self.reader = TwoBufferReader(source, buffer_size)
        self.symbol_table = SymbolTable()
        self.tokens: list[Token] = []

    def analyze(self) -> list[Token]:
        while not self.reader.eof():
            self._skip_ignored()
            if self.reader.eof():
                break

            self.reader.mark_begin()
            char = self.reader.current()

            if char is None:
                break
            if self._is_identifier_start(char):
                token = self._scan_identifier_or_keyword()
            elif char.isdigit():
                token = self._scan_number()
            elif char == '"':
                token = self._scan_string()
            elif char == "'":
                token = self._scan_char()
            elif char == "/":
                token = self._scan_slash_or_operator()
                if token is None:
                    continue
            elif char in "+-*%=!<>&|":
                token = self._scan_operator()
            elif char in DELIMITERS:
                token = self._scan_delimiter()
            else:
                token = self._scan_unknown_character()

            self.tokens.append(token)

        self.tokens.append(
            Token(
                token_type=TokenType.EOF,
                lexeme="",
                line=self.reader.line,
                column=self.reader.column,
            )
        )
        return self.tokens

    def _skip_ignored(self) -> None:
        while not self.reader.eof():
            char = self.reader.current()

            if char is not None and char.isspace():
                self.reader.advance()
                continue

            if char == "/" and self.reader.peek() == "/":
                self.reader.mark_begin()
                self._skip_line_comment()
                continue

            if char == "/" and self.reader.peek() == "*":
                self.reader.mark_begin()
                error = self._skip_block_comment()
                if error is not None:
                    self.tokens.append(error)
                continue

            break

    def _skip_line_comment(self) -> None:
        self.reader.advance()
        self.reader.advance()

        while not self.reader.eof() and self.reader.current() != "\n":
            self.reader.advance()

    def _skip_block_comment(self) -> Optional[Token]:
        line = self.reader.begin_line
        column = self.reader.begin_column
        self.reader.advance()
        self.reader.advance()

        while not self.reader.eof():
            if self.reader.current() == "*" and self.reader.peek() == "/":
                self.reader.advance()
                self.reader.advance()
                return None
            self.reader.advance()

        return self._error_token(
            "E004",
            "Comentário de bloco não terminado.",
            self.reader.lexeme(),
            line,
            column,
        )

    def _scan_identifier_or_keyword(self) -> Token:
        line = self.reader.begin_line
        column = self.reader.begin_column
        while not self.reader.eof():
            char = self.reader.current()
            if char is None or not self._is_identifier_part(char):
                break
            self.reader.advance()

        lexeme = self.reader.lexeme()
        if lexeme in KEYWORDS:
            return Token(TokenType.KEYWORD, lexeme, line, column)

        symbol_id = self.symbol_table.add(lexeme)
        return Token(
            TokenType.IDENTIFIER,
            lexeme,
            line,
            column,
            f"symbol_id={symbol_id}",
        )

    def _scan_number(self) -> Token:
        line = self.reader.begin_line
        column = self.reader.begin_column
        while not self.reader.eof():
            char = self.reader.current()
            if char is None or not char.isdigit():
                break
            self.reader.advance()

        if self._starts_identifier_tail():
            self._consume_identifier_tail()
            return self._error_token(
                "E002",
                "Identificador não pode começar com número.",
                self.reader.lexeme(),
                line,
                column,
            )

        if self.reader.current() == "." and self._peek_is_digit():
            self.reader.advance()
            self._consume_fraction()

            if self._starts_identifier_tail():
                self._consume_identifier_tail()
                return self._error_token(
                    "E002",
                    "Número seguido por caracteres inválidos.",
                    self.reader.lexeme(),
                    line,
                    column,
                )

            lexeme = self.reader.lexeme()
            return Token(TokenType.FLOAT, lexeme, line, column, float(lexeme))

        # O trabalho trata vírgula decimal como um único erro.
        if self.reader.current() == "," and self._peek_is_digit():
            self.reader.advance()
            self._consume_digits()
            return self._error_token(
                "E003",
                "Separador decimal inválido. Use ponto em vez de vírgula.",
                self.reader.lexeme(),
                line,
                column,
            )

        lexeme = self.reader.lexeme()
        return Token(TokenType.INTEGER, lexeme, line, column, int(lexeme))

    def _consume_fraction(self) -> None:
        while not self.reader.eof():
            char = self.reader.current()
            if char is None or not char.isdigit():
                break
            self.reader.advance()

    def _consume_digits(self) -> None:
        while not self.reader.eof():
            char = self.reader.current()
            if char is None or not char.isdigit():
                break
            self.reader.advance()

    def _starts_identifier_tail(self) -> bool:
        char = self.reader.current()
        return char is not None and (char.isalpha() or char == "_")

    def _consume_identifier_tail(self) -> None:
        while not self.reader.eof():
            char = self.reader.current()
            if char is None or not self._is_identifier_part(char):
                break
            self.reader.advance()

    def _peek_is_digit(self) -> bool:
        char = self.reader.peek()
        return char is not None and char.isdigit()

    def _scan_string(self) -> Token:
        line = self.reader.begin_line
        column = self.reader.begin_column
        decoded: list[str] = []
        terminated = False

        self.reader.advance()

        while not self.reader.eof():
            char = self.reader.current()

            if char == '"':
                self.reader.advance()
                terminated = True
                break
            if char == "\n":
                break
            if char == "\\":
                self.reader.advance()
                if self.reader.eof() or self.reader.current() == "\n":
                    break

                escape = self.reader.current()
                self.reader.advance()
                decoded.append(VALID_ESCAPES.get(escape, "\\" + escape))
                continue

            decoded.append(char)
            self.reader.advance()

        lexeme = self.reader.lexeme()
        if not terminated:
            return self._error_token(
                "E001", "String não terminada.", lexeme, line, column
            )

        return Token(TokenType.STRING, lexeme, line, column, "".join(decoded))

    def _scan_char(self) -> Token:
        line = self.reader.begin_line
        column = self.reader.begin_column
        self.reader.advance()

        if self.reader.eof() or self.reader.current() == "\n":
            return self._error_token(
                "E005",
                "Literal de caractere não terminado.",
                self.reader.lexeme(),
                line,
                column,
            )

        if self.reader.current() == "\\":
            self.reader.advance()
            if self.reader.eof():
                return self._error_token(
                    "E005",
                    "Escape incompleto em literal char.",
                    self.reader.lexeme(),
                    line,
                    column,
                )

            escape = self.reader.current()
            self.reader.advance()
            if escape not in VALID_ESCAPES:
                self._consume_until_char_end()
                return self._error_token(
                    "E005",
                    "Sequência de escape inválida.",
                    self.reader.lexeme(),
                    line,
                    column,
                )
            decoded_value = VALID_ESCAPES[escape]
        else:
            decoded_value = self.reader.current()
            self.reader.advance()

        if self.reader.current() != "'":
            self._consume_until_char_end()
            return self._error_token(
                "E005",
                "Literal char deve conter exatamente um caractere ou uma sequência de escape.",
                self.reader.lexeme(),
                line,
                column,
            )

        self.reader.advance()
        lexeme = self.reader.lexeme()
        return Token(TokenType.CHAR, lexeme, line, column, repr(decoded_value))

    def _consume_until_char_end(self) -> None:
        while not self.reader.eof():
            char = self.reader.current()
            if char == "'":
                self.reader.advance()
                return
            if char == "\n":
                return
            self.reader.advance()

    def _scan_slash_or_operator(self) -> Optional[Token]:
        if self.reader.peek() == "/":
            self._skip_line_comment()
            return None
        if self.reader.peek() == "*":
            return self._skip_block_comment()
        return self._scan_operator()

    def _scan_operator(self) -> Token:
        line = self.reader.begin_line
        column = self.reader.begin_column
        first = self.reader.current()
        second = self.reader.peek()
        pair = first + second if second is not None else first

        if pair in RELATIONAL_OPERATORS | LOGICAL_OPERATORS | ASSIGNMENT_OPERATORS:
            self.reader.advance()
            self.reader.advance()
            return self._operator_token(line, column)

        one_char_operators = (
            ARITHMETIC_OPERATORS
            | RELATIONAL_OPERATORS
            | LOGICAL_OPERATORS
            | ASSIGNMENT_OPERATORS
        )
        if first in one_char_operators:
            self.reader.advance()
            return self._operator_token(line, column)

        self.reader.advance()
        return self._error_token(
            "E006",
            f"Operador inválido: {first!r}.",
            self.reader.lexeme(),
            line,
            column,
        )

    def _operator_token(self, line: int, column: int) -> Token:
        lexeme = self.reader.lexeme()
        token_type = self._operator_type(lexeme)
        return Token(token_type, lexeme, line, column)

    def _scan_delimiter(self) -> Token:
        line = self.reader.begin_line
        column = self.reader.begin_column
        self.reader.advance()
        lexeme = self.reader.lexeme()
        return Token(TokenType.DELIMITER, lexeme, line, column)

    def _scan_unknown_character(self) -> Token:
        line = self.reader.begin_line
        column = self.reader.begin_column
        self.reader.advance()
        return self._error_token(
            "E006",
            "Caractere não reconhecido pela linguagem.",
            self.reader.lexeme(),
            line,
            column,
        )

    def _error_token(
        self,
        code: str,
        message: str,
        lexeme: str,
        line: int,
        column: int,
    ) -> Token:
        return Token(TokenType.ERROR, lexeme, line, column, f"{code}: {message}")

    @staticmethod
    def _operator_type(lexeme: str) -> TokenType:
        if lexeme in RELATIONAL_OPERATORS:
            return TokenType.RELATIONAL_OPERATOR
        if lexeme in LOGICAL_OPERATORS:
            return TokenType.LOGICAL_OPERATOR
        if lexeme in ASSIGNMENT_OPERATORS:
            return TokenType.ASSIGNMENT_OPERATOR
        return TokenType.ARITHMETIC_OPERATOR

    @staticmethod
    def _is_identifier_start(char: str) -> bool:
        return char.isalpha() or char == "_"

    @staticmethod
    def _is_identifier_part(char: str) -> bool:
        return char.isalnum() or char == "_"
