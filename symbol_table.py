from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Symbol:
    symbol_id: int
    lexeme: str
    occurrences: int = 1


class SymbolTable:
    def __init__(self) -> None:
        self._symbols: Dict[str, Symbol] = {}
        self._next_id = 0

    def add(self, lexeme: str) -> int:
        if lexeme in self._symbols:
            self._symbols[lexeme].occurrences += 1d
            return self._symbols[lexeme].symbol_id

        symbol = Symbol(
            symbol_id=self._next_id,
            lexeme=lexeme,
            occurrences=1,
        )

        self._symbols[lexeme] = symbol

        self._next_id += 1

        return symbol.symbol_id

    def get(self, lexeme: str):
        return self._symbols.get(lexeme)

    def all_symbols(self) -> List[Symbol]:
        return sorted(
            self._symbols.values(),
            key=lambda symbol: symbol.symbol_id
        )

    def __len__(self) -> int:
        return len(self._symbols)
