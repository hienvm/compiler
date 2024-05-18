from pathlib import Path
import os
from argparse import ArgumentParser
from lexer.lexer import Lexer


def main():
    argparser = ArgumentParser(description="Bộ phân tích từ vựng.")

    argparser.add_argument("input_urls", nargs="+",
                           help="Tên (nếu đặt trong folder input) hoặc đường dẫn absolute của file đầu vào")
    argparser.add_argument('-l', '--lex', default="lex.dat",
                           help="Tên file automaton data cho lexical analyzer (.dat, mặc định lex.dat)")
    argparser.add_argument('-w', '--whole', action="store_true",
                           help="Đọc toàn bộ file input thay vì từng dòng (đối với file nhỏ)")

    args = argparser.parse_args()

    # khởi tạo lexer từ file .dat
    if not os.path.isabs(args.lex):
        args.lex = os.path.abspath(Path(__file__, '..', args.lex))
    lexer = Lexer(args.lex)

    for url in args.input_urls:
        lex_analyze(lexer, url, args.whole)


def lex_analyze(lexer: Lexer, input_name: str, whole: bool):
    input_url = input_name

    # xử lý đường dẫn
    if not os.path.isabs(input_url):
        input_url = os.path.abspath(
            Path(__file__, '../..', 'input', input_name)
        )
    output_url = os.path.abspath(
        Path(__file__, '../..', 'output', input_name.removesuffix(".vc") + ".vctok"))

    # mở file output
    with open(
        output_url, "w", encoding="utf8"
    ) as out_file:
        # phân tích từ vựng file input, xuất ra từng kết quả
        for output in lexer.analyze(input_url, not whole):
            out_file.write(str(output) + '\n')
        print(f'Lexical Analysis Done: {output_url}')


if __name__ == "__main__":
    main()
