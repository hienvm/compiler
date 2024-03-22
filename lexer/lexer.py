from lexer.util import Position, Location, Token, is_newline
from lexer.lexer_builder import LexerBuilder
from lexer.state import AcceptingState, LookaheadAcceptingState, TerminalState
from typing import Iterable
from lexer.util import LexicalError, LexicalResult


class Lexer(LexerBuilder):
    def __init__(self, lex_data_url: str) -> None:
        super().__init__(lex_data_url)
        self.lexeme: str = ""               # xâu hiện tại
        self.current_input: str = ""        # input hiện tại
        self.start_pos = Position(1, 0)     # vị trí bắt đầu lexeme
        self.current_pos = Position(1, 0)   # vị trí hiện tại của lexer

    def analyze(self, input_url: str, is_ln_by_ln: bool = True) -> Iterable[LexicalResult | LexicalError]:
        """Sử dụng generator để tiết kiệm bộ nhớ và hỗ trợ xử lý gối đầu nhau cho các phần sau nếu có (không phải chờ tính hết kết quả rồi trả về mảng)

        Args:
            input_url (str): Url file code cần phân tích
            is_ln_by_ln (bool, optional): Đọc theo từng dòng hay toàn bộ. Defaults to True.

        Yields:
            Iterable[LexicalResult | LexicalError]: Iterator cho output stream, có nội dung là kết quả hoặc lỗi
        """
        with open(input_url, "r") as input_file:
            if is_ln_by_ln:
                # Đọc từng dòng một để tiết kiệm bộ nhớ đối với file có kích thước lớn
                for line in input_file:
                    # Xử lý từng ký tự một
                    for symbol in line:
                        res = self.process(symbol)
                        # Trả về kết quả mỗi khi terminate
                        if res is not None:
                            yield res
            else:
                # Đọc hết một lúc để tận dụng buffer cho các file nhỏ
                text = input_file.read()
                for symbol in text:
                    res = self.process(symbol)
                    # Trả về kết quả mỗi khi terminate
                    if res is not None:
                        yield res
            # quét cuối file để dọn dẹp các lexeme chưa terminate
            res = self.process(None)
            if res is not None:
                yield res

    def process(self, next_input: str | None) -> LexicalResult | LexicalError | None:
        """Xử lý trễ 1 ký tự để thực hiện lookahead

        Args:
            next_input (str): nhìn trước 1 ký tự

        Returns:
            LexicalResult: Kết quả được chấp nhận
            LexicalErrot: Lỗi từ vựng
            None: Chưa terminate
        """
        res = None

        if self.current_input != "":
            # cập nhật vị trí
            if is_newline(self.current_input, next_input):
                self.current_pos.ln += 1
                self.current_pos.col = 0
            else:
                self.current_pos.col += 1

            if self.lexeme == "":
                self.start_pos = self.current_pos.copy()

            # chuyển trạng thái
            self.current_state = self.transit(self.current_input)
            self.lexeme += self.current_input

            # xử lý lookahead
            if self.current_state is not None and isinstance(
                self.transit(next_input), LookaheadAcceptingState
            ):
                self.current_state = self.transit(next_input)

            if self.current_state is None:
                # trả về thông báo lỗi mặc định nếu không match được input
                res = LexicalError(
                    self.lexeme,
                    Location(self.start_pos, self.current_pos)
                )
            elif isinstance(self.current_state, AcceptingState):
                if self.lexeme in self.keywords:
                    # Xử lý keyword
                    res = LexicalResult(
                        self.lexeme,
                        Token({"keyword"}),
                        Location(self.start_pos, self.current_pos)
                    )
                else:
                    res = LexicalResult(
                        self.lexeme,
                        self.current_state.token,
                        Location(self.start_pos, self.current_pos)
                    )

            # reset lại DFA khi tới terminal state hoặc gặp lỗi
            if self.current_state is None or isinstance(self.current_state, TerminalState):
                self.reset()

        self.current_input = next_input

        return res

    def reset(self):
        # override
        super().reset()
        self.lexeme = ""
