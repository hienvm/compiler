from dataclasses import dataclass


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
        '''Check rỗng (chỉ chứa espilon)'''
        return len(self.rsyms) == 1 and self.rsyms[0] == EPSILON


def json_default(o):
    return o.__dict__


def str_to_symbol(val: str) -> Symbol:
    # epsilon
    if val == EPSILON.val:
        return EPSILON
    # "terminal"
    elif val[0] == '`' and val[-1] == '`':
        return TerminalSymbol(val[1:-1])
    # non-terminal
    else:
        return NonTerminalSymbol(val)


# ký tự rỗng
EPSILON = Epsilon("epsilon")
# ký tự cuối file
EOF = TerminalSymbol("EOF")
