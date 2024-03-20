from enum import Enum


# class StateType(Enum):
#     NON_TERMINAL = 0
#     TERMINAL = 1
#     LOOKAHEAD_TERMINAL = 2


class State:
    """DFA state"""

    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type

        # dùng dict(hash map từ input -> trạng thái tiếp theo) để quản lý các bước chuyển trạng thái
        self.transitions: dict[any, 'State'] = {}

    def add_transition(self, input, target: 'State') -> None:
        self.transitions[input] = target

    def transit(self, input, group) -> 'State':
        return self.transitions[input]


BLANK_STATE = State("", "")
