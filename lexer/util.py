from enum import Enum


class ReadMode(Enum):
    KEYWORDS = 0
    START_STATE = 1
    TERMINAL_STATES = 2
    LOOKAHEAD_TERMINAL_STATES = 3
    GROUPS = 4
    TRANSITIONS = 5


class LexerResult:
    def __init__(self, labels: set[str], lexeme: str) -> None:
        self.labels = labels
        self.lexeme = lexeme


class LexicalError:
    pass
