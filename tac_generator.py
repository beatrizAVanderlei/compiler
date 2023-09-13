from lexer import Token


class ThreeAddressCodeGenerator:
    def __init__(self):
        self.index = 0
        self.tokens = None
        self.current_token = None
        self.instructions = []
        self.labels = 0

    def extract_instructions(self, tokens: list[Token]):
        self.tokens = tokens
        max_line = max(self.tokens, key=lambda x: x.line).line
        self.current_token = self.tokens[self.index]

        for i in range(1, max_line+1):
            aux_list = []
            while self.current_token is not None and self.current_token.line == i:
                aux_list.append(self.current_token)
                self.consume_token()
            if aux_list:
                self.instructions.append(aux_list)

        return self.instructions

    def consume_token(self):
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def start(self):
        arq = open("output.txt", 'w')
        i = 0
        while i < len(self.instructions):
            if len(self.instructions[i]) > 1 and self.instructions[i][1].token_type == 'ASSIGN':
                self.get_attribution(self.instructions[i], arq)
            elif len(self.instructions[i]) > 1 and self.instructions[i][1].token_type == 'LPAREN' and self.instructions[i][0].token_type == 'IDENTIFIER':
                self.get_declaration(self.instructions[i], arq)
            elif len(self.instructions[i]) > 1 and self.instructions[i][0].token_type in ['FUNCTION', 'PROCEDURE']:
                self.get_function(self.instructions[i], arq)
            elif self.instructions[i][0].token_type in ['ENDFUNCTION', 'ENDPROCEDURE']:
                self.get_endfunction(self.instructions[i], arq)
            elif self.instructions[i][0].token_type == 'RETURN':
                self.get_return(self.instructions[i], arq)
            elif self.instructions[i][0].token_type == 'PRINT':
                self.get_print(self.instructions[i], arq)
            elif self.instructions[i][0].token_type == 'IF':
                aux = i
                else_end = aux
                while aux < len(self.instructions) and self.instructions[aux][0].token_type != 'ENDIF':
                    aux = aux + 1

                if len(self.instructions[aux]) > 1 and self.instructions[aux][1].token_type == 'ELSE':
                    while else_end < len(self.instructions) and self.instructions[else_end][0].token_type != 'ENDELSE':
                        else_end += 1
                self.get_if(i, aux, arq)
                i = else_end

            elif self.instructions[i][0].token_type == 'WHILE':
                while_scope = 1
                aux = i
                while while_scope != 0:
                    if self.instructions[aux][0].token_type == 'BEGINLOOP':
                        while_scope += 1
                    elif self.instructions[aux][0].token_type == 'ENDLOOP':
                        while_scope -= 1
                    aux = aux + 1
                self.get_while(i, aux, arq)
                i = aux - 1

            elif len(self.instructions[i]) == 1 and self.instructions[i][0].token_type == 'IDENTIFIER':
                arq.write(f"{self.instructions[i][0].value} = undefined\n")

            i += 1

        arq.close()

    def get_else(self, arq):
        arq.write("entrei no if-else\n")

    def get_while(self, instruction_begin, instruction_end, arq):
        local_label = 0
        params = []
        i = 0

        while i < len(self.instructions[instruction_begin]) and self.instructions[instruction_begin][
            i].token_type != 'BEGINLOOP':
            if self.instructions[instruction_begin][i].token_type not in ['RPAREN', 'LPAREN', 'WHILE']:
                params.append(self.instructions[instruction_begin][i].value)
            i += 1

        params_str = " ".join(params)

        start_while = self.labels  # Salva o valor atual dos rótulos
        end_while = self.labels + 1

        arq.write(f"\nL{start_while}:\n")
        arq.write(f"t{local_label} = {params_str}\n")
        arq.write(f"ifFalse t{local_label} go to L{end_while}\n")

        j = instruction_begin + 1
        while j < instruction_end:
            if len(self.instructions[j]) > 1 and self.instructions[j][1].token_type == 'ASSIGN':
                self.get_attribution(self.instructions[j], arq)

            elif self.instructions[j][0].token_type == 'BREAK':
                arq.write(f"go to L{end_while}\n")

            elif self.instructions[j][0].token_type == 'CONTINUE':
                arq.write(f"go to L{start_while}\n")

            elif len(self.instructions[j]) > 1 and self.instructions[j][1].token_type == 'LPAREN' and self.instructions[j][0].token_type == 'IDENTIFIER':
                self.get_declaration(self.instructions[j], arq)

            elif self.instructions[j][0].token_type == 'PRINT':
                self.get_print(self.instructions[j], arq)

            elif len(self.instructions[j]) == 1 and self.instructions[j][0].token_type == 'IDENTIFIER':
                arq.write(f"{self.instructions[j][0].value} = undefined\n")

            elif self.instructions[j][0].token_type == 'IF':
                aux = j
                while aux < len(self.instructions) and self.instructions[aux][0].token_type != 'ENDIF':
                    aux = aux + 1
                self.get_if_while(j, aux, arq, start_while, end_while)
                j = aux

            elif self.instructions[j][0].token_type == 'WHILE':
                while_scope = 1
                aux = j
                while while_scope != 0:
                    if self.instructions[aux][0].token_type == 'BEGINLOOP':
                        while_scope += 1
                    elif self.instructions[aux][0].token_type == 'ENDLOOP':
                        while_scope -= 1
                    aux = aux + 1
                self.get_while(j, aux, arq)
                j = aux - 1

            j += 1

        arq.write(f"go to L{start_while}\n")
        arq.write(f"L{end_while}:\n\n")

    def get_if_while(self, instruction_begin, instruction_end, arq, start_while, end_while):
        local_label = 0
        params = []
        i = 0

        while i < len(self.instructions[instruction_begin]) and self.instructions[instruction_begin][i].token_type != 'RPAREN':
            if self.instructions[instruction_begin][i].token_type not in ['RPAREN', 'LPAREN', 'IF']:
                params.append(self.instructions[instruction_begin][i].value)
            i += 1

        params_str = " ".join(params)

        end_if = end_while + 1

        arq.write(f"t{local_label} = {params_str}\n")
        end_else = 0

        if len(self.instructions[instruction_end]) > 1 and self.instructions[instruction_end][1].token_type == 'ELSE':
            end_else_loop = end_if
            end_if += 1
            arq.write(f"ifFalse t{local_label} go to L{end_else_loop}\n")

            end_else = instruction_end
            while end_else < len(self.instructions) and self.instructions[end_else][0].token_type != 'ENDELSE':
                end_else += 1
        else:
            arq.write(f"ifTrue t{local_label} go to L{end_if}\n")
            arq.write(f"go to L{start_while}\n")
            arq.write(f"L{end_if}:\n")

        teste = instruction_begin + 1

        self.labels = end_if + 1

        while teste < instruction_end:
            if len(self.instructions[teste]) > 1 and self.instructions[teste][1].token_type == 'ASSIGN':
                self.get_attribution(self.instructions[teste], arq)

            elif len(self.instructions[teste]) > 1 and self.instructions[teste][1].token_type == 'LPAREN' and \
                    self.instructions[teste][0].token_type == 'IDENTIFIER':
                self.get_declaration(self.instructions[teste], arq)

            elif self.instructions[teste][0].token_type == 'PRINT':
                self.get_print(self.instructions[teste], arq)

            elif self.instructions[teste][0].token_type == 'BREAK':
                arq.write(f"go to L{end_while}\n")

            elif self.instructions[teste][0].token_type == 'CONTINUE':
                arq.write(f"go to L{start_while}\n")

            elif self.instructions[teste][0].token_type == 'IF':
                aux = teste
                while aux < len(self.instructions) and self.instructions[aux][0].token_type != 'ENDIF':
                    aux = aux + 1
                self.get_if_while(teste, aux, arq, start_while, end_while)

            elif len(self.instructions[teste]) == 1 and self.instructions[teste][0].token_type == 'IDENTIFIER':
                arq.write(f"{self.instructions[teste][0].value} = undefined\n")

            elif self.instructions[teste][0].token_type == 'WHILE':
                while_scope = 1
                aux = teste
                while while_scope != 0:
                    if self.instructions[aux][0].token_type == 'BEGINLOOP':
                        while_scope += 1
                    elif self.instructions[aux][0].token_type == 'ENDLOOP':
                        while_scope -= 1
                    aux = aux + 1
                self.get_while(i, aux, arq)
                teste = aux - 1

            teste += 1

        arq.write(f"go to L{start_while}\n")

        if end_else != 0:
            if end_else > instruction_end:
                arq.write(f"L{end_else_loop}:\n")

                teste1 = end_else

                while teste1 <= end_else:
                    if len(self.instructions[teste1]) > 1 and self.instructions[teste1][1].token_type == 'ASSIGN':
                        self.get_attribution(self.instructions[teste1], arq)

                    elif len(self.instructions[teste1]) > 1 and self.instructions[teste1][1].token_type == 'LPAREN' and \
                            self.instructions[teste1][0].token_type == 'IDENTIFIER':
                        self.get_declaration(self.instructions[teste1], arq)

                    elif self.instructions[teste1][0].token_type == 'PRINT':
                        self.get_print(self.instructions[teste1], arq)

                    elif len(self.instructions[teste1]) == 1 and self.instructions[teste1][
                        0].token_type == 'IDENTIFIER':
                        arq.write(f"{self.instructions[teste1][0].value} = undefined\n")

                    elif self.instructions[teste1][0].token_type == 'WHILE':
                        while_scope = 1
                        aux = teste1
                        while while_scope != 0:
                            if self.instructions[aux][0].token_type == 'BEGINLOOP':
                                while_scope += 1
                            elif self.instructions[aux][0].token_type == 'ENDLOOP':
                                while_scope -= 1
                            aux = aux + 1
                        self.get_while(teste1, aux, arq)
                        teste1 = aux - 1

                    teste1 += 1

    def get_if(self, instruction_begin, instruction_end, arq):
        local_label = 0
        params = []
        i = 0

        while i < len(self.instructions[instruction_begin]) and self.instructions[instruction_begin][i].token_type != 'RPAREN':
            if self.instructions[instruction_begin][i].token_type not in ['RPAREN', 'LPAREN', 'IF']:
                params.append(self.instructions[instruction_begin][i].value)
            i += 1

        params_str = " ".join(params)

        start_if = self.labels
        end_if = self.labels - 1

        arq.write(f"\nt{local_label} = {params_str}\n")

        end_else = 0

        self.labels = end_if + 1

        if len(self.instructions[instruction_end]) > 1 and self.instructions[instruction_end][1].token_type == 'ELSE':
            end_else_loop = self.labels
            end_if += 1
            arq.write(f"ifFalse t{local_label} go to L{end_else_loop}\n")

            end_else = instruction_end
            while end_else < len(self.instructions) and self.instructions[end_else][0].token_type != 'ENDELSE':
                end_else += 1
        else:
            arq.write(f"ifFalse t{local_label} go to L{end_if}\n")

        j = instruction_begin
        while j < instruction_end:
            if len(self.instructions[j]) > 1 and self.instructions[j][1].token_type == 'ASSIGN':
                self.get_attribution(self.instructions[j], arq)

            elif len(self.instructions[j]) > 1 and self.instructions[j][1].token_type == 'LPAREN' and self.instructions[j][0].token_type == 'IDENTIFIER':
                self.get_declaration(self.instructions[j], arq)

            elif self.instructions[j][0].token_type == 'PRINT':
                self.get_print(self.instructions[j], arq)

            elif len(self.instructions[j]) == 1 and self.instructions[j][0].token_type == 'IDENTIFIER':
                arq.write(f"{self.instructions[j][0].value} = undefined\n")

            elif self.instructions[j][0].token_type == 'WHILE':
                while_scope = 1
                aux = j
                while while_scope != 0:
                    if self.instructions[aux][0].token_type == 'BEGINLOOP':
                        while_scope += 1
                    elif self.instructions[aux][0].token_type == 'ENDLOOP':
                        while_scope -= 1
                    aux = aux + 1
                self.get_while(j, aux, arq)
                j = aux - 1

            j += 1

        arq.write(f"go to L{end_if+1}\n")

        if end_else > instruction_end:

            arq.write(f"L{end_else_loop}:\n")

            teste1 = end_else -1

            while teste1 <= end_else:
                if len(self.instructions[teste1]) > 1 and self.instructions[teste1][1].token_type == 'ASSIGN':
                    self.get_attribution(self.instructions[teste1], arq)

                elif len(self.instructions[teste1]) > 1 and self.instructions[teste1][1].token_type == 'LPAREN' and \
                        self.instructions[teste1][0].token_type == 'IDENTIFIER':
                    self.get_declaration(self.instructions[teste1], arq)

                elif self.instructions[teste1][0].token_type == 'PRINT':
                    self.get_print(self.instructions[teste1], arq)

                elif len(self.instructions[teste1]) == 1 and self.instructions[teste1][0].token_type == 'IDENTIFIER':
                    arq.write(f"{self.instructions[teste1][0].value} = undefined\n")

                elif self.instructions[teste1][0].token_type == 'WHILE':
                    while_scope = 1
                    aux = teste1
                    while while_scope != 0:
                        if self.instructions[aux][0].token_type == 'BEGINLOOP':
                            while_scope += 1
                        elif self.instructions[aux][0].token_type == 'ENDLOOP':
                            while_scope -= 1
                        aux = aux + 1
                    self.get_while(teste1, aux, arq)
                    teste1 = aux - 1

                teste1 += 1

            arq.write(f"go to L{end_if+1}\n")

        arq.write(f"L{end_if+1}:\n")

        self.labels = end_if + 2

    def get_attribution(self, instruction, arq):
        if len(instruction) == 3:
            for item in instruction:
                arq.write(item.value + " ")
            arq.write("\n")

        else:
            if instruction[3].token_type == "LPAREN":
                params = []
                i = 4
                while i < len(instruction) and instruction[i].token_type != "RPAREN":
                    if instruction[i].token_type not in ["COLON", "RPAREN", "LPAREN"]:
                        params.append(instruction[i].value)
                    i += 1

                params_str = ", ".join(params)
                arq.write(f"{instruction[0].value} = call {instruction[2].value}({params_str})\n")

            else:
                arq.write("t0 = {0} {1} {2}".format(instruction[2].value, instruction[3].value, instruction[4].value) + "\n")
                anterior = 0
                i = 5
                while i < len(instruction):
                    arq.write("t{0} = t{1} {2} {3}".format(anterior + 1, anterior, instruction[i].value, instruction[i + 1].value) + "\n")
                    anterior += 1
                    i += 2
                arq.write("{0} = t{1}".format(instruction[0].value, anterior) + "\n")

    def get_return(self, instruction, arq):
        if len(instruction) == 2:
            for item in instruction:
                arq.write(item.value + " ")
            arq.write("\n")

        else:
            if instruction[2].token_type == "LPAREN":
                params = []
                i = 3
                while i < len(instruction) and instruction[i].token_type != "RPAREN":
                    if instruction[i].token_type not in ["COLON", "RPAREN", "LPAREN"]:
                        params.append(instruction[i].value)
                    i += 1

                params_str = ", ".join(params)
                arq.write(f"{instruction[0].value} call {instruction[1].value}({params_str})\n")

            else:
                arq.write("t0 = {0} {1} {2}".format(instruction[1].value, instruction[2].value, instruction[3].value) + "\n")
                anterior = 0
                i = 4
                while i < len(instruction):
                    arq.write("t{0} = t{1} {2} {3}".format(anterior + 1, anterior, instruction[i].value, instruction[i + 1].value) + "\n")
                    anterior += 1
                    i += 2

                arq.write("{0} = t{1}".format(instruction[0].value, anterior) + "\n")

    def get_declaration(self, instruction, arq):
        params = []
        i = 1
        while i < len(instruction) and instruction[i].token_type != "RPAREN":
            if instruction[i].token_type not in ["COLON", "RPAREN", "LPAREN"]:
                params.append(instruction[i].value)
            i += 1

        params_str = ", ".join(params)
        arq.write(f"call {instruction[0].value}({params_str})\n")

    def get_function(self, instruction, arq):
        params = []
        i = 2
        while i < len(instruction) and instruction[i].token_type != "RPAREN":
            if instruction[i].token_type not in ["COLON", "RPAREN", "LPAREN", "BEGINFUNCTION", "BEGINPROCEDURE"]:
                params.append(instruction[i].value)
            i += 1

        params_str = ", ".join(params)
        arq.write(f"\n{instruction[0].value} {instruction[1].value}({params_str}):\n")

    def get_print(self, instruction, arq):
        if len(instruction) == 4:
            for item in instruction:
                arq.write(item.value + " ")
            arq.write("\n")

        else:
            if instruction[3].token_type == "LPAREN":
                params = []
                i = 3

                while i < len(instruction) and instruction[i].token_type != "RPAREN":
                    if instruction[i].token_type not in ["COLON", "RPAREN", "LPAREN"]:
                        params.append(instruction[i].value)
                    i += 1

                params_str = ", ".join(params)
                arq.write(f"{instruction[0].value} (call {instruction[2].value}({params_str}))\n")

            else:
                arq.write("t0 = {0} {1} {2}".format(instruction[2].value, instruction[3].value, instruction[4].value) + "\n")
                anterior = 0
                i = 5

                while i < len(instruction) - 1:
                    arq.write("t{0} = t{1} {2} {3}".format(anterior + 1, anterior, instruction[i].value, instruction[i + 1].value) + "\n")
                    anterior += 1
                    i += 2

                arq.write("{0} = t{1}".format(instruction[0].value, anterior) + "\n")

    def get_endfunction(self, instruction, arq):
        arq.write(f"{instruction[0].value}\n\n")

    def error(self):
        raise SyntaxError(f"Unexpected token at line {self.current_token.line} on token {self.current_token}")
