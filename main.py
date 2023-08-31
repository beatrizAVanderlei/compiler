from compiler import Compiler


def main(filename):
    with open(filename, "r") as file:
        code_string = file.read()

    compiler = Compiler(code_string)
    compiler.compile()


if __name__ == "__main__":
    main("code2.in")
