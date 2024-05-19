from parser.types import TerminalSymbol, NonTerminalSymbol
from parser.parser_builder import ParserBuilder
from parser.parser import Parser
from parser.types import Symbol
from pathlib import Path
import os
from argparse import ArgumentParser
from lexer.lexer import Lexer


def main():
    argparser = ArgumentParser(description="Bộ phân tích cú pháp.")

    argparser.add_argument("input_files", nargs="+",
                           help="Tên (nếu đặt trong folder input) hoặc đường dẫn absolute của file đầu vào")
    argparser.add_argument('-t', '--table', action="store_true",
                           help="Build parser trực tiếp từ table.dat.")
    argparser.add_argument('-w', '--whole', action="store_true",
                           help="Đọc toàn bộ file input thay vì từng dòng (đối với file nhỏ)")

    args = argparser.parse_args()

    # khởi tạo lexer từ file lex.dat
    lex_url = os.path.abspath(Path(__file__, '../..', "lexer/lex.dat"))
    lexer = Lexer(lex_url)
    parser = Parser(lexer, from_table=args.table, whole=args.whole)

    for input_name in args.input_files:
        handle(parser, input_name)


def handle(parser: Parser, input_name: str):
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
        (ast, err_log) = parser.parse(input_url)
        out_file.write(ast.to_str(verbose=True))
        print(f'Syntax Parsing Done: {output_url}')
        if err_log == "":
            print("Parsing successful!")
        else:
            print("Errors occured when parsing!")
            out_file.write("\n\nErrors:")
            out_file.write(err_log)
            # err_url = os.path.abspath(
            #     Path(__file__, "../../output", input_name.removesuffix(".vc") + ".err"))
            # with open(err_url, "w", encoding="utf8") as err_file:
            #     err_file.write(err_log)
            #     print("Errors occured when parsing!")
            #     print(f"See more at {err_url}")


if __name__ == "__main__":
    main()
