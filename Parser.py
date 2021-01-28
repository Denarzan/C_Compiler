from abc import ABC


class MyNode:
    def masm_32(self):
        raise NotImplementedError


class Statement(MyNode, ABC):
    pass


class Scope(Statement):
    def __init__(self):
        self.scope = [dict()]
        self.func_array = []

    def __getitem__(self, item):
        for scope in self.scope[::-1]:
            if scope.get(item, None) is not None:
                return scope.get(item, None)

    def __setitem__(self, key, value):
        for scope in self.scope[::-1]:
            if scope.get(key, None) is not None:
                scope[key] = value
                return True
        return False

    def local_var(self, key, value):
        self.scope[-1][key] = value

    def get_local_var(self, key):
        return self.scope[-1].get(key, None)

    def create_scope(self):
        self.scope.append(dict())

    def delete_scope(self):
        self.scope.pop()

    def add_function(self, name_function):
        self.func_array.append(name_function)

    def exist_function(self, name_function):
        return name_function in self.func_array


class Declare(Statement):
    var_dict = Scope()
    offset = -4

    def __init__(self, dec_type, dec_name_string, default_expression=None):
        self.dec_type = dec_type
        self.dec_name_string = dec_name_string
        self.default_expression = default_expression

    def masm_32(self) -> str:
        if Declare.var_dict.get_local_var(self.dec_name_string) is not None:
            raise Exception(
                f"Variable {self.dec_name_string} is already declared. You are trying to switch its type to {self.dec_type}.")
        template = """
{dec}
push eax
""".strip()
        Declare.var_dict.local_var(self.dec_name_string, Declare.offset)
        Declare.offset -= 4
        return template.format(
            dec=self.default_expression.masm_32() if self.default_expression else "mov eax, 0")


class ReturnStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

    def masm_32(self) -> str:
        template = """
{expression}
mov esp, ebp
pop ebp
ret
""".strip()
        return template.format(expression=self.expression.masm_32())


class ExpStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

    def masm_32(self) -> str:
        return self.expression.masm_32()


class Conditional(Statement):
    def __init__(self, condition, con_true, con_false=None):
        self.con_false = con_false
        self.con_true = con_true
        self.condition = condition

    def masm_32(self) -> str:
        result = [self.condition.masm_32(), self.con_true.masm_32(), self.con_false.masm_32() if self.con_false else '']
        return result[0] + "\n.if eax\n" + result[1] + "\n.else\n" + result[2] + "\n.endif\n"


class Conditional_exp(ExpStatement):

    def __init__(self, condition, con_true, con_false):
        self.condition = condition
        self.con_true = con_true
        self.con_false = con_false

    def masm_32(self) -> str:
        result = [self.condition.masm_32(), self.con_true.masm_32(), self.con_false.masm_32() if self.con_false else '']
        return result[0] + "\n.if eax\n" + result[1] + "\n.else\n" + result[2] + "\n.endif\n"


class For(Statement):
    def __init__(self, initial, conditional, post_conditional, statement):
        self.statement = statement
        self.post_conditional = post_conditional
        self.conditional = conditional
        self.initial = initial

    def masm_32(self) -> str:
        self.initial.masm_32()


class While(Statement):
    def __init__(self, conditional, statement):
        self.statement = statement
        self.conditional = conditional

    def masm_32(self) -> str:
        template = """
_{start_mark}:
{conditional}
.if eax ==0
jmp _{end_mark}
.else
{statement}
jmp _{start_mark}
.endif
_{end_mark}:
add esp, 4
"""
        start_mark = mark_generating()
        end_mark = mark_generating()
        Declare.var_dict.create_scope()
        result = template.format(start_mark=start_mark, end_mark=end_mark,
                               conditional=self.conditional.masm_32() if self.conditional is not None else '',
                               statement=self.statement.masm_32())
        Declare.var_dict.delete_scope()
        return result


