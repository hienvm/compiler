from pathlib import Path
import os
from argparse import ArgumentParser, FileType
from lexer.lexer import Lexer


def main():
    argparser = ArgumentParser(description="Phân tích từ vựng.")
    argparser.add_argument("input", help="Tên file đầu vào")
    argparser.add_argument('-l', '--lex', default="lex.dat",
                           help="Tên file automaton data cho lexical analyzer (.dat, mặc định lex.dat)")
    args = argparser.parse_args()

    lex_analyze(args.lex, args.input)


def lex_analyze(lex_name, input_name):
    lex_url = lex_name
    input_url = input_name
    # xử lý đường dẫn
    if not os.path.isabs(lex_url):
        lex_url = os.path.abspath(Path(__file__, '..', lex_name))
    if not os.path.isabs(input_url):
        input_url = os.path.abspath(
            Path(__file__, '../..', 'input', input_name)
        )
    with open(
        os.path.abspath(
            Path(__file__, '../..', 'output', input_name + ".vctok")
        ), "w"
    ) as out_file:
        lexer = Lexer(lex_url)
        for output in lexer.analyze(input_url):
            out_file.write(str(output) + '\n')

if __name__ == "__main__":
    main()
