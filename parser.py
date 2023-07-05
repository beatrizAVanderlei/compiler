from typing import Any

from lexer import Token


class Parser:
    class SyntaxError(Exception):
        pass

    def __init__(self):
        self.index = 0
        self.tokens = None
        self.symbol_table = None
        self.current_token: Token | None = None

    def parse(self, tokens: list[Token], symbol_table: dict[Token, dict[str, Any]]):
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.current_token = self.tokens[self.index]
        self.origin()

        if self.current_token is not None:
            self.error()

    def error(self):
        raise SyntaxError(
            f"Syntax error at line {self.symbol_table[self.current_token]['line']} on token {self.current_token}"
        )

    def consume_token(self):
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def match(self, expected_token):
        if self.current_token.token_type == expected_token:
            self.consume_token()
        else:
            raise SyntaxError(f"Expected {expected_token}, found {self.current_token}")

    def origin(self):
        while self.current_token is not None:
            self.declare_variable()

    def declare_variable(self):
        if self.current_token.token_type == "INT":
            self.match("INT")
            identifier_token = self.current_token
            self.match("IDENTIFIER")
            self.match("ASSIGN")
            value_of_identifier_token = self.current_token
            self.match("INTEGER")
            self.match("SEMICOLON")
            self.symbol_table[identifier_token]["variable_type"] = "INT"
            self.symbol_table[identifier_token][
                "variable_value"
            ] = value_of_identifier_token.value
        elif self.current_token.token_type == "BOOL":
            self.match("BOOL")
            self.match("IDENTIFIER")
            self.match("SEMICOLON")
        else:
            self.error()
