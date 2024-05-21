from lexer.lexer_result import LexicalResult
from typing import Literal
from parser.types import Epsilon, NonTerminalSymbol, Symbol, TerminalSymbol


class Node:
    def __init__(self, symbol: Symbol) -> None:
        self.symbol = symbol


class InnerNode(Node):
    def __init__(self, symbol: NonTerminalSymbol, childs: list[Node] | None = None) -> None:
        """Nút trong AST (non-terminal)

        Args:
            symbol (NonTerminalSymbol): Symbol ứng với Node.
            childs (tuple[Node, ...] | None, optional): Danh sách nút con.
        """
        super().__init__(symbol)
        self.childs: list[Node] = []
        if childs is not None:
            self.childs = childs


class Leaf(Node):
    '''Lá AST (terminal hoặc epsilon)'''

    def __init__(self, symbol: TerminalSymbol | Epsilon, value: LexicalResult | Literal["Undefined", ""] = "Undefined") -> None:
        """Lá AST (terminal hoặc epsilon)

        Args:
            symbol (TerminalSymbol | Epsilon): Symbol ứng với Node
            value (LexicalResult | Literal[&quot;Undefined&quot;, &quot;&quot;], optional): Giá trị nút lá (LexicalResult ứng với terminal hoặc xâu rỗng cho epsilon). Defaults to "Undefined".
        """

        super().__init__(symbol)
        self.value = value


def sym2node(sym: Symbol) -> Node:
    '''factory function tạo ra node tương ứng từ sym'''
    if isinstance(sym, TerminalSymbol | Epsilon):
        return Leaf(sym)
    elif isinstance(sym, NonTerminalSymbol):
        return InnerNode(sym)
    else:
        raise TypeError()
