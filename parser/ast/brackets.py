from typing import Literal
from parser.ast.node import Leaf
from parser.ast.node import InnerNode, Node
from parser.types import EPSILON, Epsilon

'''Định dạng output normal brackets'''


def to_str_brackets_dfs(node: Node) -> list[str]:
    '''hàm helper đệ quy để convert ast sang format mặc định (mở ngoặc đóng ngoặc)'''
    ls = []
    # Nếu là nút trong (non-terminal)
    if isinstance(node, InnerNode):
        # mở ngoặc
        ls += ['(']
        for child in node.childs:
            ls += to_str_brackets_dfs(child)
        ls += [')']
    # nếu là nút lá (epslion hoặc terminal)
    elif isinstance(node, Leaf):
        if isinstance(node.symbol, Epsilon):
            # epsilon
            ls += ['(', EPSILON.val, ')']
        else:
            # terminal
            ls += [node.value.lexeme]
    return ls


def reduce_brackets(ls: list[str], reduce_level: Literal[1, 2]) -> list[str]:
    '''Dùng stack để khử khác dấu ngoặc thừa.\n
    Level 1: Giữ lại các cặp chỉ có duy nhất leaf_value\n
    Level 2: Loại các cặp chỉ có duy nhất leaf_value'''
    # 2 dấu ngoặc là thừa nếu giữa chúng:
    # + hoặc không có ký tự nào
    # + hoặc chỉ có MỘT cặp dấu ngoặc con trực tiếp KHÔNG THỪA (có thể có nhiều cặp thừa)
    # + hoặc nếu chỉ có một kí tự (với reduce level 2)

    try:  # Giả định xâu là hợp lệ
        # stack chứa các ký tự đầu vào
        input_stack: list[str] = []
        # stack chứa trạng thái cho các dấu ngoặc mở theo bộ (idx, số cặp ngoặc con)
        op_stack: list[list] = []
        # mảng bool để check xem giữ hay khử các dấu ngoặc
        keep: list[bool] = [True] * len(ls)

        for i, s in enumerate(ls):
            if s == ')':
                # đếm số lượng leaf_value chưa được pop ra
                # (tức đếm số con trực tiếp là leaf_value)
                leftover = 0
                # pop tới khi gặp dấu mở ngoặc tương ứng
                while input_stack[-1] != '(':
                    leftover += 1
                    input_stack.pop()
                input_stack.pop()
                # Lấy ra trạng thái của dấu mở ngoặc tương ứng
                # op[0]: chỉ số trong xâu
                # op[1]: số cặp ngoặc con TRỰC TIẾP giữa ngoặc mở và s
                op = op_stack.pop()

                # Nếu (không còn sót lại leaf_value hoặc vẫn còn MỘT nhưng reduce_level là 2)
                # và giữa 2 dấu ngoặc có TỐI ĐA 1 cặp ngoặc con
                if (leftover == 0 or leftover <= 1 and reduce_level == 2) and op[1] <= 1:
                    # mark 2 dấu ngoặc là thừa
                    keep[op[0]] = keep[i] = False
                # cộng 1 con cho dấu mở ngoặc gần nhất (tức dấu mở ngoặc cha) nếu có
                if len(input_stack):
                    op_stack[-1][1] += 1
            else:
                # nếu là '(' hoặc leaf_value thì thêm vào stack
                input_stack.append(s)
                if s == '(':
                    # thêm trạng thái của các dấu mở ngoặc vào op_stack
                    op_stack.append([i, 0])

        # Chỉ dữ lại những phần không thừa
        return [s for i, s in enumerate(ls) if keep[i]]

    except Exception:
        # xử lý ngoại lệ
        print("Invalid bracket string.")
        return ["invalid"]


def __old_reduce_brackets(ls: list[str], reduce_level: Literal[1, 2]) -> list[str]:
    '''Deprecated\n
    Bằng một cách nào đó hàm này sinh ra được kết quả đẹp mà thậm chí không cần phải post process\n
    Dùng stack để khử khác dấu ngoặc thừa.\n
    Level 1: Giữ lại các cặp chỉ có một leaf_value\n
    Level 2: Loại các cặp chỉ có một leaf_value'''
    try:  # Giả định xâu là hợp lệ
        # stack chứa các bộ(chỉ số, kí tự, biến đếm số cặp dấu ngoặc con được lưu ở dấu ngoặc mở)
        stack: list[list] = []
        # mảng bool để check xem giữ hay khử các dấu ngoặc
        keep: list[bool] = [True] * len(ls)

        # 2 dấu ngoặc là thừa nếu giữa chúng:
        # + hoặc không có ký tự nào
        # + hoặc chỉ có MỘT cặp dấu ngoặc con trực tiếp KHÔNG THỪA (có thể có nhiều cặp thừa)
        # + hoặc nếu chỉ có một kí tự (với reduce level 2)

        for i, s in enumerate(ls):
            if s == ')':
                # đếm số lượng leaf_value chưa được pop ra
                # (tức đếm số con trực tiếp là leaf_value)
                leftover = 0
                # pop tới khi gặp dấu mở ngoặc tương ứng
                while stack[-1][1] != '(':
                    leftover += 1
                    stack.pop()
                # Khi đã thực hiện xong lần pop gần nhất thì trong stack chỉ còn chứa các dấu '(' (nếu valid)
                # Lấy ra dấu mở ngoặc tương ứng
                op_bracket = stack.pop()

                # Nếu (không còn sót lại leaf_value hoặc vẫn còn MỘT nhưng reduce_level là 2)
                # và giữa 2 dấu ngoặc có TỐI ĐA 1 cặp ngoặc con
                if (leftover == 0 or leftover <= 1 and reduce_level == 2) and op_bracket[2] <= 1:
                    # đánh dấu 2 dấu ngoặc là thừa
                    keep[op_bracket[0]] = keep[i] = False
                # cộng 1 con cho dấu mở ngoặc gần nhất (tức dấu mở ngoặc cha) nếu có
                if len(stack):
                    stack[-1][2] += 1
            else:
                # nếu là '(' hoặc leaf_value thì thêm vào stack và khởi tạo biến đếm con cho các dấu '('
                stack.append([i, s, 0])
        # Chỉ dữ lại những phần không thừa
        return [s for i, s in enumerate(ls) if keep[i]]
    except Exception:
        # xử lý ngoại lệ
        print("Invalid bracket string.")
        return ["invalid"]
