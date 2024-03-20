from state import State, BLANK_STATE


class DFA:
    '''DFA'''

    def __init__(self) -> None:

        self.start_state = BLANK_STATE      # trạng thái BẮT ĐẦU
        self.current_state = BLANK_STATE    # trạng thái HIỆN TẠI

        # trạng thái dùng để lược bỏ các từ tố không cần thiết
        self.discard_state = BLANK_STATE

        self.states: dict[any, 'State']     # ánh xạ từ tên -> trạng thái

        # ánh xạ từ đầu vào -> phân nhóm của nó
        self.input_to_group: dict[any, any]

    def transit(self, input: str):
        return self.current_state.transit(
            input,
            self.input_to_group.get(input, input)
        )

    def restart(self):
        self.current_state = self.start_state

    # def save(self):
    #     self.previous_state = self.current_state

    # def rollback(self):
    #     self.current_state = self.previous_state
