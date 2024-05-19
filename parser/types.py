'''Định nghĩa các loại symbol và production, cùng một số hàm tiện ích'''
from dataclasses import dataclass
from lexer.lexer_result import LexicalResult


@dataclass(frozen=True, eq=True)
# Cho phép hash
class Symbol:
    val: str


class NonTerminalSymbol(Symbol):
    def __str__(self) -> str:
        return self.val


class TerminalSymbol(Symbol):
    def __str__(self) -> str:
        return f"`{self.val}`"


class Epsilon(Symbol):
    def __str__(self) -> str:
        return EPSILON.val


class Production:
    '''Sản xuất lsym -> rsyms[1] rsyms[2] ... '''

    def __init__(self, lsym: NonTerminalSymbol, rsyms: tuple[Symbol, ...]) -> None:
        self.lsym = lsym
        self.rsyms = rsyms

    def __str__(self) -> str:
        s = f'{str(self.lsym)} ->'
        for sym in self.rsyms:
            s += " " + str(sym)
        return s

    def empty(self) -> bool:
        '''Check rỗng (chỉ chứa espilon ở vế phải)'''
        return len(self.rsyms) == 1 and self.rsyms[0] == EPSILON


# ký tự rỗng
EPSILON = Epsilon("epsilon")
# ký tự cuối file
EOF = TerminalSymbol("EOF")


def json_default(o):
    '''format sang json'''
    if isinstance(o, Symbol):
        return str(o)
    if isinstance(o, LexicalResult):
        return o.lexeme
    else:
        return o.__dict__


def raw2production(raw: str) -> Production:
    '''Tạo production từ raw string, dùng cho i/o'''
    # tách các tham số arg theo khoảng trắng
    args = raw.split()
    # non-terminal vế trái
    lsym = NonTerminalSymbol(args[0])
    # thêm từ arg thứ 2 trở đi (sau lsym và "->") vào danh sách vế phải sản suất
    rsyms = tuple(map(raw2sym, args[2:]))

    return Production(lsym, rsyms)


def raw2sym(raw: str) -> Symbol:
    '''chuyển đổi raw string thành symbol, dùng cho i/o'''
    # epsilon
    if raw == EPSILON.val:
        return EPSILON
    # "terminal"
    elif raw[0] == '`' and raw[-1] == '`':
        return TerminalSymbol(raw[1:-1])
    # non-terminal
    else:
        return NonTerminalSymbol(raw)


def raw2table(raw) -> dict[NonTerminalSymbol, dict[TerminalSymbol, Production]]:
    '''convert từ raw dict sang table'''
    table: dict[NonTerminalSymbol, dict[TerminalSymbol, Production]] = {}
    for row in raw:
        table[NonTerminalSymbol(row)] = {
            TerminalSymbol(col[1:-1]): raw2production(raw[row][col]) for col in raw[row]
        }
    return table
