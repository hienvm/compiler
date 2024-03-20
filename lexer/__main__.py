from pathlib import Path
import os
from argparse import ArgumentParser, FileType


def main():
    argparser = ArgumentParser(description="Phân tích từ vựng.")
    argparser.add_argument('-l', '--lex', nargs='?', default="lex.dat",
                           help="Tên file automaton data cho lexical analyzer (.dat, mặc định lex.dat)")
    args = argparser.parse_args()
    print(os.path.abspath(Path(__file__, '../..', 'automaton_data', args.lex)))


if __name__ == "__main__":
    # main()
    with open('lexer/test.in', 'r') as file:
        s = file.read()
