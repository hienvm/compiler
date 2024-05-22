from parser.ast.node import InnerNode, Leaf, Node
from parser.types import Epsilon


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
