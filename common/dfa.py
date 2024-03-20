from state import State, BLANK_STATE


class DFA:
    '''DFA'''

    def __init__(self) -> None:
        # trạng thái BẮT ĐẦU
        self.start_state = BLANK_STATE
        self.current_state = BLANK_STATE        # trạng thái HIỆN TẠI
        self.previous_state = BLANK_STATE      # trạng thái gần nhất được lưu
        self.states: dict[any, 'State']     # ánh xạ từ tên -> trạng thái
        self.terminal_states: dict[any, 'State']  # ánh xạ từ tên -> trạng thái
        # ánh xạ từ đầu vào -> phân nhóm của nó
        self.input_to_group: dict[any, any]

    def restart(self):
        self.current_state = self.start_state

    def save(self):
        self.previous_state = self.current_state

    def rollback(self):
        self.current_state = self.previous_state