class ForDecl(Statement):
    def __init__(self, initial, conditional, post_conditional, statement):
        self.statement = statement
        self.post_conditional = post_conditional
        self.conditional = conditional
        self.initial = initial

    def masm_32(self) -> str:
        template = """
{initial}
_{start_mark}:
{conditional}
.if eax ==0
jmp _{end_mark}
.else
{statement}
{post_conditional}
jmp _{start_mark}
.endif
_{end_mark}:
"""
        start_mark = mark_generating()
        end_mark = mark_generating()
        return template.format(initial=self.initial.masm_32() if self.initial is not None else '',
                               start_mark=start_mark, end_mark=end_mark,
                               conditional=self.conditional.masm_32() if self.conditional is not None else '',
                               post_conditional=self.post_conditional.masm_32()
                               if self.post_conditional is not None else '',
                               statement=self.statement.masm_32())


class Expression(MyNode, ABC):
    pass


class Constant(Expression):
    def __init__(self, value):
        self.value = value

    def masm_32(self) -> str:
        return f"mov eax, {int(float(self.value))}"


class BinaryOperation(Expression):
    def __init__(self, left, operation, right):
        self.left = left
        self.operation = operation
        self.right = right

    def masm_32(self) -> str:
        template: str
        if self.operation == "+":
            template = """
{left_expression}
push eax
{right_expression}
pop ebx
add eax,ebx
""".strip()
        elif self.operation == "-":
            template = """
{right_expression}
push eax
{left_expression}
pop ebx
sub eax, ebx 
""".strip()
        elif self.operation == "<":
            template = """
{left_expression}
push eax
{right_expression}
pop ebx
.if ebx < eax
    mov eax, 1
.else
    mov eax, 0
.endif
""".strip()
        elif self.operation == ">":
            template = """
{left_expression}
push eax
{right_expression}
pop ebx
.if ebx > eax
    mov eax, 1
.else
    mov eax, 0
.endif
""".strip()
        elif self.operation == "==":
            template = """
{left_expression}
push eax
{right_expression}
pop ebx
.if eax == ebx
mov eax, 1
.else
mov eax, 0
.endif
""".strip()
        elif self.operation == "*":
            template = """
{right_expression}
push eax
{left_expression}
pop ebx
mul ebx 
""".strip()
        elif self.operation == "/":
            template = """
{left_expression}
push eax
{right_expression}
mov ebx, eax
pop eax
xor edx, edx
div ebx
""".strip()
        elif self.operation == "%":
            template = """
{left_expression}
push eax
{right_expression}
mov ebx, eax
pop eax
xor edx, edx
div ebx
mov eax, edx
""".strip()
        else:
            raise Exception(
                f"Unknown binary operator: {self.operation}")
        return template.format(left_expression=self.left.masm_32(),
                               right_expression=self.right.masm_32())


class UnaryOperation(Expression):
    def __init__(self, operation, expression):
        self.operation = operation
        self.expression = expression

    def masm_32(self) -> str:
        template: str
        if self.operation == "-":
            template = """
{operation}
neg eax
"""
        elif self.operation == "postfix_++":
            offset = Declare.var_dict[self.expression.name_string]
            template = """
{{operation}}
inc dword ptr[ebp + {offset}]
""".format(offset=offset)
        else:
            raise Exception(
                f"Unknown unary operator: {self.operation}")
        return template.format(operation=self.expression.masm_32())


class Variable(Expression):
    def __init__(self, name_string):
        self.name_string = name_string

    def masm_32(self) -> str:
        offset = Declare.var_dict[self.name_string]
        if offset is None:
            raise Exception(
                f"Variable is not declared: {self.name_string}")
        return f"mov eax, [ebp + {offset}]"


class Assign(Expression):
    def __init__(self, ass_name_string, ass_expression):
        self.ass_expression = ass_expression
        self.ass_name_string = ass_name_string

    def masm_32(self) -> str:
        offset = Declare.var_dict[self.ass_name_string]
        if offset is None:
            raise Exception(f"Variable is not declared: {self.ass_name_string}")
        template = """
{asn}
mov [ebp + {offset}], eax
""".strip()
        return template.format(asn=self.ass_expression.masm_32(), offset=offset)


class Wrapper:

    def __init__(self, tokens):
        self.index = -1
        self.tokens = tokens

    def look_ahead(self):
        return self.tokens[self.index + 1] if len(self.tokens) > self.index + 1 else None

    def next_index(self):
        self.index += 1
        return self.tokens[self.index]

    def super_look_ahead(self, amount):
        return self.tokens[self.index + 1:self.index + 1 + amount]


