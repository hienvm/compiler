class Position:
    def __init__(self, ln: int, col: int) -> None:
        self.ln = ln
        self.col = col

    def copy(self) -> 'Position':
        return Position(self.ln, self.col)


def is_newline(input: str, next: str) -> bool:
    '''Tận dụng lookahead để xuống dòng cho \\n, \\r, \\r\\n'''
    match input:
        case '\n':
            return True
        case '\r':
            if next != '\n':
                return True
    return False
