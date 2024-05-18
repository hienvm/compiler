from enum import Enum
from pathlib import Path
import os.path
import json

from parser.types import EOF, EPSILON, Epsilon, Production, Symbol, NonTerminalSymbol, TerminalSymbol, json_default, str_to_symbol


class ReadMode(Enum):
    SKIP = -1
    START = 0
    PRODUCTIONS = 1


GRAMMAR_URL = os.path.abspath(
    Path(__file__, "..", "grammar.dat")
)
TABLE_URL = os.path.abspath(
    Path(__file__, "..", "table.dat"))


class ParserBuilder:
    def __init__(self, from_grammar: bool = False) -> None:
        '''Xây dựng lexer dfa từ file .dat'''
        self.start = ""
        # Ánh xạ từ [non_terminal ở trên cùng stack, terminal từ input] -> sản xuất được chọn
        # VD: production = self.table[non_terminal][terminal]
        self.table: dict[
            NonTerminalSymbol, dict[TerminalSymbol, Production]
        ] | dict = {}

        with open(GRAMMAR_URL, "r", encoding="utf8") as file:
            # ánh xạ từ vế trái (gồm 1 ký tự nonterminal) tới vế phải (dãy các symbol liền nhau) của các sản suất
            productions: list[Production] = []
            # tập các non_terminal
            non_terminals: set[NonTerminalSymbol] = set()
            # cache lưu lại kết quả của các lần tính first
            first_cache: dict[tuple[Symbol, ...],
                              set[TerminalSymbol | Epsilon]] = {}
            # cache lưu lại kết quả của các lần tính follow
            follow_cache: dict[NonTerminalSymbol,
                               set[TerminalSymbol]] = {}
            # tập hợp những nonterminal đã tính xong follow
            follow_done = set()
            # mode đọc để đổi hàm đọc giữa các section
            read_mode: ReadMode = ReadMode.SKIP

            # Đọc từng dòng
            for ln in file:
                # Xử lý comment
                if ln[0] == "#":
                    continue

                # Tách các tham số theo khoảng trắng
                args = ln.split()
                if len(args) == 0:
                    continue

                match args[0]:
                    case "START":
                        read_mode = ReadMode.START
                    case "PRODUCTIONS":
                        read_mode = ReadMode.PRODUCTIONS
                    case _:
                        # với section nào tihf
                        match read_mode:
                            case ReadMode.START:
                                # Đọc ký tự nonterminal bắt đầu
                                self.start = args[0]
                            case ReadMode.PRODUCTIONS:
                                # Đọc sản suất
                                readln_productions(
                                    args, productions, non_terminals)

            # khai báo first, follow, select là inner function để capture các giá trị cần thiết
            def first(syms: tuple[Symbol, ...]) -> set[TerminalSymbol | Epsilon]:
                '''Trả về tập first của một chuỗi các ký tự'''
                # lấy ra kết quả từ cache
                fetch = first_cache.get(syms, None)
                # sử dụng lại kết quả nếu được
                if fetch is not None:
                    return set(fetch)

                # Kết quả trả về
                res = set()
                if len(syms) == 1:  # Nếu syms chỉ có 1 ký tự
                    sym = syms[0]
                    # nếu syms[0] là nonterminal
                    if isinstance(sym, NonTerminalSymbol):
                        for p in productions:
                            # Tìm luật có vế trái là sym
                            if sym == p.lsym:
                                # Thêm first của các symbol vế phải
                                res.update(first(p.rsyms))
                    # nếu sym là terminal hoặc Epsilon
                    elif isinstance(sym, TerminalSymbol | Epsilon):
                        res.add(sym)
                else:
                    nullable = True
                    for sym in syms:
                        # duyệt từ trái sang, tìm x là tập first của ký tự hiện tại
                        x = first((sym,))
                        # cập nhật kết quả
                        res.update(x)
                        # Nếu x ko chứa epsilon thì dừng và tắt flag nullable
                        if EPSILON not in res:
                            nullable = False
                            break
                    # nếu ko nullable thì loại epsilon ra
                    if not nullable:
                        res.discard(EPSILON)
                first_cache[syms] = set(res)
                return res

            def follow(sym: NonTerminalSymbol) -> set[TerminalSymbol]:
                # print(sym)
                # nếu tính xong rồi thì dùng kết quả từ cache
                if sym in follow_done:
                    return set(follow_cache[sym])

                # kết quả
                res = set()

                for p in productions:
                    # tìm các productions có chứa sym ở vế phải
                    # xét p.lsym -> alpha sym beta
                    if sym in p.rsyms:
                        # tìm chỉ số của sym
                        idx = p.rsyms.index(sym)
                        # tìm beta là phần phía sau sym của vế phải production
                        beta = p.rsyms[idx + 1:]
                        # tính first(beta)
                        f_beta = first(beta) if len(beta) > 0 else {EPSILON}
                        if EPSILON in f_beta:
                            # nếu beta nullable thì thêm follow của vế trái vào kết quả
                            res.update(follow_cache.get(
                                p.lsym, set())
                            )
                            # loại epsilon ra khỏi f_beta
                            f_beta.discard(EPSILON)
                        # thêm follow của beta vào kết quả
                        res.update(f_beta)

                return res

            def select(p: Production) -> set[TerminalSymbol]:
                ''''''
                # chỉ tính 1 lần nên ko cần cache
                # xét luật p: p.lsym -> p.rsyms
                # Kết quả trả về
                res = set()
                # thêm first(vế phải) vào select
                res.update(first(p.rsyms))
                if EPSILON in res:
                    # Nếu select là nullable thì bỏ epsilon ra và thêm follow của vế trái vào
                    res.discard(EPSILON)
                    res.update(follow(p.lsym))
                return res

            # thêm EOF vào follow của ký tự bắt đầu
            follow_cache[NonTerminalSymbol(self.start)] = {EOF}

            # tính lại follow cho tất cả các terminal cho tới khi không còn thay đổi gì
            while len(follow_done) < len(non_terminals):
                for sym in non_terminals:
                    # với mỗi nonterminal, tính mới tập follow
                    f = follow(sym)
                    # lấy ra tập follow cũ từ cache
                    prev = follow_cache.get(sym, None)
                    # so sánh 2 tập
                    if prev is None or len(prev.symmetric_difference(f)) > 0:
                        # nếu như follow có thay đổi, cập nhật cache
                        follow_cache[sym] = f
                    else:
                        # nếu ko thay đổi thì đánh dấu là xong
                        follow_done.add(sym)

            # bắt đầu xây dựng table từ grammar và select
            self.table = {non_t: {} for non_t in non_terminals}
            ambiguities_cnt = 0
            for p in productions:
                # với mỗi luật, tính select
                sel = select(p)
                # với mỗi ký tự trong select
                for sym in sel:
                    # Nếu ô đã chứa production thì giữ production cũ, bỏ production mới
                    # Như vậy, production được khai báo trước sẽ có độ ưu tiên cao hơn
                    # -> Xử lý được các trường hợp như Dangling Else
                    # https://hypertextbookshop.com/transPL/Contents/01_Topics/03_Parsing/05_Section_5/02_page_2_-_LL(1)_Table_Conflicts.html
                    if self.table[p.lsym].get(sym) is not None:
                        print("Ambiguity resolved!")
                        print(f"  Row: {p.lsym}")
                        print(f"  Col: {sym}")
                        print(f"  Keep: {self.table[p.lsym].get(sym)}")
                        print(f"  Discard: {p}")
                        ambiguities_cnt += 1
                    else:
                        # nếu ô còn trống thì gán production
                        self.table[p.lsym][sym] = p
            print(f"Total ambiguities resolved: {ambiguities_cnt}")

            with open(TABLE_URL, "w", encoding="utf8") as table_file:
                tmp_table = {
                    str(row): {
                        str(col): str(self.table[row][col]) for col in self.table[row]
                    } for row in self.table
                }
                tmp_table, self.table = self.table, tmp_table
                json.dump(self, table_file, indent=4,
                          default=json_default)
                tmp_table, self.table = self.table, tmp_table
                print("Building table done!")


def readln_productions(args: list[str], productions: list[Production], non_terminals: set[NonTerminalSymbol]):
    # non-terminal vế trái
    lsym = NonTerminalSymbol(args[0])
    # mọi non_terminal đều nằm vế trái của 1 production nào đó
    non_terminals.add(lsym)
    # thêm từ arg thứ 2 trở đi (sau lsym và "->") vào danh sách vế phải sản suất
    rsyms = tuple(map(str_to_symbol, args[2:]))
    # thêm vào danh sách sản xuất
    productions.append(Production(lsym, rsyms))
