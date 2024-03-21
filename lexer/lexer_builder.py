from enum import Enum
from common.dfa import DFA
from common.state import AcceptingState, LookaheadAcceptingState, NormalState, DiscardState


class ReadMode(Enum):
    SKIP = -1
    KEYWORDS = 0
    START_STATE = 1
    TERMINAL_STATES = 2
    LOOKAHEAD_TERMINAL_STATES = 3
    GROUPS = 4
    TRANSITIONS = 5
    DISCARD_STATE = 6


class LexerBuilder(DFA):
    def __init__(self, lex_data_url: str) -> None:
        super().__init__()
        self.keywords: set[str] = set()  # các từ khóa
        # mapping từ tên của AC state -> các token label
        self.token_labels_of: dict[str, set[str]] = {}

        read_mode: ReadMode = ReadMode.SKIP

        with open(lex_data_url, "r", encoding="utf8") as file:
            for ln in file:
                args = ln.split()
                if ln[0] == "#" or len(args) == 0:
                    continue
                match args[0]:
                    case "KEYWORDS":
                        read_mode = ReadMode.KEYWORDS
                    case "START_STATE":
                        read_mode = ReadMode.START_STATE
                    case "DISCARD_STATE":
                        read_mode = ReadMode.DISCARD_STATE
                    case "ACCEPTING_STATES":
                        read_mode = ReadMode.TERMINAL_STATES
                    case "LOOKAHEAD_ACCEPTING_STATES":
                        read_mode = ReadMode.LOOKAHEAD_TERMINAL_STATES
                    case "GROUPS":
                        read_mode = ReadMode.GROUPS
                    case "TRANSITIONS":
                        read_mode = ReadMode.TRANSITIONS
                    case _:
                        match read_mode:
                            case ReadMode.KEYWORDS:
                                readln_keywords(self, args)
                            case ReadMode.START_STATE:
                                readln_start_state(self, args)
                            case ReadMode.DISCARD_STATE:
                                readln_discard_state(self, args)
                            case ReadMode.TERMINAL_STATES:
                                readln_accepting_states(self, args)
                            case ReadMode.LOOKAHEAD_TERMINAL_STATES:
                                readln_lookahead_accepting_states(self, args)
                            case ReadMode.GROUPS:
                                readln_groups(self, args)
                            case ReadMode.TRANSITIONS:
                                readln_transitions(self, args)


def preproccess(arg: str):
    match arg:
        case "blank":
            return ' '
        case 'tab':
            return '\t'
        case 'newline':
            return '\n'
        case _:
            return arg


def readln_keywords(lexer: LexerBuilder, args: list[str]):
    lexer.keywords = set(args)


def readln_start_state(lexer: LexerBuilder, args: list[str]):
    lexer.states[args[0]] = lexer.current_state = lexer.start_state = NormalState(
        args[0])
    print(f'Start state: {args[0]}')


def readln_accepting_states(lexer: LexerBuilder, args: list[str]):
    lexer.states[args[0]] = AcceptingState(next(iter(args)))
    # cho phép khai báo nhiều dòng
    lexer.token_labels_of.setdefault(args[0], set())
    for label in args:
        lexer.token_labels_of[args[0]].add(label)


def readln_lookahead_accepting_states(lexer: LexerBuilder, args: list[str]):
    lexer.states[args[0]] = LookaheadAcceptingState(next(iter(args)))
    # cho phép khai báo nhiều dòng
    lexer.token_labels_of.setdefault(args[0], set())
    for label in args:
        lexer.token_labels_of[args[0]].add(label)


def readln_groups(lexer: LexerBuilder, args: list[str]):
    for i in range(1, len(args)):
        args[i] = preproccess(args[i])
        lexer.input_to_group[args[i]] = args[0]


def readln_transitions(lexer: LexerBuilder, args: list[str]):
    # cho phép khai báo nhiều dòng
    state = lexer.states.setdefault(
        args[0],
        NormalState(args[0])
    )
    for i in range(1, len(args), 2):
        args[i] = preproccess(args[i].removeprefix("("))
        args[i + 1] = preproccess(args[i + 1].removesuffix(")"))
        state.add_transition(
            args[i], lexer.states.setdefault(
                args[i + 1],
                # Tất cả những state chưa được định nghĩa đều là normal (non accepting) state
                NormalState(args[i + 1])
            )
        )


def readln_discard_state(lexer: LexerBuilder, args: list[str]):
    lexer.discard_state = lexer.states[args[0]] = DiscardState(args[0])
