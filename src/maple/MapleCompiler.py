import os
import argparse

from MapleLexer import MapleLexer
from MapleParser import MapleParser
from MapleTranspiler import MapleTranspiler
from MapleError import MapleError

# :!python src\maple\MapleCompiler.py src\files\mpl\Test.mpl
def MapleCompile(file) -> None:
    with open(file, "r") as file:
        source_code = file.read()
        
    lexer = MapleLexer(source_code)
    tokens = lexer.tokenize()
    print(tokens)
    parser = MapleParser(tokens)
    ast = parser.parse() # Abstract Syntax Tree
    transpiler = MapleTranspiler(ast)
    cpp_code = transpiler.transpile() 
    
    # Going back one directory, then going to files/ and creating a file called {file_Maple}.cpp
    file_name = os.path.basename(file.name) # Gets the file name
    file_extension = os.path.splitext(file_name)[1] # Gets the file extension

    if file_extension != ".mpl":
        raise MapleError(f"Invalid file extension: {file_extension}", 0, 0)

    file_name = os.path.splitext(file_name)[0] # Gets the file name without the extension
    file_name = file_name + "_Maple.cpp" # Adds the _Maple.cpp extension
    os.chdir("src/files/cpp") # Goes back one directory, then into files/
    file_path = os.path.join(os.getcwd(), file_name) # Gets the file path

    # Creates the file
    with open(file_path, "w") as file:
        file.write(cpp_code)

    # Compiles the file
    os.system(f"g++ {file_path} -o {file_name}.exe")
    os.system(f"{file_name}.exe")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compiles Maple code")
    parser.add_argument("file", help="The .mpl file to compile")
    args = parser.parse_args()

    MapleCompile(args.file)
