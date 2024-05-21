from typing import Literal
from parser.ast.brackets import reduce_brackets, to_str_brackets_dfs
from parser.ast.node import InnerNode, Leaf, Node, sym2node
from parser.types import Symbol, NonTerminalSymbol, Epsilon, json_default
import json
from lexer.lexer_result import LexicalResult


class AST:
    def __init__(self, start: NonTerminalSymbol) -> None:
        # nút gốc
        self.root: InnerNode = InnerNode(start)
        # dfs stack, dùng để build ast, cần được đồng bộ với LL(1) stack
        self.dfs: list[Node] = []
        # nút hiện tại, dùng để build ast, cần được đồng bộ với LL(1) stack
        self.cur: Node = self.root

    def next(self):
        '''nhảy đến nút tiếp theo trên cây dfs (top của stack), cần được đồng bộ với LL(1) stack'''
        self.cur = self.dfs.pop()

    def expand_inner(self, symbols: tuple[Symbol, ...]):
        '''
        Mở rộng, tức là tạo các nút con từ top stack của LL(1), cho nút trong (non-terminal) hiện tại và cập nhật stack dfs.\n
        Cần được đồng bộ với LL(1) stack
        Args:
            symbols (tuple[Symbol, ...]): danh sách các symbols TỪ TRÁI SANG
        '''
        if isinstance(self.cur, InnerNode):
            childs = [sym2node(sym) for sym in symbols]
            self.cur.childs = childs
            # nút con bên trái cùng đặt lên đầu
            self.dfs.extend(reversed(childs))
        else:
            print("Error: Attempting to expand non-inner node.")

    def decorate_leaf(self, value: LexicalResult | Literal[""]):
        '''
        Hoàn thiện, tức là gán giá trị cho nút lá, (terminal hoặc epsilon).\n
        Cần được đồng bộ với LL(1) stack
        '''
        if isinstance(self.cur, Leaf):
            self.cur.value = value
        else:
            print(
                f"Error: Attempting to decorate non-leaf node {self.cur.symbol} -> {value}")

    def to_str(self, verbose: bool = False, indent: int = 2, reduce_level: Literal[0, 1, 2] = 2) -> str:
        if verbose:
            # convert cây sang json
            return json.dumps(self.root, indent=indent, default=json_default)

        # dfs từ gốc
        ls: list[str] = to_str_brackets_dfs(self.root)
        # reduce brackets
        if reduce_level in (1, 2):
            ls = reduce_brackets(ls, reduce_level)
            if len(ls) == 0:
                # Chương trình rỗng
                return "()"
            elif ls[0] == "invalid":
                return "Invalid bracket string."
        # hợp list lại thành string
        return " ".join(ls)

    def clear_epsilon(self):
        '''Post-parse Processing 1st step: Loại bỏ epsilon và các nhánh chỉ chứa epsilon'''
        # nút gốc không cần xóa
        clear_epsilon_helper(self.root)


def clear_epsilon_helper(node: Node) -> bool:
    '''Helper function để loại bỏ epsilon và các nhánh chỉ chứa epsilon\n
    Xử lý IN PLACE. Giá trị trả về dùng nội bộ trong hàm để kiểm tra xem có nên xóa nhánh hay không.'''
    if isinstance(node, Leaf) and isinstance(node.symbol, Epsilon):
        return True
    elif isinstance(node, InnerNode):
        # Nếu là innernode, check xem cần xóa hay không
        delete = True
        # check dfs
        for child in tuple(node.childs):
            # Nếu nút con không cần xóa
            if clear_epsilon_helper(child) is False:
                # nút cha cũng không cần xóa
                delete = False
            # Ngược lại thì xóa nút con
            else:
                node.childs.remove(child)
        return delete
    else:
        # Nút terminal thì không cần xóa
        return False
