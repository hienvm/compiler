from typing import Literal
from parser.types import Symbol, NonTerminalSymbol, TerminalSymbol, Epsilon, EPSILON, json_default
import json
from lexer.lexer_result import LexicalResult


class Node:
    def __init__(self, symbol: Symbol) -> None:
        self.symbol = symbol


class InnerNode(Node):
    def __init__(self, symbol: NonTerminalSymbol, childs: tuple[Node, ...] | None = None) -> None:
        super().__init__(symbol)
        self.childs: tuple[Node, ...] = tuple()
        if childs is not None:
            self.childs = childs


class Leaf(Node):
    def __init__(self, symbol: TerminalSymbol | Epsilon, value: LexicalResult | Literal["Undefined"] | Literal[""] = "Undefined") -> None:
        super().__init__(symbol)
        self.value = value


class AST:
    def __init__(self, start: NonTerminalSymbol) -> None:
        # nút gốc
        self.root: InnerNode = InnerNode(start)
        # dfs stack, dùng để build ast
        self.dfs: list[Node] = []
        # nút hiện tại, dùng để build ast
        self.cur: Node = self.root

    def next(self):
        '''nhảy đến nút tiếp theo trên cây dfs (top của stack)'''
        self.cur = self.dfs.pop()

    def expand_nonterminal(self, symbols: tuple[Symbol, ...]):
        '''
        Mở rộng, tức là tạo các nút con, cho nút trong (non-terminal) hiện tại và cập nhật stack dfs.
        Args:
            symbols (tuple[Symbol, ...]): danh sách các symbols TỪ TRÁI SANG
        '''
        if isinstance(self.cur, InnerNode):
            childs = tuple([sym2node(sym) for sym in symbols])
            self.cur.childs = childs
            # nút con bên trái cùng đặt lên đầu
            self.dfs.extend(reversed(childs))
        else:
            print("Error: Attempting to expand non-inner node.")

    def decorate_leaf(self, value: LexicalResult | Literal[""]):
        '''
        Hoàn thiện, tức là gán giá trị cho nút lá, (terminal hoặc epsilon).
        '''
        if isinstance(self.cur, Leaf):
            self.cur.value = value
        else:
            print(
                f"Error: Attempting to decorate non-leaf node {self.cur.symbol} -> {value}")

    def to_str(self, verbose: bool = False) -> str:
        if verbose:
            return json.dumps(self.root, indent=2, default=json_default)
        res = ""
        return res


def sym2node(sym: Symbol) -> Node:
    '''factory function tạo ra node tương ứng từ sym'''
    if isinstance(sym, TerminalSymbol | Epsilon):
        return Leaf(sym)
    elif isinstance(sym, NonTerminalSymbol):
        return InnerNode(sym)
    else:
        raise TypeError()
