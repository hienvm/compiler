from lexer.lexer_result import Position, Location, Token
from lexer.lexer_builder import LexerBuilder
from lexer.state import AcceptingState, Lookahead, ErrorState, State, TerminalState
from typing import Iterable
from lexer.lexer_result import LexicalError, LexicalResult


class Lexer(LexerBuilder):
    def __init__(self, lex_data_url: str) -> None:
        super().__init__(lex_data_url)
        self.lexeme: str = ""               # xâu hiện tại
        self.current_input: str | None = ""        # input hiện tại
        self.start_pos = Position(1, 0)     # vị trí bắt đầu lexeme
        self.current_pos = Position(1, 0)   # vị trí hiện tại

    def analyze(self, input_url: str, is_ln_by_ln: bool = True) -> Iterable[LexicalResult | LexicalError]:
        """Sử dụng generator để tiết kiệm bộ nhớ

        Args:
            input_url (str): Url file code cần phân tích
            is_ln_by_ln (bool, optional): Đọc theo từng dòng hay toàn bộ. Defaults to True.

        Yields:
            Iterable[LexicalResult | LexicalError]: Iterator cho output stream, có nội dung là kết quả hoặc lỗi
        """
        with open(input_url, "r", encoding="utf8") as input_file:
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
            res = self.process('\n')
            if res is not None:
                yield res
            res = self.process(None)
            if res is not None:
                yield res
            # Thêm token EOF vào cuối file
            yield LexicalResult("EOF", Token("EOF"), Location(self.current_pos, self.current_pos))

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
            if self.current_input is not None:
                self.lexeme += self.current_input

            # state tạm thời
            tmp_state = self.current_state

            if tmp_state is not None:
                # xử lý escape: thay chuỗi hậu tố cũ bằng chuỗi mới
                if tmp_state.escape is not None:
                    self.lexeme = self.lexeme.removesuffix(
                        tmp_state.escape.old)
                    self.lexeme += tmp_state.escape.new
                # xử lý lookahead
                if isinstance(
                    self.transit(next_input), Lookahead
                ):  # tạm thời nhảy đến state tiếp theo
                    tmp_state = self.transit(next_input)
            else:
                # trả về thông báo lỗi mặc định nếu không match được input
                res = LexicalError(
                    self.lexeme,
                    Location(self.start_pos, self.current_pos)
                )

            if isinstance(tmp_state, AcceptingState):
                if self.lexeme in self.keywords:
                    # Xử lý keyword
                    res = LexicalResult(
                        self.lexeme,
                        Token("keyword", self.lexeme),
                        Location(self.start_pos, self.current_pos)
                    )
                else:
                    # Trả về kết quả chấp nhận (token + lexeme + pos)
                    res = LexicalResult(
                        self.lexeme,
                        tmp_state.token,
                        Location(self.start_pos, self.current_pos)
                    )
            elif isinstance(tmp_state, ErrorState):
                # báo lỗi nếu nhảy đến trạng thái lỗi
                res = LexicalError(
                    self.lexeme,
                    Location(self.start_pos, self.current_pos),
                    tmp_state.msg
                )

            # reset lại DFA khi tới terminal state hoặc gặp lỗi
            if tmp_state is None or isinstance(tmp_state, TerminalState):
                self.reset()

        self.current_input = next_input

        return res

    def transit(self, input: str | None):
        '''Trả về trạng thái tiếp theo khi đọc input'''
        if isinstance(self.current_state, State):
            return self.current_state.transit(
                input,
                self.input_to_group.get(input, input)
            )
        else:
            return None

    def reset(self):
        '''reset lại dfa'''
        self.current_state = self.start_state
        self.lexeme = ""


def is_newline(current_input: str | None, next_input: str | None) -> bool:
    '''Tận dụng lookahead để xuống dòng cho \\n, \\r, \\r\\n (khi gặp \\r\\n thì chỉ coi \\n là kí tự xuống dòng)'''
    match current_input:
        case '\n':
            return True
        case '\r':
            if next_input != '\n':
                return True
    return False
