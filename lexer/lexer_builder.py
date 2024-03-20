from enum import Enum
from common.dfa import DFA
from common.state import State, AcceptingState, LookaheadAcceptingState, NormalState, DiscardState


class ReadMode(Enum):
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
        self.lexeme: str = ""            # xâu hiện tại
        # mapping từ tên của AC state -> các token label
        self.token_labels_of: dict[str, set[str]] = {}

        read_mode: ReadMode

        with open(lex_data_url, "r") as file:
            lines = file.readlines()
            for ln in lines:
                if ln[0] == "#":
                    continue
                match ln:
                    case "":
                        continue
                    case "KEYWORDS":
                        read_mode = ReadMode.KEYWORDS
                    case "START_STATE":
                        read_mode = ReadMode.START_STATE
                    case "DISCARD_STATE":
                        read_mode = ReadMode.DISCARD_STATE
                    case "TERMINAL_STATES":
                        read_mode = ReadMode.TERMINAL_STATES
                    case "LOOKAHEAD_TERMINAL_STATES":
                        read_mode = ReadMode.LOOKAHEAD_TERMINAL_STATES
                    case "GROUPS":
                        read_mode = ReadMode.GROUPS
                    case "TRANSITIONS":
                        read_mode = ReadMode.TRANSITIONS
                    case _:
                        match read_mode:
                            case ReadMode.KEYWORDS:
                                readln_keywords(self, ln)
                            case ReadMode.START_STATE:
                                readln_start_state(self, ln)
                            case ReadMode.DISCARD_STATE:
                                readln_discard_state(self, ln)
                            case ReadMode.TERMINAL_STATES:
                                readln_accepting_states(self, ln)
                            case ReadMode.LOOKAHEAD_TERMINAL_STATES:
                                readln_lookahead_accepting_states(self, ln)
                            case ReadMode.GROUPS:
                                readln_groups(self, ln)
                            case ReadMode.TRANSITIONS:
                                readln_transitions(self, ln)


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


def readln_keywords(lexer: LexerBuilder, ln: str):
    lexer.keywords = set(ln.split())


def readln_start_state(lexer: LexerBuilder, ln: str):
    lexer.states[ln] = lexer.current_state = lexer.start_state = NormalState(
        ln)


def readln_accepting_states(lexer: LexerBuilder, ln: str):
    args = ln.split()
    lexer.states[args[0]] = AcceptingState(next(args))
    for label in args:
        lexer.token_labels_of[args[0]].add(label)


def readln_lookahead_accepting_states(lexer: LexerBuilder, ln: str):
    args = ln.split()
    lexer.states[args[0]] = LookaheadAcceptingState(next(args))
    for label in args:
        lexer.token_labels_of[args[0]].add(label)


def readln_groups(lexer: LexerBuilder, ln: str):
    args = ln.split()
    for i in range(1, len(args)):
        args[i] = preproccess(args[i])
        lexer.input_to_group[args[i]] = args[0]


def readln_transitions(lexer: LexerBuilder, ln: str):
    args = ln.split()
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


def readln_discard_state(lexer: LexerBuilder, ln: str):
    lexer.discard_state = lexer.states[ln] = DiscardState(ln)
