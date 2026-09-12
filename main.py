import argparse
from pathlib import Path

from lexer import Lexer
from token_model import TokenType


def print_header(title: str):

    print()

    print("=" * 78)

    print(
        title.center(78)
    )

    print("=" * 78)


def format_attribute(value):

    if value is None:
        return "-"

    if isinstance(value, str):

        return (
            value
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )

    return str(value)


def print_tokens(tokens):

    print_header(
        "LISTA / TABELA DE TOKENS"
    )

    print(
        f"{'#':<5}"
        f"{'LIN':<6}"
        f"{'COL':<6}"
        f"{'TIPO':<26}"
        f"{'LEXEMA':<24}"
        f"ATRIBUTO"
    )

    print("-" * 110)

    index = 1

    for token in tokens:

        if (
            token.token_type
            == TokenType.EOF
        ):
            continue

        lexeme = (
            token.lexeme
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )

        print(
            f"{index:<5}"
            f"{token.line:<6}"
            f"{token.column:<6}"
            f"{token.type_name():<26}"
            f"{lexeme!r:<24}"
            f"{format_attribute(token.attribute)}"
        )

        index += 1


def print_symbol_table(
    symbol_table
):

    print_header(
        "TABELA DE SÍMBOLOS"
    )

    print(
        f"{'ID':<8}"
        f"{'IDENTIFICADOR':<35}"
        f"OCORRÊNCIAS"
    )

    print("-" * 58)

    for symbol in (
        symbol_table.all_symbols()
    ):

        print(
            f"{symbol.symbol_id:<8}"
            f"{symbol.lexeme:<35}"
            f"{symbol.occurrences}"
        )


def print_errors(tokens):

    errors = [
        token
        for token in tokens
        if token.token_type
        == TokenType.ERROR
    ]

    print_header(
        "ERROS LÉXICOS"
    )

    if not errors:

        print(
            "Nenhum erro léxico encontrado."
        )

        return

    for error in errors:

        lexeme = (
            error.lexeme
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )

        print(
            f"Linha {error.line}, "
            f"coluna {error.column}: "
            f"{error.attribute}"
        )

        print(
            f"  Lexema: {lexeme!r}"
        )


def print_summary(
    path,
    source,
    tokens,
    lexer
):

    token_count = sum(
        1
        for token in tokens
        if token.token_type
        != TokenType.EOF
    )

    error_count = sum(
        1
        for token in tokens
        if token.token_type
        == TokenType.ERROR
    )

    print_header(
        "RESUMO DA ANÁLISE"
    )

    print(
        f"Arquivo                  : "
        f"{path}"
    )

    print(
        f"Caracteres carregados    : "
        f"{len(source)}"
    )

    print(
        f"Tokens reconhecidos      : "
        f"{token_count}"
    )

    print(
        f"Identificadores distintos: "
        f"{len(lexer.symbol_table)}"
    )

    print(
        f"Erros léxicos            : "
        f"{error_count}"
    )

    if error_count == 0:

        print(
            "Status                   : "
            "análise concluída sem "
            "erros léxicos."
        )

    else:

        print(
            "Status                   : "
            "análise concluída com "
            "erros léxicos."
        )


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Analisador léxico manual "
            "para uma linguagem semelhante "
            "a Java."
        )
    )

    parser.add_argument(
        "arquivo",
        help=(
            "Arquivo-fonte com "
            "extensão .java"
        ),
    )

    parser.add_argument(
        "--trace",
        action="store_true",
        help=(
            "Mostra transições do AFD "
            "e begin/forward."
        ),
    )

    parser.add_argument(
        "--buffer-size",
        type=int,
        default=32,
        help=(
            "Tamanho de cada buffer. "
            "Padrão: 32."
        ),
    )

    parser.add_argument(
        "--buffer-view",
        action="store_true",
        help=(
            "Mostra o estado final "
            "dos dois buffers."
        ),
    )

    return parser.parse_args()


def main():

    args = parse_args()

    path = Path(args.arquivo)

    if path.suffix.lower() != ".java":

        raise SystemExit(
            "Erro: o arquivo deve "
            "possuir extensão .java."
        )

    if not path.exists():

        raise SystemExit(
            f"Arquivo não encontrado: "
            f"{path}"
        )

    source = path.read_text(
        encoding="utf-8"
    )

    lexer = Lexer(
        source=source,
        buffer_size=args.buffer_size,
        trace=args.trace,
    )

    tokens = lexer.analyze()

    print_summary(
        path,
        source,
        tokens,
        lexer,
    )

    print_tokens(tokens)

    print_symbol_table(
        lexer.symbol_table
    )

    print_errors(tokens)

    if args.buffer_view:

        print_header(
            "ESTADO FINAL DOS DOIS BUFFERS"
        )

        print(
            lexer.reader.buffer_snapshot()
        )


if __name__ == "__main__":
    main()