class Program(MyNode):
    def __init__(self, functions):
        self.functions = functions

    def masm_32(self) -> str:
        Declare.var_dict = Scope()
        template = """.386

.model flat, stdcall

option casemap:none

include D://masm32/include/windows.inc
include D://masm32/include/kernel32.inc
include D://masm32/include/user32.inc
include D://masm32/include/masm32.inc
include D://masm32/include/masm32rt.inc 

includelib D://masm32/lib/kernel32.lib
includelib D://masm32/lib/masm32.lib
includelib D://masm32/lib/user32.lib

main PROTO

.data

.code

start:
    invoke main
    fn MessageBox,0,str$(eax), "Lab6" ,MB_OK
    invoke ExitProcess, 0

{functions}

END start
""".strip()
        functions = list()
        for function in self.functions:
            functions.append(function.masm_32())
            Declare.offset = -4
        return template.format(functions="\n".join(functions))


class Function(MyNode):
    functions = dict()  # key - tuple(name, amount of arguments), value - (or have statement list)

    def __init__(self, name_string, statement_list, parameters):
        self.statement_list = statement_list
        self.name_string = name_string
        self.parameters = parameters

    def masm_32(self) -> str:
        Declare.var_dict.create_scope()
        for i, param in enumerate(self.parameters[::-1]):
            Declare.var_dict.local_var(param, 8 + i * 4)
        template = """
{name} PROC
push ebp
mov ebp, esp
{statement_list}
mov esp, ebp
pop ebp
ret
{name} ENDP
""".strip()
        code = template.format(
            name=self.name_string,
            statement_list="\n".join(
                s.masm_32()
                for s in self.statement_list
            )
        )
        Declare.var_dict.delete_scope()
        return code


class FunctionCalling(Expression):

    def __init__(self, func_name, args):
        self.args = args
        self.func_name = func_name

    def masm_32(self) -> str:
        arguments = [argument.masm_32() for argument in self.args]
        code = "\npush eax\n".join(
            arguments[::-1]) + "\npush eax\n" + f"call {self.func_name}\n" + f"add esp, {len(arguments) * 4}\n"
        return code


class Compound(Statement):
    def __init__(self, statements):
        self.statements = statements

    def masm_32(self):
        Declare.var_dict.create_scope()
        result = "\n".join(map(lambda x: x.masm_32(), self.statements))
        Declare.var_dict.delete_scope()
        return result


def program_parsing(tokens) -> Program:
    functions = []
    while tokens.look_ahead() is not None:
        functions.append(func_parsing(tokens))
    return Program(functions)


def func_parsing(tokens: Wrapper):
    if tokens.look_ahead().name == "int":
        tokens.next_index()
        if tokens.look_ahead().name == "identifier":
            name = tokens.next_index().value
            Declare.var_dict.add_function(name)
            parameters = []
            if tokens.look_ahead().name == "(":
                tokens.next_index()
                if tokens.look_ahead().name == "int":
                    tokens.next_index()
                    if tokens.look_ahead().name == "identifier":
                        parameters.append(tokens.next_index().value)
                        while tokens.look_ahead().name == ",":
                            tokens.next_index()
                            if tokens.look_ahead().name == "int":
                                tokens.next_index()
                                if tokens.look_ahead().name == "identifier":
                                    parameters.append(tokens.next_index().value)
                if tokens.look_ahead().name == ")":
                    tokens.next_index()
                    if tokens.look_ahead().name == ";":
                        tokens.next_index()
                        Function.functions[(name, len(parameters))] = Function.functions.get((name, len(parameters)),
                                                                                             False)
                        return Function(name, None, parameters)
                    t = tokens.look_ahead()
                    if t.name == "{":
                        tokens.next_index()
                        function_exist = Function.functions.get((name, len(parameters)), None)
                        if function_exist is not None and function_exist:
                            raise Exception(f"Error. Function redeclaration. Row: {t.row}. Column: {t.column}.")
                        Function.functions[(name, len(parameters))] = True
                        statements = []
                        Declare.var_dict.create_scope()
                        for p in parameters:
                            Declare.var_dict.local_var(p, 0)
                        try:
                            while tokens.look_ahead().name != "}":
                                statement = statement_parsing(tokens)
                                statements.append(statement)
                        except AttributeError:
                            raise Exception(f"Error. Missing brace in function. Row: {t.row}. Column: {t.column}.")
                        Declare.var_dict.delete_scope()
                        tokens.next_index()
                        return Function(name, statements, parameters)


