from collections import defaultdict

EPSILON = "ε"
EOF = "$"
GRAMMAR = {
    "PROG": [["public", "class", "id", "{", "public", "static", "void", "id", "(", ")", "{", "CMDS", "}", "}"]],
    "CMDS": [["CMD", "CMDS"], [EPSILON]],
    "CMD": [["DECL"], ["ATRIB"], ["IF_STMT"]],
    "DECL": [["TIPO", "id", ";"]],
    "TIPO": [["int"], ["float"], ["char"]],
    "ATRIB": [["id", "=", "E", ";"]],
    "IF_STMT": [["if", "(", "COND", ")", "{", "CMDS", "}", "SENAO"]],
    "SENAO": [["else", "{", "CMDS", "}"], [EPSILON]],
    "COND": [["E", "OP_REL", "E"]],
    "OP_REL": [["=="], ["!="], ["<"], [">"]],
    "E": [["T", "E'"]],
    "E'": [["+", "T", "E'"], ["-", "T", "E'"], [EPSILON]],
    "T": [["F", "T'"]],
    "T'": [["*", "F", "T'"], ["/", "F", "T'"], [EPSILON]],
    "F": [["(", "E", ")"], ["id"], ["num"]],
}
NONTERMINALS = set(GRAMMAR)


def _first_sequence(sequence, first):
    result = set()
    nullable = True
    for symbol in sequence:
        if symbol == EPSILON:
            result.add(EPSILON)
            break
        if symbol in NONTERMINALS:
            result.update(first[symbol] - {EPSILON})
            if EPSILON not in first[symbol]:
                nullable = False
                break
        else:
            result.add(symbol)
            nullable = False
            break
    if nullable:
        result.add(EPSILON)
    return result


def build_sets_and_table():
    first = {nt: set() for nt in GRAMMAR}
    changed = True
    while changed:
        changed = False
        for nt, productions in GRAMMAR.items():
            for production in productions:
                before = len(first[nt])
                first[nt].update(_first_sequence(production, first))
                changed |= len(first[nt]) != before
    follow = {nt: set() for nt in GRAMMAR}
    follow["PROG"].add(EOF)
    changed = True
    while changed:
        changed = False
        for lhs, productions in GRAMMAR.items():
            for production in productions:
                for i, symbol in enumerate(production):
                    if symbol not in NONTERMINALS:
                        continue
                    suffix_first = _first_sequence(production[i + 1:], first)
                    before = len(follow[symbol])
                    follow[symbol].update(suffix_first - {EPSILON})
                    if EPSILON in suffix_first or i == len(production) - 1:
                        follow[symbol].update(follow[lhs])
                    changed |= len(follow[symbol]) != before
    table = defaultdict(dict)
    for lhs, productions in GRAMMAR.items():
        for production in productions:
            starts = _first_sequence(production, first)
            for terminal in starts - {EPSILON}:
                table[lhs][terminal] = production
            if EPSILON in starts:
                for terminal in follow[lhs]:
                    table[lhs][terminal] = production
    return first, follow, table


def token_symbol(token):
    lexeme = token.lexeme
    if token.token_type.name == "IDENTIFIER":
        return "id"
    if token.token_type.name in {"INTEGER", "FLOAT"}:
        return "num"
    return lexeme


def analyze(tokens, show_report=True):
    first, follow, table = build_sets_and_table()
    stream = [(token_symbol(t), t) for t in tokens if t.token_type.name != "EOF"]
    stream.append((EOF, None))
    stack = [EOF, "PROG"]
    cursor = 0
    errors = []
    if show_report:
        print("\nFIRST / FOLLOW")
        for nt in GRAMMAR:
            print(f"{nt:<8} FIRST={{{', '.join(sorted(first[nt]))}}} FOLLOW={{{', '.join(sorted(follow[nt]))}}}")
        print("\nTABELA M (células preenchidas)")
        for nt in GRAMMAR:
            for terminal, production in sorted(table[nt].items()):
                print(f"M[{nt}, {terminal}] = {nt} -> {' '.join(production)}")
        print("\nTRACE: PILHA | ENTRADA | AÇÃO")
    steps = 0
    while stack and steps < 10000:
        steps += 1
        top = stack[-1]
        lookahead = stream[cursor][0] if cursor < len(stream) else EOF
        remaining = " ".join(sym for sym, _ in stream[cursor:])
        action = ""
        if top == lookahead == EOF:
            action = "aceita"
            stack.pop()
        elif top not in NONTERMINALS:
            if top == lookahead:
                stack.pop(); cursor += 1
                action = f"casa {top}"
            else:
                tok = stream[cursor][1] if cursor < len(stream) else None
                loc = f"linha {tok.line}, coluna {tok.column}: " if tok else ""
                errors.append(f"{loc}encontrado '{lookahead}', esperava-se '{top}' no topo da pilha")
                action = f"ERRO: esperava {top}; descarta {lookahead}"
                if lookahead == EOF:
                    stack.pop()
                else:
                    cursor += 1
        else:
            production = table[top].get(lookahead)
            if production is not None:
                stack.pop()
                if production != [EPSILON]:
                    stack.extend(reversed(production))
                action = f"{top} -> {' '.join(production)}"
            else:
                expected = ", ".join(sorted(table[top])) or "nenhum terminal"
                tok = stream[cursor][1] if cursor < len(stream) else None
                loc = f"linha {tok.line}, coluna {tok.column}: " if tok else ""
                errors.append(f"{loc}token inesperado '{lookahead}' para {top}; esperava-se {expected}")
                action = f"ERRO em M[{top}, {lookahead}]; sincroniza"
                if lookahead in {";", "}"}:
                    stack.pop()
                elif lookahead == EOF:
                    stack.pop()
                else:
                    cursor += 1
        if show_report:
            print(f"{' '.join(stack):<38} | {remaining:<38} | {action}")
        if cursor >= len(stream):
            break
    accepted = not errors and not stack and cursor >= len(stream) - 1
    return accepted, errors
