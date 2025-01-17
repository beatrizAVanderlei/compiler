from typing import Any, Dict
from lexer import Token


Type = str  # Type alias for better readability, can be either "INT" or "BOOL"


class SemanticError(Exception):
    pass


class Parser:
    """
    Syntactic and semantic analysis of the program. And also create three address code.
    """

    def __init__(self):
        self.index = 0
        self.tokens = None
        self.symbol_table = None
        self.current_token = None
        self.current_scope = -1
        self.scopes = []
        self.instructions = []

    def parse(self, tokens: list[Token], symbol_table: Dict[Token, Dict[str, Any]]):
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.current_token = self.tokens[self.index]
        self.program()

        if self.current_token is not None:
            self.error()

    def program(self):
        self.current_scope = 0
        self.scopes.insert(self.current_scope, {})

        self.start_of_program()
        while self.current_token is not None:
            self.start_of_program()

        self.scopes.pop(self.current_scope)

    def start_of_program(self):
        if self.current_token.token_type in ["INT", "BOOL"]:
            self.declaration_and_assignment()
        elif self.current_token.token_type == "PRINT":
            self.print_statement()
        elif self.current_token.token_type in ["FUNCTION", "PROCEDURE"]:
            self.function_or_procedure()
        elif self.current_token.token_type == "IF":
            self.if_statement()
        elif self.current_token.token_type == "WHILE":
            self.while_loop()
        elif self.current_token.token_type == "IDENTIFIER":
            if self.tokens[self.index + 1].token_type == "LPAREN":
                self.function_or_procedure_call()
                self.match("SEMICOLON")
            elif self.tokens[self.index + 1].token_type == "ASSIGN":
                self.assignment_statement()
            else:
                self.expression()
                self.match("SEMICOLON")
        else:
            self.error()

    def start_of_while(self):
        if self.current_token.token_type in ["INT", "BOOL"]:
            self.declaration_and_assignment()
        elif self.current_token.token_type == "PRINT":
            self.print_statement()
        elif self.current_token.token_type in ["FUNCTION", "PROCEDURE"]:
            self.function_or_procedure()
        elif self.current_token.token_type == "IF":
            self.if_statement_while()
        elif self.current_token.token_type == "WHILE":
            self.while_loop()
        elif self.current_token.token_type == "BREAK":
            self.break_statement()
        elif self.current_token.token_type == "CONTINUE":
            self.continue_statement()
        elif self.current_token.token_type == "IDENTIFIER":
            if self.tokens[self.index + 1].token_type == "LPAREN":
                self.function_or_procedure_call()
                self.match("SEMICOLON")
            elif self.tokens[self.index + 1].token_type == "ASSIGN":
                self.assignment_statement()
            else:
                self.expression()
                self.match("SEMICOLON")
        else:
            self.error()

    def declaration_and_assignment(self):
        variable_type = self.current_token.token_type
        self.tipo()
        variable_token = self.current_token
        self.instructions.append(self.current_token)
        self.identifier()

        # check if the variable has already been declared in the current scope or in the parent scopes
        for scope in self.scopes:
            for token in scope.keys():
                if token.value == variable_token.value:
                    raise SemanticError(
                        f"Variable '{variable_token.value}' in line {variable_token.line} "
                        f"already declared in line {token.line}"
                    )

        if self.current_token.token_type == "ASSIGN":
            self.instructions.append(self.current_token)
            self.match("ASSIGN")
            expression_type = self.expression()
            self.check_types(variable_type, expression_type)

        if self.current_token.token_type == "SEMICOLON":
            self.match("SEMICOLON")

        self.scopes[self.current_scope][variable_token] = {
            "variable_type": variable_type,
            "scope": self.current_scope,
        }

    def assignment_statement(self):
        variable_token = self.current_token
        self.instructions.append(self.current_token)
        self.identifier()
        variable_type = self.get_variable_type(variable_token)
        self.instructions.append(self.current_token)
        self.match("ASSIGN")
        expression_type = self.expression()
        self.check_types(variable_type, expression_type)
        self.match("SEMICOLON")

    def expression(self) -> Type:
        return self.boolean_expression()

    def boolean_expression(self) -> Type:
        expression_type = self.arithmetic_expression()
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
            operator = self.current_token.token_type
            self.instructions.append(self.current_token)
            self.match(operator)

            right_operand_type = self.arithmetic_expression()

            if expression_type != right_operand_type:
                raise SemanticError(
                    f"Type mismatch: Cannot perform {operator} operation between {expression_type} and "
                    f"{right_operand_type} at line {self.current_token.line}"
                )

            if operator in ["AND", "OR"]:
                if expression_type != "BOOL":
                    raise SemanticError(
                        f"Invalid operation: {operator} operation not supported on "
                        f"type {expression_type} at line {self.current_token.line}"
                    )

                if right_operand_type != "BOOL":
                    raise SemanticError(
                        f"Invalid operation: {operator} operation not supported "
                        f"on type {right_operand_type} at line {self.current_token.line}"
                    )

            expression_type = "BOOL"

        return expression_type

    def arithmetic_expression(self) -> Type:
        expression_type = self.factor()
        while self.current_token.token_type in [
            "PLUS",
            "MINUS",
            "MULTIPLY",
            "DIVIDE",
            "MODULE",
        ]:
            operator = self.current_token.token_type
            self.instructions.append(self.current_token)
            self.match(operator)
            right_operand_type = self.factor()

            if expression_type != right_operand_type:
                raise SemanticError(
                    f"Type mismatch: Cannot perform {operator} operation between {expression_type} and "
                    f"{right_operand_type} at line {self.current_token.line}"
                )

            expression_type = "INT"

        return expression_type

    def factor(self) -> Type:
        expression_type = None

        if self.current_token.token_type == "LPAREN":
            self.instructions.append(self.current_token)
            self.match("LPAREN")
            expression_type = self.expression()
            self.instructions.append(self.current_token)
            self.match("RPAREN")
        elif self.current_token.token_type == "IDENTIFIER":
            if self.tokens[self.index + 1].token_type == "LPAREN":
                expression_type = self.function_or_procedure_call()

            else:
                variable_token = self.current_token
                self.instructions.append(self.current_token)
                self.identifier()
                expression_type = self.get_variable_type(variable_token)

        elif self.current_token.token_type == "INTEGER":
            self.instructions.append(self.current_token)
            self.number()
            expression_type = "INT"
        elif self.current_token.token_type in ["TRUE", "FALSE"]:
            self.instructions.append(self.current_token)
            self.boolean()
            expression_type = "BOOL"
        elif self.current_token.token_type == "NOT":
            self.instructions.append(self.current_token)
            self.match("NOT")
            expression_type = self.factor()
            if expression_type != "BOOL":
                raise SemanticError(
                    f"Invalid operation: NOT operation not supported on type {expression_type} "
                    f"at line {self.current_token.line}"
                )
        else:
            self.error()

        return expression_type

    def print_statement(self):
        self.instructions.append(self.current_token)
        self.match("PRINT")
        self.instructions.append(self.current_token)
        self.match("LPAREN")
        if self.current_token.token_type != "RPAREN":
            self.argument_list()
        self.instructions.append(self.current_token)
        self.match("RPAREN")
        self.match("SEMICOLON")

    def function_or_procedure(self):
        self.current_scope += 1
        self.scopes.insert(self.current_scope, {})

        if self.current_token.token_type == "FUNCTION":
            self.instructions.append(self.current_token)
            self.match("FUNCTION")
            variable_token = self.current_token
            self.instructions.append(self.current_token)
            self.identifier()

            for scope in self.scopes:
                for token in scope.keys():
                    if token.value == variable_token.value:
                        raise SemanticError(
                            f"Function '{variable_token.value}' in line {variable_token.line} "
                            f"already declared in line {token.line}"
                        )

            self.instructions.append(self.current_token)
            self.match("LPAREN")

            list_of_parameters = []
            if self.current_token.token_type != "RPAREN":
                list_of_parameters = self.parameters()

            self.instructions.append(self.current_token)
            self.match("RPAREN")
            self.match("ARROW")
            variable_type = self.current_token.token_type
            self.tipo()
            temp_token = Token("BEGINFUNCTION", "begin_function", self.current_token.line)
            self.instructions.append(temp_token)
            self.match("LBRACE")

            self.function_or_procedure_scope()
            self.return_statement()
            temp_token = Token("ENDFUNCTION", "end_function", self.current_token.line)
            self.instructions.append(temp_token)
            self.match("RBRACE")
            self.scopes[self.current_scope - 1][variable_token] = {
                "variable_type": variable_type,
                "scope": self.current_scope - 1,
                "parameters": list_of_parameters,
            }
        elif self.current_token.token_type == "PROCEDURE":
            self.instructions.append(self.current_token)
            self.match("PROCEDURE")
            variable_token = self.current_token
            self.instructions.append(self.current_token)
            self.identifier()

            for scope in self.scopes:
                for token in scope.keys():
                    if token.value == variable_token.value:
                        raise SemanticError(
                            f"Procedure '{variable_token.value}' in line {variable_token.line} "
                            f"already declared in line {token.line}"
                        )

            self.instructions.append(self.current_token)
            self.match("LPAREN")

            list_of_parameters = []
            if self.current_token.token_type != "RPAREN":
                list_of_parameters = self.parameters()

            self.instructions.append(self.current_token)
            self.match("RPAREN")
            temp_token = Token("BEGINPROCEDURE", "begin_procedure", self.current_token.line)
            self.instructions.append(temp_token)
            self.match("LBRACE")
            self.function_or_procedure_scope()
            temp_token = Token("ENDPROCEDURE", "end_procedure", self.current_token.line)
            self.instructions.append(temp_token)
            self.match("RBRACE")
            self.scopes[self.current_scope - 1][variable_token] = {
                "variable_type": None,
                "scope": self.current_scope - 1,
                "parameters": list_of_parameters,
            }

        self.scopes.pop(self.current_scope)
        self.current_scope -= 1

    def function_or_procedure_scope(self):
        while self.current_token.token_type not in ["RBRACE", "RETURN"]:
            self.start_of_program()

    def function_or_procedure_call(self) -> Type:
        variable_token = self.current_token
        self.instructions.append(self.current_token)
        self.identifier()

        list_of_parameters = None
        for scope in self.scopes:
            for token in scope.keys():
                if token.value == variable_token.value:
                    list_of_parameters = scope[token]["parameters"]
                    break

        if list_of_parameters is None:
            raise SemanticError(
                f"Function '{variable_token.value}' in line {variable_token.line} not declared"
            )

        self.instructions.append(self.current_token)
        self.match("LPAREN")

        list_of_arguments = []
        if self.current_token.token_type != "RPAREN":
            list_of_arguments = self.argument_list()
        self.instructions.append(self.current_token)
        self.match("RPAREN")

        if len(list_of_parameters) != len(list_of_arguments):
            raise SemanticError(
                f"Invalid number of arguments in function '{variable_token.value}' at line {variable_token.line}. "
                f"Expected {len(list_of_parameters)} parameters, found {len(list_of_arguments)}"
            )

        for i in range(len(list_of_parameters)):
            if list_of_parameters[i] != list_of_arguments[i]:
                raise SemanticError(
                    f"Type mismatch: Cannot assign {list_of_arguments[i]} to {list_of_parameters[i]} "
                    f"parameter in function '{variable_token.value}' at line {variable_token.line}"
                )

        expression_type = self.get_variable_type(variable_token)

        return expression_type

    def parameters(self) -> list[Type]:
        list_of_parameters = []
        variable_type = self.current_token.token_type
        list_of_parameters.append(variable_type)

        self.tipo()
        variable_token = self.current_token
        self.instructions.append(self.current_token)
        self.identifier()
        self.scopes[self.current_scope][variable_token] = {
            "variable_type": variable_type,
            "scope": self.current_scope,
        }

        while self.current_token.token_type == "COLON":
            self.instructions.append(self.current_token)
            self.match("COLON")
            variable_type = self.current_token.token_type
            list_of_parameters.append(variable_type)

            self.tipo()
            variable_token = self.current_token
            self.instructions.append(self.current_token)
            self.identifier()
            self.scopes[self.current_scope][variable_token] = {
                "variable_type": variable_type,
                "scope": self.current_scope,
            }

        return list_of_parameters

    def argument_list(self) -> list[Type]:
        list_of_arguments = [self.expression()]

        while self.current_token.token_type == "COLON":
            self.instructions.append(self.current_token)
            self.match("COLON")
            list_of_arguments.append(self.expression())

        return list_of_arguments

    def return_statement(self):
        self.instructions.append(self.current_token)
        self.match("RETURN")
        self.expression()
        self.match("SEMICOLON")

    def if_statement(self):
        self.instructions.append(self.current_token)
        self.match("IF")
        self.instructions.append(self.current_token)
        self.match("LPAREN")
        expression_type = self.boolean_expression()
        if expression_type != "BOOL":
            raise SemanticError(
                f"Type mismatch: Cannot use {expression_type} in IF statement at line {self.current_token.line}"
            )
        self.instructions.append(self.current_token)
        self.match("RPAREN")
        temp_token = Token("BEGINIF", "begin_if", self.current_token.line)
        self.instructions.append(temp_token)
        self.match("LBRACE")
        self.conditional_scope()
        temp_token = Token("ENDIF", "end_if", self.current_token.line)
        self.instructions.append(temp_token)
        self.match("RBRACE")

        if self.current_token is not None and self.current_token.token_type == "ELSE":
            self.instructions.append(self.current_token)
            self.match("ELSE")
            temp_token = Token("BEGINELSE", "begin_else", self.current_token.line)
            self.instructions.append(temp_token)
            self.match("LBRACE")
            self.conditional_scope()
            temp_token = Token("ENDELSE", "end_else", self.current_token.line)
            self.instructions.append(temp_token)
            self.match("RBRACE")

    def if_statement_while(self):
        self.instructions.append(self.current_token)
        self.match("IF")
        self.instructions.append(self.current_token)
        self.match("LPAREN")
        expression_type = self.boolean_expression()
        if expression_type != "BOOL":
            raise SemanticError(
                f"Type mismatch: Cannot use {expression_type} in IF statement at line {self.current_token.line}"
            )
        self.instructions.append(self.current_token)
        self.match("RPAREN")
        temp_token = Token("BEGINIF", "begin_if", self.current_token.line)
        self.instructions.append(temp_token)
        self.match("LBRACE")
        self.conditional_scope_while()
        temp_token = Token("ENDIF", "end_if", self.current_token.line)
        self.instructions.append(temp_token)
        self.match("RBRACE")

        if self.current_token is not None and self.current_token.token_type == "ELSE":
            self.instructions.append(self.current_token)
            self.match("ELSE")
            temp_token = Token("BEGINELSE", "begin_else", self.current_token.line)
            self.instructions.append(temp_token)
            self.match("LBRACE")
            self.conditional_scope_while()
            temp_token = Token("ENDELSE", "end_else", self.current_token.line)
            self.instructions.append(temp_token)
            self.match("RBRACE")

    def conditional_scope(self):
        self.current_scope += 1
        self.scopes.insert(self.current_scope, {})

        while (
            self.current_token.token_type != "RBRACE"
            and self.current_token.token_type != "ELSE"
        ):
            self.start_of_program()

        self.scopes.pop(self.current_scope)
        self.current_scope -= 1

    def conditional_scope_while(self):
        self.current_scope += 1
        self.scopes.insert(self.current_scope, {})

        while (
            self.current_token.token_type != "RBRACE"
            and self.current_token.token_type != "ELSE"
        ):
            self.start_of_while()

        self.scopes.pop(self.current_scope)
        self.current_scope -= 1

    def while_loop(self):
        self.instructions.append(self.current_token)
        self.match("WHILE")
        self.instructions.append(self.current_token)
        self.match("LPAREN")
        expression_type = self.boolean_expression()
        if expression_type != "BOOL":
            raise SemanticError(
                f"Type mismatch: Cannot use {expression_type} in WHILE statement at line {self.current_token.line}"
            )
        self.instructions.append(self.current_token)
        self.match("RPAREN")
        temp_token = Token("BEGINLOOP", "begin_loop", self.current_token.line)
        self.instructions.append(temp_token)
        self.match("LBRACE")
        self.loop_scope()
        temp_token = Token("ENDLOOP", "end_loop", self.current_token.line)
        self.instructions.append(temp_token)
        self.match("RBRACE")

    def break_statement(self):
        self.instructions.append(self.current_token)
        self.match("BREAK")
        self.match("SEMICOLON")

    def continue_statement(self):
        self.instructions.append(self.current_token)
        self.match("CONTINUE")
        self.match("SEMICOLON")

    def loop_scope(self):
        self.current_scope += 1
        self.scopes.insert(self.current_scope, {})

        while self.current_token.token_type != "RBRACE":
            self.start_of_while()

        self.scopes.pop(self.current_scope)
        self.current_scope -= 1

    def identifier(self):
        self.match("IDENTIFIER")

    def number(self):
        self.match("INTEGER")

    def boolean(self):
        self.match("TRUE" if self.current_token.token_type == "TRUE" else "FALSE")

    def tipo(self):
        self.match("INT" if self.current_token.token_type == "INT" else "BOOL")

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

    def get_variable_type(self, variable_token: Token) -> Type:
        for scope in self.scopes:
            for token in scope.keys():
                if token.value == variable_token.value:
                    return scope[token]["variable_type"]

        raise SemanticError(
            f"Variable '{variable_token.value}' used before declaration at line {variable_token.line}"
        )

    @staticmethod
    def check_types(left_type: Type, right_type: Type):
        if left_type == "INT" and right_type != "INT":
            raise SemanticError(
                f"Type mismatch: Cannot assign {right_type} to INT variable"
            )
        elif left_type == "BOOL" and right_type != "BOOL":
            raise SemanticError(
                f"Type mismatch: Cannot assign {right_type} to BOOL variable"
            )

    def error(self):
        raise SyntaxError(
            f"Syntax error at line {self.current_token.line} on token {self.current_token}"
        )
