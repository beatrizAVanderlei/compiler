import re


class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.token_type}, {self.value})"


class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.current_line = 0
        self.tokens: list[Token] = []
        self.symbol_table = {}
        self.patterns: list[tuple[str, str]] = [
            (r"\bif\b", "IF"),
            (r"\belse\b", "ELSE"),
            (r"\bwhile\b", "WHILE"),
            (r"\bint\b", "INT"),
            (r"\bbool\b", "BOOL"),
            (r"\btrue\b", "TRUE"),
            (r"\bfalse\b", "FALSE"),
            (r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", "IDENTIFIER"),
            (r"\b[0-9]+\b", "INTEGER"),
            (r"\+", "PLUS"),
            (r"-", "MINUS"),
            (r"\*", "MULTIPLY"),
            (r"/", "DIVIDE"),
            (r"=", "ASSIGN"),
            (r";", "SEMICOLON"),
            (r"\(", "LPAREN"),
            (r"\)", "RPAREN"),
        ]

    def lex(self):
        self.code = self.code.split("\n")

        for line in self.code:
            self.current_line += 1
            line = line.strip()

            while line:
                matched = False
                for pattern, token_type in self.patterns:
                    match = re.match(pattern, line)
                    if match:
                        matched = True
                        value = match.group(0)
                        self.tokens.append(Token(token_type=token_type, value=value))

                        if token_type == "IDENTIFIER":
                            self.symbol_table[value] = {
                                "type": None,
                                "value": None,
                                "line": self.current_line,
                            }

                        line = line[len(value):].strip()
                        break

                if not matched:
                    raise ValueError("Invalid syntax")


with open("code.in", "r") as file:
    code_string = file.read()

lexer = Lexer(code_string)
lexer.lex()

print("Tokens:")
for token in lexer.tokens:
    print(token)

print("\nTabela de Símbolos:")
for identifier, info in lexer.symbol_table.items():
    print(f"Identifier: {identifier} - Type: {info['type']} - Value: {info['value']} - Line: {info['line']}")
