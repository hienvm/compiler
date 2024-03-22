from lexer.state import BLANK_STATE


class DFA:
    '''DFA'''

    def __init__(self) -> None:
        self.start_state = BLANK_STATE      # trạng thái BẮT ĐẦU
        self.current_state = BLANK_STATE    # trạng thái HIỆN TẠI

        # ánh xạ từ đầu vào -> phân nhóm của nó
        self.input_to_group: dict[str, str] = {}

    def transit(self, input: str):
        return self.current_state.transit(
            input,
            self.input_to_group.get(input, input)
        )

    def reset(self):
        self.current_state = self.start_state

    # def save(self):
    #     self.previous_state = self.current_state

    # def rollback(self):
    #     self.current_state = self.previous_state
