from enum import Enum
from common.dfa import DFA
from common.state import State
from lexer.util import ReadMode


class LexerBuilder(DFA):
    def __init__(self, lex_data_url: str) -> None:
        super().__init__()
        self.keywords = set()
        self.lexeme = ""

        readMode: ReadMode

        with open(lex_data_url, "r") as file:
            lines = file.readlines()
            for ln in lines:
                if ln[0] == "#":
                    continue
                match ln:
                    case "":
                        continue
                    case "KEYWORDS":
                        readMode = ReadMode.KEYWORDS
                    case "START_STATE":
                        readMode = ReadMode.START_STATE
                    case "TERMINAL_STATES":
                        readMode = ReadMode.TERMINAL_STATES
                    case "LOOKAHEAD_TERMINAL_STATES":
                        readMode = ReadMode.LOOKAHEAD_TERMINAL_STATES
                    case "GROUPS":
                        readMode = ReadMode.GROUPS
                    case "TRANSITIONS":
                        readMode = ReadMode.TRANSITIONS
                    case _:
                        match readMode:
                            case ReadMode.KEYWORDS:
                                readln_keywords(self, ln)
                            case ReadMode.START_STATE:
                                readln_start_state(self, ln)
                            case ReadMode.TERMINAL_STATES:
                                readln_terminal_states(
                                    self, ln, "LOOKAHEAD_TERMINAL"
                                )
                            case ReadMode.LOOKAHEAD_TERMINAL_STATES:
                                readln_terminal_states(self, ln, "TERMINAL")
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


def readln_keywords(lexer: DFA, ln: str):
    lexer.keywords = set(ln.split())


def readln_start_state(lexer: DFA, ln: str):
    lexer.states[ln] = lexer.current_state = lexer.start_state = State(
        ln, "NON_TERMINAL"
    )


def readln_terminal_states(lexer: DFA, ln: str, type: str):
    args = ln.split()
    lexer.terminal_states[args[0]] = lexer.states[args[0]] = State(
        args[0], type
    )


def readln_groups(lexer: DFA, ln: str):
    args = ln.split()
    for i in range(1, len(args)):
        args[i] = preproccess(args[i])
        lexer.input_to_group[args[i]] = args[0]


def readln_transitions(lexer: DFA, ln: str):
    args = ln.split()
    state = lexer.states.setdefault(
        args[0], State(args[0], "NON_TERMINAL"))
    for i in range(1, len(args), 2):
        args[i].removeprefix("(")
        args[i + 1].removesuffix(")")
        args[i] = preproccess(args[i])
        args[i + 1] = preproccess(args[i + 1])
        state.add_transition(
            args[i], lexer.states.setdefault(
                args[i + 1],
                State(args[i + 1], "NON_TERMINAL")
            )
        )
