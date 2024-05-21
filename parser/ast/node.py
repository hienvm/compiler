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

    def merge_up(self, child: 'InnerNode') -> 'InnerNode':
        '''
        Hợp nhất nút con vào nút cha và trả về nút gốc mới:\n
        1. Loại nút child ra khỏi danh sách con.\n
        2. Insert các nút con của child vào đúng vị trí idx của child.\n
        3. Trả về nút gốc mới (chính mình).
        '''
        idx = self.childs.index(child)
        self.childs.remove(child)
        self.childs = self.childs[:idx] + child.childs + self.childs[idx:]
        return self

    def rotate_left(self, child: 'InnerNode') -> 'InnerNode':
        '''
        Xoay trái và trả về nút gốc mới:\n
        1. Loại nút child ra khỏi danh sách con.\n
        2. Cho self làm con trái của child.\n
        3. Trả về nút gốc mới (nút con).
        '''
        self.childs.remove(child)
        child.childs.insert(0, self)
        return child


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
