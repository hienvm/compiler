from lexer.util import LexerResult
from lexical_automaton import LexerBuilder


class Lexer(LexerBuilder):
    def __init__(self, lex_data_url: str) -> None:
        super().__init__(lex_data_url)

    def produce(self, input) -> LexerResult | None:
        res = None

        self.current_state = self.current_state.transit(
            input, self.input_to_group.get(input, input)
        )

        match self.current_state.type:
            case "TERMINAL":
                self.restart()
                self.lexeme = ""
            case "LOOKAHEAD_TERMINAL":
                self.restart()
                self.lexeme = ""
                self.transit(input)
            case _:
                pass

        return res
