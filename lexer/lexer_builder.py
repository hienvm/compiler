from enum import Enum
from functools import reduce
from lexer.state import BLANK_STATE, AcceptingState, Escape, LookaheadAcceptingState, State, TerminalState, ErrorState


class ReadMode(Enum):
    SKIP = -1
    KEYWORDS = 0
    START_STATE = 1
    ACCEPTING_STATES = 2
    LOOKAHEAD_ACCEPTING_STATES = 3
    GROUPS = 4
    TRANSITIONS = 5
    TERMINAL_STATES = 6
    ERROR_STATES = 7
    ESCAPES = 8


class LexerBuilder:
    def __init__(self, lex_data_url: str) -> None:
        '''Xây dựng lexer dfa từ file .dat'''
        self.start_state: State = BLANK_STATE      # trạng thái BẮT ĐẦU
        self.current_state: State | None = BLANK_STATE    # trạng thái HIỆN TẠI

        self.keywords: set[str] = set()  # các từ khóa
        # ánh xạ từ đầu vào -> phân nhóm của nó
        self.input_to_group: dict[str | None, str] = {}

        # mapping từ tên -> trạng thái, chỉ dùng trong giai đoạn build lexer
        states: dict[str, 'State'] = {}

        read_mode: ReadMode = ReadMode.SKIP

        with open(lex_data_url, "r", encoding="utf8") as file:
            # Đọc từng dòng
            for ln in file:
                # Xử lý comment
                if ln[0] == "#":
                    continue

                # Tách các tham số theo khoảng trắng
                args = ln.split()
                if len(args) == 0:
                    continue

                # Tiền xử lý cho các macro
                for i, x in enumerate(args):
                    args[i] = preproccess(x)

                match args[0]:
                    case "KEYWORDS":
                        read_mode = ReadMode.KEYWORDS
                    case "START_STATE":
                        read_mode = ReadMode.START_STATE
                    case "TERMINAL_STATES":
                        read_mode = ReadMode.TERMINAL_STATES
                    case "ACCEPTING_STATES":
                        read_mode = ReadMode.ACCEPTING_STATES
                    case "LOOKAHEAD_ACCEPTING_STATES":
                        read_mode = ReadMode.LOOKAHEAD_ACCEPTING_STATES
                    case "ERROR_STATES":
                        read_mode = ReadMode.ERROR_STATES
                    case "ESCAPES":
                        read_mode = ReadMode.ESCAPES
                    case "GROUPS":
                        read_mode = ReadMode.GROUPS
                    case "TRANSITIONS":
                        read_mode = ReadMode.TRANSITIONS
                    case _:
                        match read_mode:
                            case ReadMode.KEYWORDS:
                                readln_keywords(self, args, states)
                            case ReadMode.START_STATE:
                                readln_start_state(self, args, states)
                            case ReadMode.TERMINAL_STATES:
                                readln_terminal_states(self, args, states)
                            case ReadMode.ACCEPTING_STATES:
                                readln_accepting_states(self, args, states)
                            case ReadMode.LOOKAHEAD_ACCEPTING_STATES:
                                readln_lookahead_accepting_states(
                                    self, args, states)
                            case ReadMode.ERROR_STATES:
                                readln_error_states(self, args, states)
                            case ReadMode.ESCAPES:
                                readln_escapes(self, args, states)
                            case ReadMode.GROUPS:
                                readln_groups(self, args, states)
                            case ReadMode.TRANSITIONS:
                                readln_transitions(self, args, states)


def preproccess(arg: str):
    '''Xử lý các macro cho file .dat'''
    match arg:
        case "blank":
            return ' '
        case 'tab':
            return '\t'
        case 'LF':
            return '\n'
        case 'CR':
            return '\r'
        case 'FF':
            return '\f'
        case 'backspace':
            return '\b'
        case 'hash':
            return '#'
        case _:
            return arg


def readln_keywords(lexer: LexerBuilder, args: list[str], states: dict[str, State]):
    # cho phép nhiều dòng
    lexer.keywords.update(args)


def readln_start_state(lexer: LexerBuilder, args: list[str], states: dict[str, State]):
    states[args[0]] = lexer.current_state = lexer.start_state = State(
        args[0])


def readln_accepting_states(lexer: LexerBuilder, args: list[str], states: dict[str, State]):
    state = states[args[0]] = AcceptingState(args[0])
    state.token.labels.update(args[1:])


def readln_lookahead_accepting_states(lexer: LexerBuilder, args: list[str], states: dict[str, State]):
    state = states[args[0]] = LookaheadAcceptingState(args[0])
    state.token.labels.update(args[1:])


def readln_groups(lexer: LexerBuilder, args: list[str], states: dict[str, State]):
    for i in range(1, len(args)):
        lexer.input_to_group[args[i]] = args[0]


def readln_transitions(lexer: LexerBuilder, args: list[str], states: dict[str, State]):
    # cho phép khai báo nhiều dòng
    state = states.setdefault(
        args[0],
        State(args[0])
    )
    for i in range(1, len(args), 2):
        args[i] = preproccess(args[i].removeprefix("("))
        args[i + 1] = preproccess(args[i + 1].removesuffix(")"))
        state.add_transition(
            args[i], states.setdefault(
                args[i + 1],
                # Tất cả những state chưa được định nghĩa đều là normal (non accepting) state
                State(args[i + 1])
            )
        )


def readln_terminal_states(lexer: LexerBuilder, args: list[str], states: dict[str, State]):
    states[args[0]] = TerminalState(args[0])


def readln_error_states(lexer: LexerBuilder, args: list[str], states: dict[str, State]):
    msg = reduce(lambda x, y: x + ' ' + y, args[1:])
    states[args[0]] = ErrorState(args[0], msg)


def readln_escapes(lexer: LexerBuilder, args: list[str], states: dict[str, State]):
    state = states.setdefault(args[0], State(args[0]))
    state.escape = Escape(
        args[1],
        reduce(lambda x, y: x + y, args[2:], '')
    )
