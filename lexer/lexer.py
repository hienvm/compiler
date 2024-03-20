from lexer.lexer_builder import LexerBuilder
from common.state import AcceptingState, LookaheadAcceptingState, NormalState, DiscardState


class LexicalResult:
    def __init__(self, lexeme: str, token_labels: set[str]) -> None:
        self.lexeme = lexeme
        self.token_labels = token_labels


class LexicalError:
    def __init__(self, spelling: str) -> None:
        self.spelling = spelling


class DefaultLexicalError(LexicalError):
    def __str__(self) -> str:
        return f"Illegal spelling: {self.spelling}"

class Lexer(LexerBuilder):
    def __init__(self, lex_data_url: str) -> None:
        super().__init__(lex_data_url)
        self.lexeme: str = ""           # xâu hiện tại
        self.current_input: str         # input hiện tại

    def process(self, next_input: str):
        """Xử lý trễ 1 ký tự để thực hiện lookahead

        Args:
            input (str): ký tự đầu vào
            next_input (str): nhìn trước 1 ký tự

        Returns:
            _type_: _description_
        """
        res = None

        if self.current_input is None:
            return res

        self.lexeme += self.current_input
        self.current_state = self.transit(self.current_input)

        # xử lý lookahead
        if next_input is not None and isinstance(self.transit(next_input), LookaheadAcceptingState):
            self.current_state = self.transit(next_input)

        if self.current_state is None:
            # trả về thông báo lỗi nếu không match được input
            res = DefaultLexicalError(self.lexeme)
            # nhảy đến discard_state để reset
            self.current_state = DiscardState
        elif isinstance(self.current_state, AcceptingState):
            res = LexicalResult(
                self.lexeme,
                self.token_labels_of[self.current_state.name]
            )

        # reset lại DFA khi tới 1 trạng thái kết thúc (bao gồm cả DiscardState)
        if isinstance(self.current_state, NormalState):
            self.restart()
            self.lexeme = ""

        self.current_input = next_input

        return res
