from Token import Token


def find_row_col(code, i):
    new_code = code[:i]
    row = new_code.count("\n") + 1
    col = i - new_code.rfind("\n")
    return row, col


def is_float(stroka):
    try:
        float(stroka)
        return True
    except ValueError:
        return False


def is_int(stroka):
    try:
        (stroka[:2] in ("0x", "0X") and int(stroka[2:], 16)) or int(stroka)
        return True
    except ValueError:
        return False


def is_string(stroka):
    return stroka[0] == stroka[-1] == '"' and stroka.count('"') == 2


class Lexer:
    keywords = {"void", "int", "float", "char", "double", "long", "return", "null", "true", "false", "class", "if", "else", "while", "for"}
    one_symbols = {",", "=", ";", ":", "`", "'", "*", "/", "+", "-", "<", ">", "!", "(", ")", "{", "}", "[", "]", "%", "?"}
    double_symbols = {"<=", ">=", "!=", "==", "++", "--", "+=", "-=", "/="}
    whitespaces = {" ", "\t", "\n", "\r"}

    @classmethod
    def tokeniser(cls, code) -> object:
        index = 0
        tokens = []
        while index < len(code):
            if code[index] in cls.one_symbols:
                if code[index: index + 2] in cls.double_symbols:
                    token = Token(code[index:index + 2], None, *find_row_col(code, index))
                    tokens.append(token)
                    index += 2
                else:
                    token = Token(code[index], None, *find_row_col(code, index))
                    tokens.append(token)
                    index += 1
            elif code[index] in cls.whitespaces:
                index += 1
            elif code[index].isnumeric() or code[index] in (".", "'", '"'):
                i = index
                while index < len(code) and code[index] not in (*cls.one_symbols, *cls.double_symbols, *cls.whitespaces):
                    index += 1
                constant = code[i:index]
                if is_int(constant) or is_float(constant) or is_string(constant):
                    token = Token("constant", constant, *find_row_col(code, i))
                    tokens.append(token)
                else:
                    row_col_show = find_row_col(code, i)
                    raise Exception(f"syntax error, row and column: {row_col_show}")
            else:
                i = index
                while index < len(code) and code[index] not in (*cls.one_symbols, *cls.double_symbols, *cls.whitespaces):
                    index += 1
                constant = code[i:index]
                if constant in cls.keywords:
                    token = Token(constant, None, *find_row_col(code, i))
                    tokens.append(token)
                else:
                    token = Token("identifier", constant, *find_row_col(code, i))
                    tokens.append(token)
        return tokens
