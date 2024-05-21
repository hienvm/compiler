from parser.parser import Parser
from pathlib import Path
import os
from argparse import ArgumentParser
from lexer.lexer import Lexer


def main():
    argparser = ArgumentParser(
        prog="python -m parser",
        description="Bộ phân tích cú pháp.",
    )

    # vc files
    argparser.add_argument("input_files", nargs="+",
                           help="Tên (nếu đặt trong folder input) hoặc đường dẫn absolute của file đầu vào")

    # parser build mode
    argparser.add_argument('-t', '--table', action="store_true",
                           help="Build parser trực tiếp từ table.dat.")

    # JSON
    argparser.add_argument('-v', '--verbose', action="store_true",
                           help="In ra cây AST theo định dạng JSON.")
    argparser.add_argument('-i', '--indent', type=int, default=2,
                           help="JSON indent cho verbose. Mặc định 2.")

    # normal brackets
    argparser.add_argument('-r', '--reduce_level', type=int, choices=[0, 1, 2], default=2,
                           help="Cấp độ loại bỏ các cặp dấu ngoặc thừa.\n0 - Không bỏ;\n1 - Giữ lại các cặp chỉ chứa duy nhất leaf_value;\n2 - Loại các cặp chỉ chứa duy nhất leaf_value.\nMặc định 2.")

    # Post-parse Processing Options
    # lexer file-reading mode
    argparser.add_argument('-e', '--epsilon', action="store_true",
                           help="Giữ lại epsilon.")

    # lexer file-reading mode
    argparser.add_argument('-w', '--whole', action="store_true",
                           help="Đọc toàn bộ file input thay vì từng dòng (đối với file nhỏ)")

    args = argparser.parse_args()

    # khởi tạo lexer từ file lex.dat
    lex_url = os.path.abspath(Path(__file__, '../..', "lexer/lex.dat"))
    lexer = Lexer(lex_url)
    parser = Parser(lexer, from_table=args.table, whole=args.whole)

    for input_name in args.input_files:
        input_url = input_name

        # xử lý đường dẫn
        if not os.path.isabs(input_url):
            input_url = os.path.abspath(
                Path(__file__, '../..', 'input', input_name)
            )
        output_url = os.path.abspath(
            Path(__file__, '../..', 'output', input_name.removesuffix(".vc") + ".vcps"))

        # mở file output
        with open(
            output_url, "w", encoding="utf8"
        ) as out_file:
            # Lấy kết quả từ LL(1) parser
            (ast, err_log) = parser.parse(input_url)
            print('LL(1) Parsing Done!')

            # Hậu xử lý (Post-parse Processing)
            if args.epsilon is False:
                # xoá epsilon
                ast.clear_epsilon()
                print("Null paths cleared!")

            # Đảm bảo left-right associativity
            ast.enforce_associativity()
            print("Associativity enforced!")

            # In kết quả
            out_file.write(
                ast.to_str(
                    verbose=args.verbose,
                    indent=args.indent,
                    reduce_level=args.reduce_level,
                )
            )

            # xử lý lỗi
            if err_log == "":
                print("Parsing successful!")
            else:
                print("Errors occured when parsing!")
                out_file.write("\n\nErrors:")
                out_file.write(err_log)
            print(f"\t-> See results at: {output_url}")


if __name__ == "__main__":
    main()
