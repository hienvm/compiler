from parser.ast.node import Node, InnerNode

LEFT_ASSOC = "_lassoc"
'''
Hậu tố dùng để nhận diện non-terminal trung gian được tạo ra từ thao tác Left Recursion Elimination.\n
Áp dụng cho các phép toán left-associative (phép cộng, phép or, ... ).\n
VD:\n
Từ: A -> A + B | B\n
Ta đổi thành:\n
    A -> B A_lassoc\n
    A_lassoc -> + B A_lassoc\n
    A_lassoc -> epsilon\n
'''


RIGHT_ASSOC = "_rassoc"
'''
Hậu tố dùng để nhận diện non-terminal trung gian được tạo ra từ thao tác Left Factoring.\n
Áp dụng cho các phép toán right-associative (phép gán).\n
VD:\n
Từ: A -> B = A | B\n
Ta đổi thành:\n
    A -> B A_rassoc\n
    A_rassoc -> = A\n
    A_rassoc -> epsilon\n
'''


def enforce_associativity_helper(node: Node) -> Node:
    '''
    Đảm bảo associativity (luật kết hợp) thực hiện từ TRÊN XUỐNG:\n
    + Rotate_left để được Left Associativity\n
    + Merge_up để được Right Associativity\n
    Trả về nút gốc mới của subtree hiện tại.\n
    '''
    if not isinstance(node, InnerNode):
        # Chỉ quan tâm đến nút trong
        return node
    # chỉ số nút con
    idx = 0
    while idx < len(node.childs):
        child = node.childs[idx]
        if isinstance(child, InnerNode):
            # Chỉ quan tâm đến nút trong
            # Nếu child là nonterminal mới được tạo ra từ việc loại bỏ left recursion
            if child.symbol.val.endswith(LEFT_ASSOC):
                # Để đảm bảo được Left Associativity thì ta quay trái nút cha <- nút con
                # Nút con sẽ làm gốc mới của subtree
                node = node.rotate_left(child)
                # Sau đó, ta xóa nhãn hậu tố của nút gốc mới (vì nút này đã thỏa mãn left associativity)
                node.symbol.val.removesuffix(LEFT_ASSOC)
                continue
            # Nếu child là nonterminal mới được tạo ra từ left factoring
            elif child.symbol.val.endswith(RIGHT_ASSOC):
                # Để đảm bảo được Right Associativity thì ta hợp nhất danh sách childs của nút con vào nút cha
                # Nút gốc mới vẫn là nút cha, nút con bị xóa đi (bởi garbage collector vì ko còn ref đến nó)
                node = node.merge_up(child)
                continue
            # Nếu child là nonterminal bình thường thì tiếp tục đệ quy từ trên xuống
            else:
                # cập nhật child bằng gốc mới của subtree
                node.childs[idx] = enforce_associativity_helper(child)
        # Chỉ khi nào không cần đảm bảo left right associativity nữa thì ta mới đẩy chỉ số sang phải
        idx += 1

    return node
