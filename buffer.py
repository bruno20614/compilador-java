from typing import Optional


class TwoBufferReader:

    def __init__(
        self,
        source: str,
        buffer_size: int = 32,
    ) -> None:

        if buffer_size < 4:
            raise ValueError(
                "buffer_size deve ser pelo menos 4"
            )

        self.source = source

        self.buffer_size = buffer_size

        self.begin = 0
        self.forward = 0

        self.line = 1
        self.column = 1

        self.begin_line = 1
        self.begin_column = 1

        self.buffer_a_start = 0
        self.buffer_b_start = buffer_size

        self.buffer_a = ""
        self.buffer_b = ""

        self._load_initial_buffers()

    def _load_initial_buffers(self) -> None:

        self.buffer_a = self.source[
            self.buffer_a_start:
            self.buffer_a_start + self.buffer_size
        ]

        self.buffer_b = self.source[
            self.buffer_b_start:
            self.buffer_b_start + self.buffer_size
        ]

    def _buffer_for_position(
        self,
        position: int
    ) -> str:

        if (
            self.buffer_a_start
            <= position
            < self.buffer_a_start + len(self.buffer_a)
        ):
            return "A"

        if (
            self.buffer_b_start
            <= position
            < self.buffer_b_start + len(self.buffer_b)
        ):
            return "B"

        return "-"

    def _ensure_loaded(
        self,
        position: int
    ) -> None:

        if position >= len(self.source):
            return

        if self._buffer_for_position(position) != "-":
            return

        block_start = (
            position // self.buffer_size
        ) * self.buffer_size

        # Reutiliza o buffer mais antigo para o próximo bloco.
        if block_start > max(
            self.buffer_a_start,
            self.buffer_b_start
        ):

            if self.buffer_a_start < self.buffer_b_start:

                self.buffer_a_start = block_start

                self.buffer_a = self.source[
                    block_start:
                    block_start + self.buffer_size
                ]

            else:

                self.buffer_b_start = block_start

                self.buffer_b = self.source[
                    block_start:
                    block_start + self.buffer_size
                ]

    def eof(self) -> bool:
        return self.forward >= len(self.source)

    def current(self) -> Optional[str]:

        if self.eof():
            return None

        self._ensure_loaded(self.forward)

        return self.source[self.forward]

    def peek(
        self,
        offset: int = 1
    ) -> Optional[str]:

        position = self.forward + offset

        if position >= len(self.source):
            return None

        self._ensure_loaded(position)

        return self.source[position]

    def advance(self) -> Optional[str]:

        if self.eof():
            return None

        self._ensure_loaded(self.forward)

        char = self.source[self.forward]

        self.forward += 1

        if char == "\n":
            self.line += 1
            self.column = 1

        else:
            self.column += 1

        return char

    def mark_begin(self) -> None:

        self.begin = self.forward

        self.begin_line = self.line
        self.begin_column = self.column

    def lexeme(self) -> str:

        return self.source[
            self.begin:
            self.forward
        ]

    def skip_whitespace(self) -> None:

        while not self.eof():

            char = self.current()

            if char is None:
                return

            if not char.isspace():
                return

            self.advance()

    def current_buffer_name(self) -> str:

        return self._buffer_for_position(
            self.forward
        )

    def buffer_snapshot(self) -> str:

        def visible(text: str) -> str:

            return (
                text
                .replace("\n", "\\n")
                .replace("\t", "\\t")
            )

        return (
            f"BUFFER A "
            f"[{self.buffer_a_start}:"
            f"{self.buffer_a_start + len(self.buffer_a)}] "
            f"{visible(self.buffer_a)!r}\n"

            f"BUFFER B "
            f"[{self.buffer_b_start}:"
            f"{self.buffer_b_start + len(self.buffer_b)}] "
            f"{visible(self.buffer_b)!r}\n"

            f"begin={self.begin}, "
            f"forward={self.forward}"
        )
