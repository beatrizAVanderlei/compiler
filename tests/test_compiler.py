import pytest

from compiler import Compiler


class TestCompiler:
    @staticmethod
    def check_tokens_and_symbol_table_length(
        compiler, tokens_length, symbol_table_length
    ):
        assert len(compiler.lexer.tokens) == tokens_length
        assert len(compiler.lexer.symbol_table.values()) == symbol_table_length

    def test_successful_function(self):
        code = """
        function sum(int a, int b) -> int {
            return a + b;
        }
        """
        compiler = Compiler(code)
        compiler.compile()

        # Testing lexer
        self.check_tokens_and_symbol_table_length(compiler, 18, 5)

        variables_in_string = [token.value for token in compiler.lexer.symbol_table]

        assert "a" in variables_in_string
        assert "b" in variables_in_string
        assert "sum" in variables_in_string

        # Testing parser
        self.check_tokens_and_symbol_table_length(compiler, 18, 5)

        variables_tokens = [token for token in compiler.parser.symbol_table]
        for token in variables_tokens:
            if token.value == "sum" and token.line == 0:
                symbols = compiler.parser.symbol_table[token]
                assert symbols["variable_type"] == "INT"
                assert symbols["variable_value"] is None

            if token.value == "a" and token.line == 0:
                symbols = compiler.parser.symbol_table[token]
                assert symbols["variable_type"] == "INT"
                assert symbols["variable_value"] is None

            if token.value == "b" and token.line == 0:
                symbols = compiler.parser.symbol_table[token]
                assert symbols["variable_type"] == "INT"
                assert symbols["variable_value"] is None

    def test_unsuccessful_function(self):
        code = """
        function int sum(int a, int b) {
            return a + b;
        }
        """
        compiler = Compiler(code)
        with pytest.raises(SyntaxError):
            compiler.compile()
