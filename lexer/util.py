class Token:
    def __init__(self, token_labels: set[str]) -> None:
        self.token_labels = token_labels  # Các nhãn của token

    def __eq__(self, __value: object) -> bool:
        '''so sánh xem một label hoặc một set của nhiều label có khớp một token không'''
        if isinstance(__value, str):
            # VD: "float" == Token(("literal", "float")) -> True
            return __value in self.token_labels
        elif isinstance(__value, set):
            # VD: ("e_notation", "float") == Token(("literal", "float", "e_notation")) -> True
            return self.token_labels.issuperset(__value)

    def __str__(self) -> str:
        s = ''
        for label in self.token_labels:
            s += label + ' '
        return s


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
        self.end = end

    def __str__(self) -> str:
        return f'{self.start}..{self.end}'


class LexicalResult:
    def __init__(self, lexeme: str, token: Token, location: Location) -> None:
        self.lexeme = lexeme
        self.token = token
        self.location = location

    def __str__(self) -> str:
        return f"{self.location}: Token = {self.token}; Lexeme = {self.lexeme}"


class LexicalError:
    def __init__(self, spelling: str, location: Location) -> None:
        self.spelling = spelling
        self.location = location

    def __str__(self) -> str:
        '''Thông báo lỗi mặc định'''
        return f"{self.location}: Unrecognized spelling: {self.spelling}"


def is_newline(input: str, next: str) -> bool:
    '''Tận dụng lookahead để xuống dòng cho \\n, \\r, \\r\\n'''
    match input:
        case '\n':
            return True
        case '\r':
            if next != '\n':
                return True
    return False


def preproccess(arg: str):
    '''Xử lý các macro cho file .dat'''
    match arg:
        case "blank":
            return ' '
        case 'tab':
            return '\t'
        case 'newline':
            return '\n'
        case _:
            return arg
