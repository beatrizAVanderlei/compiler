from pprint import pprint

from compiler import Compiler


def main(filename):
    with open(filename, "r") as file:
        code_string = file.read()

    compiler = Compiler(code_string)
    compiler.compile()

    print("\nTabela de Símbolos:")
    pprint(compiler.parser.symbol_table)


if __name__ == "__main__":
    main("code2.in")
