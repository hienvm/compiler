class State:
    """DFA state"""

    def __init__(self, name: str) -> None:
        self.name = name

        # dùng dict(hash map từ input -> trạng thái tiếp theo) để quản lý các bước chuyển trạng thái
        self.__transitions: dict[any, 'State'] = {}

    def add_transition(self, input, target: 'State') -> None:
        self.__transitions[input] = target

    def transit(self, input) -> 'State':
        return self.__transitions[input]