def statement_parsing(tokens):
    if tokens.look_ahead().name == "return":
        tokens.next_index()
        expression = exp_parsing(tokens)
        if tokens.look_ahead().name == ";":
            tokens.next_index()
            return ReturnStatement(expression)
    elif tokens.look_ahead().name in ("int", "float"):
        return declare_parsing(tokens)
    elif tokens.look_ahead().name == "if":
        tokens.next_index()
        if tokens.next_index().name == "(":
            expression = exp_parsing(tokens)
            if tokens.next_index().name == ")":
                statement = statement_parsing(tokens)
                if tokens.look_ahead().name == "else":
                    tokens.next_index()
                    other_statement = statement_parsing(tokens)
                    return Conditional(expression, statement, other_statement)
                return Conditional(expression, statement)
    elif tokens.look_ahead().name == "for":
        tokens.next_index()
        if tokens.look_ahead().name == "(":
            tokens.next_index()
            if tokens.look_ahead().name in ("int", "float"):
                initial = declare_parsing(tokens)
                conditional = exp_option_semicolon_parsing(tokens)
                post_expression = exp_option_close_paren_parsing(tokens)
                if conditional is None:
                    conditional = Constant(1)
                statement = statement_parsing(tokens)
                return ForDecl(initial, conditional, post_expression, statement)
            else:
                initial = exp_option_semicolon_parsing(tokens)
                conditional = exp_option_semicolon_parsing(tokens)
                post_expression = exp_option_close_paren_parsing(tokens)
                if conditional is None:
                    conditional = Constant(1)
                statement = statement_parsing(tokens)
                return For(initial, conditional, post_expression, statement)
    elif tokens.look_ahead().name == "while":
        tokens.next_index()
        if tokens.look_ahead().name == "(":
            tokens.next_index()
            conditional = exp_option_close_paren_parsing(tokens)
            if conditional is None:
                conditional = Constant(1)
            statement = statement_parsing(tokens)
            return While(conditional, statement)
    elif tokens.look_ahead().name == "{":
        Declare.var_dict.create_scope()
        tokens.next_index()
        statements = []
        while tokens.look_ahead().name != "}":
            statements.append(statement_parsing(tokens))
        if tokens.look_ahead().name == "}":
            tokens.next_index()
            Declare.var_dict.delete_scope()
            return Compound(statements)
    else:
        exp = exp_parsing(tokens)
        if tokens.look_ahead().name == ";":
            tokens.next_index()
            return ExpStatement(exp)


def binary_operator_priority(operators, func):
    def prior_func(tokens):
        left = func(tokens)
        while tokens.look_ahead().name in operators:
            op = tokens.next_index().name
            right = func(tokens)
            left = BinaryOperation(left, op, right)
        return left

    return prior_func


def declare_parsing(tokens):
    if tokens.look_ahead().name in ("int", "float"):
        dec_type = tokens.next_index().name
        if tokens.look_ahead().name == "identifier":
            t = tokens.next_index()
            id_name = t.value
            if Declare.var_dict.get_local_var(id_name):
                raise Exception(f"Double declaration of variable. Row: {t.row}. Column: {t.column}.")
            exp = None
            if tokens.look_ahead().name == "=":
                tokens.next_index()
                exp = exp_parsing(tokens)
            if tokens.look_ahead().name == ";":
                tokens.next_index()
            Declare.var_dict.local_var(id_name, 0)
            return Declare(dec_type, id_name, exp)


def exp_option_semicolon_parsing(tokens):
    t = tokens.look_ahead()
    if tokens.look_ahead().name == ";":
        tokens.next_index()
        return None
    exp = exp_parsing(tokens)
    if tokens.next_index().name == ";":
        return exp
    else:
        raise Exception(f"Error. Bad syntax in for. Column: {t.column}. Row: {t.row}.")


