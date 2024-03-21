class State:
    """DFA state"""

    def __init__(self, name: str) -> None:
        self.name = name

        # dùng dict(hash map từ input -> trạng thái tiếp theo) để quản lý các bước chuyển trạng thái
        self.transitions: dict[any, 'State'] = {}

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


class AcceptingState(State):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.token_labels = set()       # Danh sách các nhãn của token tương ứng


class LookaheadAcceptingState(AcceptingState):
    '''Nếu việc nhìn trước 1 input(ký tự) đưa 1 state tới state này thì accept toàn bộ lexeme hiện tại'''
    pass


class NormalState(State):
    def __init__(self, name: str) -> None:
        super().__init__(name)


class DiscardState(State):
    '''Dùng để lược bỏ các token không quan trọng'''
    pass


BLANK_STATE = State("")
