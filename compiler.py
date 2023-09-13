from lexer import Lexer
from parser import Parser
from tac_generator import ThreeAddressCodeGenerator  # Certifique-se de que o nome do arquivo e da classe está correto


class Compiler:
    def __init__(self, code: str):
        if not code:
            raise ValueError("Code cannot be empty!")
        self.lexer = Lexer(code)
        self.parser = Parser()
        self.tac_generator = ThreeAddressCodeGenerator()  # Cria uma instância da classe ThreeAddressCodeGenerator

    def compile(self):
        self.lexer.lex()
        self.parser.parse(self.lexer.tokens, self.lexer.symbol_table)

        # Chama o método extract_instructions e passa self.parser.instructions como argumento
        instructions_tac = self.tac_generator.extract_instructions(self.parser.instructions)

        self.tac_generator.start()
        # Imprime as instruções extraídas (se necessário)
        for i, instruction_tac in enumerate(instructions_tac):
           print(f"Instrução {i + 1}: {instruction_tac}")

        print("Successfully compiled!")

