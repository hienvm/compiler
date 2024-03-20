from lexer.lexer_builder import LexerBuilder
from common.state import State, AcceptingState, LookaheadAcceptingState, NormalState


class Token:
    def __init__(self, lexeme: str, labels: set[str]) -> None:
        self.lexeme = lexeme
        self.labels = labels


class LexicalError:
    def __init__(self, spelling: str) -> None:
        self.spelling = spelling

    def __str__(self) -> str:
        return f"Illegal spelling: {self.spelling}"

class Lexer(LexerBuilder):
    def __init__(self, lex_data_url: str) -> None:
        super().__init__(lex_data_url)

    def process(self, input: str, next_input: str):
        """Xử lý lần lượt từng cặp ký tự đầu vào và ký tự kế tiếp

        Args:
            input (str): ký tự đầu vào
            next_input (str): nhìn trước 1 ký tự

        Returns:
            _type_: _description_
        """
        res = None

        self.current_state = self.transit(input)

        # Nếu transition cuối của một xâu quay về điểm xuất phát thì có nghĩa toàn bộ xâu có thể bị lược bỏ
        if self.current_state == self.start_state:
            self.lexeme = ""
            return None

        if self.current_state is None:
            res = LexicalError(self.lexeme)
        elif self.current_state is AcceptingState or self.transit(next) is LookaheadAcceptingState:
            pass

        if self.current_state is not NormalState:
            self.restart()
            self.lexeme = ""

        return res
