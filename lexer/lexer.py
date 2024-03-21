from common.util import Position, is_newline
from lexer.lexer_builder import LexerBuilder
from common.state import AcceptingState, LookaheadAcceptingState, NormalState, DiscardState


class LexicalResult:
    def __init__(self, lexeme: str, token_labels: set[str], pos: Position) -> None:
        self.lexeme = lexeme
        self.token_labels = token_labels
        self.pos = pos


class LexicalError:
    def __init__(self, spelling: str) -> None:
        self.spelling = spelling

    def __str__(self) -> str:
        '''Thông báo lỗi mặc định'''
        return f"Illegal spelling: {self.spelling}"


class Lexer(LexerBuilder):
    def __init__(self, lex_data_url: str) -> None:
        super().__init__(lex_data_url)
        self.lexeme: str = ""               # xâu hiện tại
        self.current_input: str             # input hiện tại
        self.start_pos = Position(0, 0)     # vị trí bắt đầu lexeme
        self.current_pos = Position(0, 0)   # vị trí hiện tại của lexer

    def process(self, next_input: str):
        """Xử lý trễ 1 ký tự để thực hiện lookahead

        Args:
            input (str): ký tự đầu vào
            next_input (str): nhìn trước 1 ký tự

        Returns:
            _type_: _description_
        """
        res = None

        if self.current_input is not None:
            # cập nhật vị trí
            if is_newline(self.current_input, next_input):
                self.current_pos.ln += 1
                self.current_pos.col = 1
            else:
                self.current_pos.col += 1

            if self.lexeme == "":
                self.start_pos = self.current_pos.copy()

            # chuyển trạng thái
            self.current_state = self.transit(self.current_input)
            self.lexeme += self.current_input

            # xử lý lookahead
            if next_input is not None and isinstance(self.transit(next_input), LookaheadAcceptingState):
                self.current_state = self.transit(next_input)

            if self.current_state is None:
                # trả về thông báo lỗi mặc định nếu không match được input
                res = LexicalError(self.lexeme, self.current_pos)
            elif isinstance(self.current_state, AcceptingState):
                # trả về kết quả nếu accept
                res = LexicalResult(
                    self.lexeme,
                    self.token_labels_of[self.current_state.name],
                    self.current_pos
                )

            # reset lại DFA khi tới 1 trạng thái kết thúc (bao gồm cả DiscardState và trạng thái lỗi)
            if not isinstance(self.current_state, NormalState):
                self.restart()

        self.current_input = next_input

        return res

    def restart(self):
        # override
        super().restart()
        self.lexeme = ""
