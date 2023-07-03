from lexer import Lexer


def main(filename):
    with open(filename, "r") as file:
        code_string = file.read()

    lexer = Lexer(code_string)
    lexer.lex()

    print("Tokens:")
    for token in lexer.tokens:
        print(token)

    print("\nTabela de Símbolos:")
    for identifier, info in lexer.symbol_table.items():
        print(
            f"Identifier: {identifier} - Type: {info['variable_type']} - Value: {info['variable_value']} - Line: {info['line']}"
        )


if __name__ == "__main__":
    main("code.in")
