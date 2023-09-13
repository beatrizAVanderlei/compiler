from compiler import Compiler


def main(filename):
    # TODO: arrumar continue e break - OK
    # TODO: tradução para código de 3 endereços
    with open(filename, "r") as file:
        code_string = file.read()

    compiler = Compiler(code_string)
    compiler.compile()


if __name__ == "__main__":
    main("code2.in")
