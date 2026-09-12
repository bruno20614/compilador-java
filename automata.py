class AutomataTrace:

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def transition(
        self,
        old_state: str,
        char,
        new_state: str
    ) -> None:

        if not self.enabled:
            return

        print(
            f"[AFD] {old_state:<18} "
            f"-- {repr(char):<8} --> {new_state}"
        )

    def accepted(
        self,
        token_type: str,
        lexeme: str
    ) -> None:

        if not self.enabled:
            return

        print(
            f"[AFD] ACEITA {token_type:<22} "
            f"lexema={lexeme!r}\n"
        )

    def error(
        self,
        code: str,
        lexeme: str,
        message: str
    ) -> None:

        if not self.enabled:
            return

        print(
            f"[AFD] ERRO {code} "
            f"lexema={lexeme!r}: "
            f"{message}\n"
        )