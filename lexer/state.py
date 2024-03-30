from lexer.util import Token


class Escape:
    def __init__(self, old: int, new: str) -> None:
        """Chuỗi escape. Khi đến trạng thái được định nghĩa escape thì Lexer sẽ thay len ký tự cuối lexeme bằng xâu new_val.

        Args:
            old (str): xâu cũ
            new (str): xâu mới
        """
        self.old = old
        self.new = new

class State:
    """DFA state"""

    def __init__(self, name: str, escape: Escape | None = None) -> None:
        """trạng thái cho dfa

        Args:
            name (str): tên trạng thái
            escape (Escape | None, optional): chuỗi escape. Defaults to None.
        """
        self.name = name
        self.escape = escape

        # dùng dict(hash map từ input -> trạng thái tiếp theo) để quản lý các bước chuyển trạng thái
        self.transitions: dict[str | None, 'State'] = {}

    def add_transition(self, input: str, target: 'State') -> None:
        self.transitions[input] = target

    def transit(self, input: str | None, group: str):
        '''Thực hiện bước chuyển trạng thái\n
        Thứ tự check: input -> group -> "other"'''
        target = self.transitions.get(input, None)
        if target is not None:
            return target

        target = self.transitions.get(group, None)
        if target is not None:
            return target

        target = self.transitions.get("other", None)

        return target

    def __hash__(self) -> int:
        '''2 state == nếu trùng tên'''
        return self.name.__hash__()

    def __eq__(self, __value: object) -> bool:
        '''2 state == nếu trùng tên'''
        if isinstance(__value, State):
            return self.name == __value.name
        elif isinstance(__value, str):
            return self.name == __value
        else:
            return False


class TerminalState(State):
    '''Dùng để reset DFA'''
    pass


class AcceptingState(TerminalState):
    '''Trả về kết quả được chấp nhận'''
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.token = Token()


class Lookahead:
    '''interface dùng để gán nhãn cho các lookahead state'''
    pass


class LookaheadAcceptingState(AcceptingState, Lookahead):
    '''Nếu việc nhìn trước 1 input(ký tự) đưa 1 state tới state này thì accept toàn bộ lexeme hiện tại'''
    pass


class ErrorState(TerminalState):
    def __init__(self, name: str, msg: str) -> None:
        super().__init__(name)
        self.msg = msg

BLANK_STATE = State("")
