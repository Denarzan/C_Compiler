from Lexer import Lexer
import Parser
from Parser import Wrapper

print("Компілятор почав роботу!")
output = open("6-5-Python-IO-81-Dakhno.asm", "w")

try:
    with open("6-5-Python-IO-81-Dakhno.txt", "r") as f:
        code = f.read()
        output.write(f"{Parser.program_parsing(Wrapper(Lexer.tokeniser(code))).masm_32()}")
        print("Компілятор завершив роботу!")
except Exception as error:
    output.write(str(error))
    print("Компілятор завершив роботу з помилкою!")
output.close()
