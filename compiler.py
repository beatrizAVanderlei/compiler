from lexer import Lexer
from parser import Parser


class Compiler:
    def __init__(self, code: str):
        if not code:
            raise ValueError("Código não pode ser vazio")
        self.lexer = Lexer(code)
        self.parser = Parser()

    def compile(self):
        self.lexer.lex()
        self.parser.parse(self.lexer.tokens, self.lexer.symbol_table)
        print("Compilado com sucesso!")
