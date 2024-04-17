from lexer.state_attributes import Token


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
        return f"At {self.location}: Token = {self.token}; Lexeme = {self.lexeme}"


class LexicalError:
    '''Kết quả lỗi'''

    def __init__(self, spelling: str, location: Location, msg: str = '"Unrecognized spelling"') -> None:
        self.spelling = spelling
        self.location = location
        self.msg = msg

    def __str__(self) -> str:
        '''Thông báo lỗi'''
        return f'At {self.location}: Error {self.msg}: {self.spelling}'
