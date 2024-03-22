from typing import Union


class Token:
    def __init__(self, labels: set[str] | None = None) -> None:
        self.labels = labels if labels is not None else set()  # Các nhãn của token

    def isa(self, other: Union[str, set[str], 'Token']) -> bool:
        """Check xem token này có chứa (hay nói cách khác là thỏa mãn) một Token khác hay không.

        Args:
            other (str | set[str] | &#39;Token): label, set[labels] hoặc Token khác

        Returns:
            bool: đúng nếu other là tập con của self, false nếu ngược lại
        """
        if isinstance(other, str):
            # VD: Token({"literal", "float"}).isa("literal") -> True
            return other in self.labels
        elif isinstance(other, set):
            # VD: Token({"literal", "float", "e_notation"}).isa({"e_notation", "float"}) -> True
            return self.labels.issuperset(other)
        elif isinstance(other, Token):
            # VD: Token({"literal", "float", "e_notation"}).isa(Token({"float"})) -> True
            return self.labels.issuperset(other.labels)

    def add(self, label: str):
        self.labels.add(label)

    def __str__(self) -> str:
        s = ''
        for label in self.labels:
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
        """pointer copy\n
        Địa chỉ của một xâu trong file.

        Args:
            start (Position): vị trí ký tự bắt đầu
            end (Position): vị trí ký tự kết thúc
        """
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f'{self.start}..{self.end}'


class LexicalResult:
    def __init__(self, lexeme: str, token: Token, location: Location) -> None:
        """Kết quả chấp nhận của Lexer.

        Args:
            lexeme (str): lexeme
            token (Token): token (bao gồm một hoặc nhiều nhãn)
            location (Location): địa chỉ của lexeme trong file input
        """
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
        case 'LF':
            return '\n'
        case 'CR':
            return '\r'
        case 'FF':
            return '\f'
        case _:
            return arg
