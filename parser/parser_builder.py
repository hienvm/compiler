from enum import Enum
from pathlib import Path
import os.path
import json

from parser.types import EOF, EPSILON, Epsilon, Production, Symbol, NonTerminalSymbol, TerminalSymbol, json_default, raw2production, raw2table


class ReadMode(Enum):
    SKIP = -1
    START = 0
    PRODUCTIONS = 1


GRAMMAR_URL = os.path.abspath(
    Path(__file__, "..", "grammar.dat"))
TABLE_URL = os.path.abspath(
    Path(__file__, "..", "table.dat"))


class ParserBuilder:
    def __init__(self, from_table: bool = False) -> None:
        '''
        Xây dựng lexer dfa từ file .dat.\n
        Nếu build từ table thì load trực tiếp kết quả từ table.dat.\n
        Nếu không thì build từ grammar như sau:
        - Nhận đầu vào là các productions và một số thông tin khác từ grammar.dat
        - Build first, follow theo https://www.inf.ed.ac.uk/teaching/courses/inf2a/slides2017/inf2a_L12_slides.pdf.
        - Build LL(1) table từ select.
        - Chọn luật theo thứ tự ưu tiên để xử lý Dangling Else https://hypertextbookshop.com/transPL/Contents/01_Topics/03_Parsing/05_Section_5/02_page_2_-_LL(1)_Table_Conflicts.html
        - Cập nhật lại table.dat.\n
        '''
        # Ký tự bắt đầu
        self.start = NonTerminalSymbol("")

        # Ánh xạ từ [non_terminal ở trên cùng stack, terminal từ input] -> sản xuất được chọn
        # VD: production = self.table[non_terminal][terminal]
        self.table: dict[
            NonTerminalSymbol, dict[TerminalSymbol, Production]
        ] | dict = {}

        # build trực tiếp từ table.dat
        if from_table and os.path.isfile(TABLE_URL):
            with open(TABLE_URL, "r", encoding="utf8") as file:
                print(f"Builing table from: {TABLE_URL}")
                raw = json.load(file)
                self.start = NonTerminalSymbol(raw["start"])
                self.table = raw2table(raw["table"])
            return
            
        with open(GRAMMAR_URL, "r", encoding="utf8") as file:
            print(f"Builing table from: {GRAMMAR_URL}")
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
            # chứa các nullable non-terminal và epsilon
            nullables: set[NonTerminalSymbol] = set()
            # đã tính xong hết first hay chưa
            first_done = False
            # đã tính xong hết follow hay chưa
            follow_done = False
            # biến bool kiểm tra stabilized cho nullables, first, follow
            stable = False
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
                                self.start = NonTerminalSymbol(args[0])
                            case ReadMode.PRODUCTIONS:
                                # Đọc sản suất
                                p = raw2production(ln)
                                # mọi non_terminal đều nằm vế trái của 1 production nào đó
                                non_terminals.add(p.lsym)
                                # thêm p vào productions
                                productions.append(p)

            # khai báo first, follow, select là inner function để capture các giá trị cần thiết
            def first(syms: tuple[Symbol, ...]) -> set[TerminalSymbol | Epsilon]:
                '''Trả về tập first của một chuỗi các ký tự'''
                # lấy ra kết quả từ cache
                prev = first_cache.get(syms, None)
                # sử dụng lại kết quả nếu được
                if prev is not None and first_done:
                    return set(prev)

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
                # nếu tính xong rồi thì dùng kết quả từ cache
                if follow_done:
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
            follow_cache[self.start] = {EOF}

            # tìm các nullable terminal
            # https://www.inf.ed.ac.uk/teaching/courses/inf2a/slides2017/inf2a_L12_slides.pdf
            stable = True
            for p in productions:
                if p.empty():
                    nullables.add(p.lsym)
                    stable = False
            while stable is False:
                stable = True
                for p in productions:
                    # check xem có phải tất cả vế phải đều nullable
                    all_null = True
                    for rsym in p.rsyms:
                        if rsym not in nullables:
                            all_null = False
                            break
                    if all_null and p.lsym not in nullables:
                        # nếu vế phải nullable hết và vế trái chưa được đánh dấu là nullable
                        nullables.add(p.lsym)
                        stable = False

            # Tính trước first cho các non-terminal
            stable = False
            while not stable:
                stable = True
                for p in productions:
                    # first trước đó
                    prev = first_cache.get((p.lsym,), None)
                    # first vế phải
                    rfirst = set()
                    for rsym in p.rsyms:
                        if isinstance(rsym, NonTerminalSymbol):
                            rfirst.update(first_cache.get((rsym,), set()))
                            if rsym not in nullables:
                                rfirst.discard(EPSILON)
                                break
                        else:
                            rfirst.add(rsym)
                            if isinstance(rsym, TerminalSymbol):
                                rfirst.discard(EPSILON)
                                break
                    # nếu first vế trái chưa được tính
                    if prev is None:
                        first_cache[(p.lsym,)] = rfirst
                        stable = False
                    # nếu first vế phải chưa nằm trong first vế trái
                    elif not rfirst.issubset(prev):
                        # cập nhật và đánh dấu là chưa stable
                        prev.update(rfirst)
                        stable = False
            first_done = True

            # tính follow cho tất cả các terminal cho tới khi không còn thay đổi gì
            # https://www.inf.ed.ac.uk/teaching/courses/inf2a/slides2017/inf2a_L12_slides.pdf
            stable = False
            while not stable:
                stable = True
                for sym in non_terminals:
                    # với mỗi nonterminal, tính mới tập follow
                    f = follow(sym)
                    # lấy ra tập follow cũ từ cache
                    prev = follow_cache.get(sym, None)
                    # so sánh 2 tập
                    # nếu như follow có thay đổi
                    if prev is None or len(prev.symmetric_difference(f)) > 0:
                        # cập nhật cache và đánh dấu chưa stable
                        follow_cache[sym] = f
                        stable = False
            follow_done = True

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

            # Lưu lại table và các thông tin cơ bản của grammar
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
                print(f"Building table done: {TABLE_URL}")