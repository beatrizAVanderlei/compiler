from lexer import Lexer


def main():
    with open("code.in", "r") as file:
        code_string = file.read()

    lexer = Lexer(code_string)
    lexer.lex()

    print("Tokens:")
    for token in lexer.tokens:
        print(token)

    print("\nTabela de Símbolos:")
    for identifier, info in lexer.symbol_table.items():
        print(
            f"Identifier: {identifier} - Type: {info['type']} - Value: {info['value']} - Line: {info['line']}"
        )


if __name__ == "__main__":
    main()
