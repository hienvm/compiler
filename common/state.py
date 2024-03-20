class State:
    """DFA state"""

    def __init__(self, name: str) -> None:
        self.name = name

        # dùng dict(hash map từ input -> trạng thái tiếp theo) để quản lý các bước chuyển trạng thái
        self.transitions: dict[any, 'State'] = {}

    def add_transition(self, input, target: 'State') -> None:
        self.transitions[input] = target

    def transit(self, input, group) -> 'State' | None:
        '''Thực hiện bước chuyển trạng thái\n
        Thứ tự check: input -> group -> "other"'''
        target = self.transitions.get(input, None)
        if target is not None:
            return self.transitions[input]

        target = self.transitions.get(group, None)
        if target is not None:
            return self.transitions[input]

        target = self.transitions.get("other", None)

        return target


class AcceptingState(State):
    def __init__(self, name: str) -> None:
        super().__init__(name, type)
        self.token_labels = set()       # Danh sách các


class LookaheadAcceptingState(AcceptingState):
    def __init__(self, name: str) -> None:
        super().__init__(name, type)


class NormalState(State):
    def __init__(self, name: str) -> None:
        super().__init__(name)


class DiscardState(State):
    pass

BLANK_STATE = State("", "")
