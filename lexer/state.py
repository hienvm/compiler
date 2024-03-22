from lexer.util import Token


class State:
    """DFA state"""

    def __init__(self, name: str) -> None:
        self.name = name

        # dùng dict(hash map từ input -> trạng thái tiếp theo) để quản lý các bước chuyển trạng thái
        self.transitions: dict[str, 'State'] = {}

    def add_transition(self, input: str, target: 'State') -> None:
        self.transitions[input] = target

    def transit(self, input: str, group: str):
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


class LookaheadAcceptingState(AcceptingState):
    '''Nếu việc nhìn trước 1 input(ký tự) đưa 1 state tới state này thì accept toàn bộ lexeme hiện tại'''
    pass


BLANK_STATE = State("")
