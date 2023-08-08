from typing import Any, Dict
from lexer import Token


class Parser:
    class SyntaxError(Exception):
        pass

    def __init__(self):
        self.index = 0
        self.tokens = None
        self.symbol_table = None
        self.current_token: Token | None = None

    def parse(self, tokens: list[Token], symbol_table: Dict[Token, Dict[str, Any]]):
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.current_token = self.tokens[self.index]
        self.program()

        if self.current_token is not None:
            self.error()

    def error(self):
        raise SyntaxError(
            f"Syntax error at line {self.current_token.line} on token {self.current_token}"
        )

    def consume_token(self):
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def match(self, expected_token):
        if self.current_token:
            if self.current_token.token_type == expected_token:
                self.consume_token()
            else:
                raise SyntaxError(
                    f"Expected {expected_token}, found {self.current_token} at line {self.current_token.line}"
                )
        else:
            raise SyntaxError(
                f"Expected {expected_token}, found EOF at line {self.tokens[-1].line}"
            )

    def program(self):
        self.start_of_program()
        while self.current_token is not None:
            self.start_of_program()

    def start_of_program(self):
        if self.current_token.token_type in ["INT", "BOOL"]:
            self.declaration_or_assignment()
        elif self.current_token.token_type == "PRINT":
            self.print_statement()
        elif self.current_token.token_type == "RETURN":
            self.return_statement()
        elif self.current_token.token_type in ["FUNCTION", "PROCEDURE"]:
            self.function_or_procedure()
        elif self.current_token.token_type == "IF":
            self.if_statement()
        elif self.current_token.token_type == "WHILE":
            self.while_loop()
        elif self.current_token.token_type == "BREAK":
            self.break_statement()
        elif self.current_token.token_type == "CONTINUE":
            self.continue_statement()
        elif self.current_token.token_type == "IDENTIFIER":
            if self.tokens[self.index + 1].token_type == "LPAREN":
                self.function_or_procedure_call()
            elif self.tokens[self.index + 1].token_type == "ASSIGN":
                self.assignment_statement()
            else:
                self.expression_statement()
        else:
            self.error()

    def expression_statement(self):
        self.expression()
        self.match("SEMICOLON")

    def assignment_statement(self):
        variable_token = self.current_token
        self.variable_value()
        self.match("ASSIGN")
        variable_value = self.current_token.value
        current_index = self.index
        self.consume_token()
        while self.current_token.token_type != "SEMICOLON":
            variable_value += self.current_token.value
            self.consume_token()
        self.index = current_index
        self.current_token = self.tokens[self.index]
        self.expression()
        self.match("SEMICOLON")
        self.symbol_table[variable_token].update({"variable_value": variable_value})

    def identifier(self):
        self.match("IDENTIFIER")

    def number(self):
        self.match("INTEGER")

    def boolean(self):
        self.match("TRUE" if self.current_token.token_type == "TRUE" else "FALSE")

    def tipo(self):
        self.match("INT" if self.current_token.token_type == "INT" else "BOOL")

    def variable_value(self):
        if self.current_token.token_type == "IDENTIFIER":
            self.identifier()
        elif self.current_token.token_type == "INTEGER":
            self.number()
        elif self.current_token.token_type in ["TRUE", "FALSE"]:
            self.boolean()
        elif self.current_token.token_type == "LPAREN":
            self.match("LPAREN")
            self.expression()
            self.match("RPAREN")
        else:
            self.error()

    def declaration_or_assignment(self):
        variable_type = self.current_token.token_type
        variable_value = None
        self.tipo()
        variable_token = self.current_token
        self.identifier()

        if self.current_token.token_type == "ASSIGN":
            self.match("ASSIGN")
            variable_value = self.current_token.value
            current_index = self.index
            self.consume_token()
            while self.current_token.token_type != "SEMICOLON":
                variable_value += self.current_token.value
                self.consume_token()
            self.index = current_index
            self.current_token = self.tokens[self.index]
            self.expression()
        self.match("SEMICOLON")

        self.symbol_table[variable_token].update(
            {"variable_type": variable_type, "variable_value": variable_value}
        )

    def print_statement(self):
        self.match("PRINT")
        self.match("LPAREN")
        if self.current_token.token_type != "RPAREN":
            self.argument_list()
        self.match("RPAREN")
        self.match("SEMICOLON")

    def argument_list(self):
        self.expression()
        while self.current_token.token_type == "COLON":
            self.match("COLON")
            self.expression()

    def return_statement(self):
        self.match("RETURN")
        self.expression()
        self.match("SEMICOLON")

    def expression(self):
        self.boolean_expression()

    def function_or_procedure_call_as_argument(self):
        self.identifier()
        self.match("LPAREN")
        if self.current_token.token_type != "RPAREN":
            self.argument_list()
        self.match("RPAREN")

    def parameters(self):
        variable_type = self.current_token.token_type
        self.tipo()
        variable_token = self.current_token
        self.identifier()
        self.symbol_table[variable_token].update({"variable_type": variable_type})
        while self.current_token.token_type == "COLON":
            self.match("COLON")
            variable_type = self.current_token.token_type
            self.tipo()
            variable_token = self.current_token
            self.identifier()
            self.symbol_table[variable_token].update({"variable_type": variable_type})

    def function_or_procedure(self):
        if self.current_token.token_type == "FUNCTION":
            self.match("FUNCTION")
            variable_token = self.current_token
            self.identifier()
            self.match("LPAREN")
            if self.current_token.token_type != "RPAREN":
                self.parameters()
            self.match("RPAREN")
            self.match("ARROW")
            variable_type = self.current_token.token_type
            self.tipo()
            self.match("LBRACE")
            self.function_or_procedure_scope()
            self.return_statement()
            self.match("RBRACE")
            self.symbol_table[variable_token].update({"variable_type": variable_type})
        elif self.current_token.token_type == "PROCEDURE":
            self.match("PROCEDURE")
            self.identifier()
            self.match("LPAREN")
            if self.current_token.token_type != "RPAREN":
                self.parameters()
            self.match("RPAREN")
            self.match("LBRACE")
            self.function_or_procedure_scope()
            self.match("RBRACE")
        else:
            self.declaration_or_assignment()

    def function_or_procedure_call(self):
        self.identifier()
        self.match("LPAREN")
        if self.current_token.token_type != "RPAREN":
            self.argument_list()
        self.match("RPAREN")
        self.match("SEMICOLON")

    def if_statement(self):
        self.match("IF")
        self.match("LPAREN")
        self.boolean_expression()
        self.match("RPAREN")
        self.match("LBRACE")
        self.conditional_scope()
        self.match("RBRACE")

        if self.current_token is not None and self.current_token.token_type == "ELSE":
            self.match("ELSE")
            self.match("LBRACE")
            self.conditional_scope()
            self.match("RBRACE")

    def while_loop(self):
        self.match("WHILE")
        self.match("LPAREN")
        self.boolean_expression()
        self.match("RPAREN")
        self.match("LBRACE")
        self.loop_scope()
        self.match("RBRACE")

    def break_statement(self):
        self.match("BREAK")
        self.match("SEMICOLON")

    def continue_statement(self):
        self.match("CONTINUE")
        self.match("SEMICOLON")

    def boolean_expression(self):
        self.arithmetic_expression()
        while self.current_token.token_type in [
            "EQUAL",
            "DIFFERENT",
            "GREATER",
            "GREATER_OR_EQUAL",
            "LESS",
            "LESS_OR_EQUAL",
            "AND",
            "OR",
        ]:
            self.match(self.current_token.token_type)
            self.arithmetic_expression()

    def arithmetic_expression(self):
        self.factor()
        while self.current_token.token_type in [
            "PLUS",
            "MINUS",
            "MULTIPLY",
            "DIVIDE",
            "MODULE",
        ]:
            self.match(self.current_token.token_type)
            self.factor()

    def factor(self):
        if self.current_token.token_type == "LPAREN":
            self.match("LPAREN")
            self.expression()
            self.match("RPAREN")
        elif self.current_token.token_type == "IDENTIFIER":
            if self.tokens[self.index + 1].token_type == "LPAREN":
                self.function_or_procedure_call_as_argument()
            else:
                self.identifier()
        elif self.current_token.token_type == "INTEGER":
            self.number()
        elif self.current_token.token_type in ["TRUE", "FALSE"]:
            self.boolean()
        else:
            self.error()

    def function_or_procedure_scope(self):
        while self.current_token.token_type not in ["RBRACE", "RETURN"]:
            self.start_of_program()

    def conditional_scope(self):
        while (
            self.current_token.token_type != "RBRACE"
            and self.current_token.token_type != "ELSE"
        ):
            self.start_of_program()

    def loop_scope(self):
        while self.current_token.token_type != "RBRACE":
            self.start_of_program()