def exp_option_close_paren_parsing(tokens):
    t = tokens.look_ahead()
    if tokens.look_ahead().name == ")":
        tokens.next_index()
        return None
    exp = exp_parsing(tokens)
    if tokens.next_index().name == ")":
        return exp
    else:
        raise Exception(f"Error. Bad syntax in for. Column: {t.column}. Row: {t.row}.")


def exp_parsing(tokens):
    if list(map(lambda x: x.name, tokens.super_look_ahead(2))) == ["identifier", "="]:
        id_name = tokens.next_index()
        tokens.next_index()
        exp = exp_parsing(tokens)
        return Assign(id_name.value, exp)
    elif list(map(lambda x: x.name, tokens.super_look_ahead(2))) == ["identifier", "/="]:
        id_name = tokens.next_index()
        tokens.next_index()
        exp = exp_parsing(tokens)
        return Assign(id_name.value, BinaryOperation(Variable(id_name.value), "/", exp))
    else:
        return conditional_exp_parsing(tokens)


def conditional_exp_parsing(tokens):
    exp = binary_operator_priority(["=="],
                                   binary_operator_priority(["<", ">"],
                                                            binary_operator_priority(["+", "-"],
                                                                                     binary_operator_priority(
                                                                                         ["*", "/", "%"],
                                                                                         binary_operator_priority(
                                                                                             ["++", "--"],
                                                                                             factor_parsing)))))(tokens)
    if tokens.look_ahead().name == '?':
        t = tokens.next_index()
        cond = exp_parsing(tokens)
        if tokens.look_ahead().name == ":":
            tokens.next_index()
            cond_exp = conditional_exp_parsing(tokens)
            return Conditional_exp(exp, cond, cond_exp)
        else:
            raise Exception(f"Error. Expected :. Column: {t.column}. Row: {t.row}.")
    return exp


def factor_parsing(tokens):
    if tokens.look_ahead().name == "(":
        tokens.next_index()
        exp = exp_parsing(tokens)
        if tokens.look_ahead().name == ")":
            tokens.next_index()
            return exp
    elif tokens.look_ahead().name == "-":
        return UnaryOperation(tokens.next_index().name, factor_parsing(tokens))
    elif tokens.look_ahead().name == "constant":
        return Constant(tokens.next_index().value)
    elif tokens.look_ahead().name == "identifier":
        t = tokens.next_index()
        name = t.value
        arguments = []
        if tokens.look_ahead().name == "(":
            tokens.next_index()
            if tokens.look_ahead().name != ")":
                arguments.append(exp_parsing(tokens))
                while tokens.look_ahead().name == ",":
                    tokens.next_index()
                    arguments.append(exp_parsing(tokens))
            if tokens.look_ahead().name == ")":
                tokens.next_index()
                if Function.functions.get((name, len(arguments)), None) is None:
                    raise Exception(f"Error. Function is not declared. Row: {t.row}. Column: {t.column}.")
                return FunctionCalling(name, arguments)
        elif tokens.look_ahead().name == "++":
            tokens.next_index()
            if Declare.var_dict[name] is None:
                raise Exception(f"Such identifier is not exist. Row: {t.row}. Column: {t.column}.")
            return UnaryOperation("postfix_++", Variable(name))
        if Declare.var_dict[name] is None:
            raise Exception(f"Such identifier is not exist. Row: {t.row}. Column: {t.column}.")
        return Variable(name)


mark_value = 0


def mark_generating():
    global mark_value
    mark_value += 1
    return mark_value

# <function> ::= "int" <id> "(" ")" "{" { <statement> } "}"
# <statement> ::= "return" <exp> ";"
#             | <exp> ";"
#             | <type> <id> [ = <exp> ] ";"
# <exp> ::= <id> "=" <exp> | <add> {"<" <add>}
# <add> ::= <term> { ("+" | "-") <term> }
# <term> ::= <factor> { ("*" | "/") <factor> }
# <factor> ::= "(" <exp> ")" | <unary_op> <factor> | <int> | <id>
# - * / + - < =
