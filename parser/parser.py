from lexer.lexer import Lexer
from lexer.lexer_result import LexicalError, LexicalResult, Location
from lexer.state_attributes import Token
from parser.ast.node import Leaf, Node
from parser.parser_builder import ParserBuilder
from parser.types import EOF, EPSILON, Epsilon, Symbol, NonTerminalSymbol, TerminalSymbol
from parser.ast.ast import AST
import os.path
from pathlib import Path


class Parser(ParserBuilder):
    def __init__(self, lexer: Lexer, from_table: bool = False, eof: bool = False, whole: bool = False) -> None:
        super().__init__(from_table)
        # lexer được chuyền vào
        self.lexer = lexer
        # Giữ lại EOF hay không
        self.eof = eof
        # flag đọc cả file hay từng dòng, chuyền cho lexer
        self.whole = whole

    def parse(self, input_url: str) -> tuple[AST, str]:
        '''LL(1) Parse\n
        Build AST: Stack LL(1) (chứa các Symbol) được đồng bộ với stack dfs (chứa các Node)\n
        Error Recovery: Khi gặp lỗi, ghi nhận vào log và chuyển đến input tiếp theo\n
        '''
        # cây cú pháp
        ast = AST(self.start)
        # thông báo lỗi
        err_log = ""
        # stack cho pushdown automaton
        # Khởi tạo với start
        stack: list[Symbol] = [self.start]

        # Đọc từng input từ lexer
        for input in self.lexer.analyze(input_url, not self.whole):
            if isinstance(input, LexicalError):
                err_log += str(input) + '\n'
            elif isinstance(input, LexicalResult):
                top: Symbol = stack[-1]
                # khi nào top còn là nonterminal:
                # tìm production tương ứng -> cập nhật stack bằng production
                while isinstance(top, NonTerminalSymbol):
                    # xử lý non-terminal
                    # flag check có tìm đc production hay không
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
                            # chỉ một ô table[top][label] được phép khác rỗng với mỗi một tập labels
                            raise Exception(
                                f"Label duplicate:  \n{p}  \n`{label}`"
                            )
                        p_found = True
                        # thay top của stack bằng vế phải của production được chọn
                        stack.pop()
                        # đảo ngược để đặt symbol bên trái cùng lên top stack
                        stack.extend(reversed(p.rsyms))
                        # cập nhật lại top
                        top = stack[-1] if len(stack) > 0 else EPSILON
                        # mở rộng ast
                        ast.expand_inner(p.rsyms)
                        # nhảy đến nút tiếp theo (nút con trái cùng)
                        ast.next()
                        # xử lý epsilon
                        while top == EPSILON and len(stack) > 0:
                            # pop stack
                            stack.pop()
                            ast.decorate_leaf("")
                            if len(stack) > 0:
                                # cập nhật top
                                top = stack[-1]
                                # cập nhật lá
                                # nhảy đến nút tiếp theo
                                ast.next()
                        # nếu top không phải là non-terminal thì dừng
                        if not isinstance(top, NonTerminalSymbol):
                            break
                    if not p_found:
                        # nếu ko tìm đc production thì báo lỗi cú pháp rồi skip đến input tiếp theo
                        err_log += "Cannot find Production!\n"
                        err_log += f"  Top: {top}\n"
                        err_log += f"  Input: {input.token}\n"
                        break
                # xử lý terminal
                if isinstance(top, TerminalSymbol):
                    # Nếu token lookahead thỏa mãn token ở top stack
                    # VD: (literal_boolean, false) isa (literal_boolean) -> True
                    if input.token.isa(Token(top.val)):
                        # gán giá trị cho nút lá
                        ast.decorate_leaf(input)
                        # nhảy đến nút tiếp theo
                        ast.next()
                        # pop stack pushdown automaton
                        stack.pop()
                    else:   # Nếu không thì báo lỗi cú pháp
                        err_log += "Unexpected Token!\n"
                        err_log += f"  Expected: {Token(top.val)}\n"
                        err_log += f"  But: {input}\n"
        # input cuối cùng là EOF
        if self.eof:
            ast.root.childs.append(Leaf(EOF, input))

        # syntax errors
        if top != EPSILON:
            err_log += f"Top not set to null: {top}\n"
        if len(stack) > 0:
            # Báo lỗi nếu stack không rỗng
            err_log += f"Stack not emptied: {stack}\n"

        return (ast, err_log)
