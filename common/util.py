class Position:
    def __init__(self, ln: int, col: int) -> None:
        self.ln = ln    # hàng
        self.col = col  # cột

    def copy(self) -> 'Position':
        return Position(self.ln, self.col)

    def __str__(self) -> str:
        return f'({self.ln}, {self.col})'


class Location:
    def __init__(self, start: Position, end: Position) -> None:
        '''pointer copy'''
        self.start = start
        self.end = end.copy()

    def __str__(self) -> str:
        return f'From {self.start} to {self.end}'

def is_newline(input: str, next: str) -> bool:
    '''Tận dụng lookahead để xuống dòng cho \\n, \\r, \\r\\n'''
    match input:
        case '\n':
            return True
        case '\r':
            if next != '\n':
                return True
    return False
