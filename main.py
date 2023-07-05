from compiler import Compiler


def main(filename):
    with open(filename, "r") as file:
        code_string = file.read()

    compiler = Compiler(code_string)
    compiler.compile()

    print("Tokens:")
    for token in compiler.lexer.tokens:
        print(token)

    print("\nTabela de Símbolos:")
    for identifier, info in compiler.lexer.symbol_table.items():
        print(
            f"Identifier: {identifier} - Type: {info['variable_type']} - Value: {info['variable_value']} - Line: {info['line']}"
        )


if __name__ == "__main__":
    main("code2.in")
