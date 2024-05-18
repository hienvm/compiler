from lexer.lexer import Lexer
from lexer.lexer_result import LexicalError, LexicalResult, Location
from lexer.state_attributes import Token
from parser.parser_builder import ParserBuilder
from parser.types import EPSILON, Symbol, NonTerminalSymbol, TerminalSymbol
import os.path
from pathlib import Path


class Parser(ParserBuilder):
    def __init__(self, lexer: Lexer, from_grammar: bool = False, whole: bool = False) -> None:
        super().__init__(from_grammar)
        self.lexer = lexer
        self.whole = whole

    def parse(self, input_url: str) -> tuple[dict, str]:
        ast = {}
        stack: list[Symbol] = [NonTerminalSymbol(self.start)]
        err_log = ""

        # Đọc từng input từ lexer
        for input in self.lexer.analyze(input_url, not self.whole):
            if isinstance(input, LexicalError):
                err_log += str(input) + '\n'
            elif isinstance(input, LexicalResult):
                top: Symbol = stack[-1]
                # khi nào top còn là nonterminal:
                # tìm production tương ứng -> cập nhật stack bằng production
                while isinstance(top, NonTerminalSymbol):
                    # có tìm đc production hay không
                    p_found = False
                    # hỗ trợ token với nhiều label (nhãn | loại) khác nhau
                    # miễn là với một top và input, xác định được duy nhất một production
                    for label in input.token.labels:
                        # tìm production tương ứng với top của stack và token lookahead
                        p = self.table[top].get(
                            TerminalSymbol(label), None)
                        # xử lý các điều kiện
                        if p is None:
                            continue
                        if p_found:
                            # chỉ một ô table[top][label] được phép khác rỗng
                            raise Exception(
                                f"Label duplicate:  \n{p}  \n`{label}`"
                            )
                        p_found = True
                        # thay top của stack bằng vế phải của production được chọn
                        stack.pop()
                        if not p.empty():
                            stack.extend(reversed(p.rsyms))
                        # cập nhật lại top
                        top = stack[-1] if len(stack) > 0 else EPSILON
                        if not isinstance(top, NonTerminalSymbol):
                            break
                    if not p_found:
                        # nếu ko tìm đc production thì báo lỗi cú pháp rồi skip đến input tiếp theo
                        err_log += "Cannot find Production!\n"
                        err_log += f"  Top: {top}\n"
                        err_log += f"  Input: {input.token}\n"
                        break
                if isinstance(top, TerminalSymbol):
                    if input.token.isa(Token(top.val)):
                        # Nếu top stack thỏa mãn token lookahead
                        stack.pop()
                    else:
                        # Nếu không thì báo lỗi cú pháp
                        err_log += "Unexpected Token!\n"
                        err_log += f"  Expected: {Token(top.val)}\n"
                        err_log += f"  But: {input}\n"
        # Khi đã đọc xong hết input
        if len(stack) > 0:
            err_log += f"Stack not emptied: {stack}\n"
        return (ast, err_log)
