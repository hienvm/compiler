from state import State


class Automaton:
    '''DFA'''

    def __init__(self) -> None:
        self.current: State                 # trạng thái HIỆN TẠI
        self.states: dict[any, 'State']     # ánh xạ từ tên -> trạng thái
        self.start_state: State             # trạng thái BẮT ĐẦU
        self.end_states = set()             # TÊN của các trạng thái KẾT THÚC

    def from_transition_line(self, line: str) -> 'State':
        """Tạo state mới từ 1 dòng, nếu state đã tồn tại trước đó thì bổ sung (hoặc ghi đè) các transition

        Args:
            line (str): dòng đọc vào từ file .dat

        Returns:
            State: state được tạo
        """
        pass
