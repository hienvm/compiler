from typing import Literal
from parser.ast.associativity import enforce_associativity_helper
from parser.ast.brackets import reduce_brackets, to_str_brackets_dfs
from parser.ast.epsilon import clear_epsilon_helper
from parser.ast.node import InnerNode, Leaf, Node, sym2node
from parser.types import Symbol, NonTerminalSymbol, json_default
import json
from lexer.lexer_result import LexicalResult


class AST:
    def __init__(self, start: NonTerminalSymbol) -> None:
        # nút gốc
        self.root: InnerNode = InnerNode(start)

        # sau khi build xong thì không còn cần 2 biến này
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

    def to_str(
        self,
        verbose: bool = False,
        indent: int = 2,
        reduce_level: Literal[0, 1, 2] = 2,
        multi_ln: bool = False
    ) -> str:
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

        # in nhiều dòng
        if multi_ln:
            res = ""
            
            tab_level = 0
            for s in ls:
                if s == ")":
                    tab_level -= 1
                res += "\n" + ''.join([' '] * indent * tab_level) + s
                if s == "(":
                    tab_level += 1
                
            return res

        # hợp list lại thành string
        return " ".join(ls)

    def clear_epsilon(self):
        '''Hậu xử lý: Loại bỏ epsilon và các nhánh chỉ chứa epsilon'''
        # nút gốc không cần xóa
        clear_epsilon_helper(self.root)

    def enforce_associativity(self):
        '''Hậu xử lý: Đảm bảo Left/Right Associativity'''
        enforce_associativity_helper(self.root)
