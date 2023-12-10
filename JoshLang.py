import re
import os
import sys
import subprocess
from JLangError import JoshLangError

variable_types = ["i8", "i16", "i32", "i64", "bool", "str", "f32", "f64"]
type_dic = {
    "i8": "int8_t",
    "i16": "int16_t",
    "i32": "int32_t",
    "i64": "int64_t",
    "bool": "bool",
    "f32": "float",
    "f64": "double",
    "char": "char",
    "str": "std::string"
}

class Token:
    def __init__(self, type_, value, line_num, char_pos):
        self.type = type_
        self.value = value
        self.line_num = line_num
        self.char_pos = char_pos

    def __repr__(self):
        return f"Token({repr(self.type)}, {repr(self.value)}, {repr(self.line_num)}, {repr(self.char_pos)})"

class JoshLangLexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.current_position = 0

    def tokenize(self):
        # Regex for tokens
        token_specification = [
            ("NUMBER", r"\d+(\.\d*)?"), # Integer or decimal numbers

            # Keywords, the \b means that the keyword must be its own word and not substrings
            ("RUN", r"\brun\b"), # Run keyword
            ("DEC", r"\bdec\b"), # Declare keyword
            ("SET", r"\bset\b"), # Set keyword
            ("CH", r"\bch\b"), # Not constant keyword
            ("INTEGER8", r"\bi8\b"), # 8-bit integer keyword
            ("INTEGER16", r"\bi16\b"), # 16-bit integer keyword
            ("INTEGER32", r"\bi32\b"), # 32-bit integer keyword
            ("INTEGER64", r"\bi64\b"), # 64-bit integer keyword
            ("BOOLEAN", r"\bbool\b"), # Boolean keyword
            ("OUT", r"\bout\b"), # Output keyword
            ("IF", r"\bif\b"), # If keyword            ("END", r"\bend\b"), # End keyword (end of if statement)
            ("END", r"\bend\b"), # End keyword (end of if statement)
            ("AROUND", r"\baround\b"), # Around keyword (for loops)
            ("ROLL", r"\broll\b"), # Roll keyword (end of for loop)
            ("BACK", r"\bback\b"), # Back keyword (save current variable value)
            ("LOAD", r"\bload\b"), # Load keyword (load saved variable value)
            ("LIB", r"\blib @\w+"), # Library keyword (import libraries)
            ("FUNC", r"\bfnc\b"), # Function keyword
            ("RETURN", r"\breturn\b"), # Return keyword
            ("GREATER", r">"), # Greater than operator
            ("LESS", r"<"), # Less than operator
            ("ARROW", r"->"), # Array assign operator
            ("COMMA", r","), # Comma
            ("COLON", r":"), # Colon
            ("DOTDOT", r"\.\."), # Dot dot operator, used for ranges
            ("LEFT_PAREN", r"\("), # Left parenthesis
            ("LEFT_SQR_BRACKET", r"\["), # Left square bracket
            ("RIGHT_SQR_BRACKET", r"\]"), # Right square bracket
            ("LEFT_CRLY_BRACKET", r"\{"), # Left curly bracket
            ("RIGHT_CRLY_BRACKET", r"\}"), # Right curly bracket
            ("COMPARISON", r"\b==\b"), # Equal comparison operator

            # Other
            ("ID", r"[A-Za-z0-9_]+"),  # Identifiers (allowing alphanumeric characters and underscore)
            ("OP", r"[+\-*/]"), # Arithmetic operators
            ("NEWLINE", r"\n"), # Line endings
            ("SKIP", r"[ \t]+"), # Skip over spaces and tabs
        ]

        # Compile regex
        tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_specification)
        get_token = re.compile(tok_regex).match # Match regex to source code

        # Tokenize
        line_num = 1
        line_start = 0

        while self.current_position < len(self.source_code):
            match = get_token(self.source_code, self.current_position)
            if match is not None: # If the token is valid
                type_ = match.lastgroup
                char_pos = match.start() - line_start

                if type_ == "NEWLINE":
                    line_start = self.current_position
                    line_num += 1
                elif type_ != "SKIP":
                    value = match.group(type_) # Get the value of the token
                    if type_ == "NUMBER":
                        val = float(value) if "." in value else int(value)
                    self.tokens.append(Token(type_, value, line_num, char_pos)) # Appending the token
                self.current_position = match.end()
            else:
                sys.stderr.write("Illegal character: %s\\n" % self.source_code[self.current_position])
                sys.exit(1)

        return self.tokens

# The parser will be used to transpile the JoshLang code into C++ code
class ASTnode:
    def __init__(self, type_):
        self.type = type_
        self.children = []

    def __repr__(self):
        return f"ASTnode({repr(self.type)}, {repr(self.children)})"


class RUNnode(ASTnode):
    def __init__(self, times_to_run):
        super().__init__('RUN')
        self.times_to_run = times_to_run

    def __repr__(self):
        return f"RUNnode(times_to_run={self.times_to_run})"

class DECnode(ASTnode):
    def __init__(self, variable_type, variable_name, variable_value, is_constant=True, is_array=False, array_values=None):
        super().__init__('DEC')
        self.variable_type = variable_type
        self.variable_name = variable_name
        self.variable_value = variable_value
        self.is_constant = is_constant
        self.is_array = is_array 
        self.array_values = array_values

    def __repr__(self):
        return f"DECnode(variable_type={self.variable_type}, variable_name={self.variable_name}, variable_value={self.variable_value}, is_constant={self.is_constant}, is_array={self.is_array}, array_values={self.array_values}"

class SETnode(ASTnode):
    def __init__(self, target, value, target_is_array=False, target_array_index=None, value_is_array=False, value_array_index=None):
        super().__init__('SET')
        self.target = target
        self.value = value
        self.target_is_array = target_is_array
        self.target_array_index = target_array_index
        self.value_is_array = value_is_array
        self.value_array_index = value_array_index

    def __repr__(self):
        return f"SETnode(target={self.target}, value={self.value})"

class OUTnode(ASTnode):
    def __init__(self, variable_name, is_array=False, array_index=None):
        super().__init__('OUT')
        self.variable_name = variable_name
        self.is_array = is_array
        self.array_index = array_index

    def __repr__(self):
        return f"OUTnode(variable_name={self.variable_name}, is_array={self.is_array}, array_index={self.array_index})"
        
class IFnode(ASTnode):
    def __init__(self, condition):
        super().__init__('IF')
        self.condition = condition
        self.children = [] # List of nodes inside the if statement

    def __repr__(self):
        return f"IFnode(condition={self.condition})"

class CONDITIONnode(ASTnode):
    def __init__(self, left, operator, right):
        super().__init__('CONDITION')
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"CONDITIONnode(left={self.left}, operator={self.operator}, right={self.right})"

class ENDnode(ASTnode):
    def __init__(self):
        super().__init__('END')

    def __repr__(self):
        return f"ENDnode()"

class AROUNDnode(ASTnode):
    def __init__(self, variable, times_to_run, start_index=0):
        super().__init__('AROUND')
        self.variable = variable
        self.start_index = start_index
        self.times_to_run = times_to_run # This can also be thend indexx
        self.children = [] # List of nodes inside the for loop

    def __repr__(self):
        return f"AROUNDnode(times_to_run={self.times_to_run})"

class ROLLnode(ASTnode):
    def __init__(self):
        super().__init__('ROLL')

    def __repr__(self):
        return f"ROLLnode()"

class BACKnode(ASTnode):
    def __init__(self, variable_name):
        super().__init__('BACK')
        self.variable_name = variable_name

    def __repr__(self):
        return f"BACKnode(variable_name={self.variable_name})"

class LOADnode(ASTnode):
    def __init__(self, variable_name):
        super().__init__('LOAD')
        self.variable_name = variable_name

    def __repr__(self):
        return f"LOADnode(variable_name={self.variable_name})"

class FNCnode(ASTnode):
    def __init__(self, function_type, function_name, args: dict):
        super().__init__('FUNC')
        self.function_type = function_type
        self.function_name = function_name
        self.args = args
        self.body = []

    def __repr__(self):
        return f"FNCnode(function_name={self.function_name}, args={self.args}, body={self.body})"

class RETURNnode(ASTnode):
    def __init__(self, value):
        super().__init__('RETURN')
        self.value = value

    def __repr__(self):
        return f"RETURNnode(value={self.value})"

class CALLnode(ASTnode): # Function call
    def __init__(self, function_name, args: list):
        super().__init__('CALL')
        self.function_name = function_name
        self.args = args

    def __repr__(self):
        return f"CALLnode(function_name={self.function_name}, args={self.args})"

class RANGEnode(ASTnode):
    def __init__(self, start, end):
        super().__init__('RANGE')
        self.start = start
        self.end = end

    def __repr__(self):
        return f"RANGEnode(start={self.start}, end={self.end})"

class JoshLangParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_position = 0
        self.nodes = [] # List of nodes in the AST
        self.symbol_table = {} # Dictionary of variables and their values
    
    def is_function_call(self):
        position = self.current_position
        if self.tokens[position].type == "ID" and position + 1 < len(self.tokens) and self.tokens[position + 1].type == "COLON":
            return True
        return False

    def parse(self):
        while self.current_position < len(self.tokens):
            if self.is_function_call():
                call_node = self.parse_call() # Call node returns instead of appending to nodes
                self.nodes.append(call_node)
            else:
                self.parse_statement()

        return self.nodes

    def parse_statement(self):
        token = self.tokens[self.current_position]

        if token.type == "RUN":
            self.parse_run()
        elif token.type == "DEC":
            self.parse_dec()
        elif token.type == "OUT":
            self.parse_out()
        elif token.type == "IF":
            self.parse_if()
        elif token.type == "END":
            self.parse_end()
        elif token.type == "SET":
            self.parse_set()
        elif token.type == "AROUND":
            self.parse_around()
        elif token.type == "ROLL":
            self.parse_roll()
        elif token.type == "BACK":
            self.parse_back()
        elif token.type == "LOAD":
            self.parse_load()
        elif token.type == "FUNC":
            self.parse_fnc()
        elif token.type == "RETURN":
            self.parse_return()
        elif self.is_function_call():
            self.parse_call()
        else:
            self.current_position += 1

    def parse_run(self):
        self.current_position += 1
        times_to_run = self.tokens[self.current_position].value
        self.current_position += 1
        
        run_node = RUNnode(times_to_run)
        self.nodes.append(run_node)

    def parse_dec(self):
        self.current_position += 1
        # Check if "ch" keyword is present, if so, is_constant is False, else proceed as normal
        if self.tokens[self.current_position].type == "CH":
            self.current_position += 1
            is_constant = False
        else:
            is_constant = True

        variable_type = self.tokens[self.current_position].value
        self.current_position += 1 # Move past variable type
        variable_name = self.tokens[self.current_position].value
        self.current_position += 1 # Move past variable name

        # Check for a function call
        if self.is_function_call():
            function_call_node = self.parse_call()
            print(function_call_node)
            self.nodes.append(DECnode(variable_type, variable_name, function_call_node, is_constant))

        else:
            # Initialize variable_value to None or a default value
            variable_value = None

            # Error handling
            if variable_name in self.symbol_table:  # Variable already exists
                raise JoshLangError(f"Variable {variable_name} already exists", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)
            elif variable_type not in variable_types:  # Invalid variable type 
                raise JoshLangError(f"Invalid variable type {variable_type}", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)

            # Check for array declaration
            is_array = False
            array_size = None
            array_values = []
            if self.current_position < len(self.tokens) and self.tokens[self.current_position].type == "LEFT_SQR_BRACKET":
                self.current_position += 2  # Move past '[' and ']'
                is_array = True
                array_size = self.tokens[self.current_position].value
                self.current_position += 1  # Move past array size
                if self.tokens[self.current_position].type == "ARROW":
                    self.current_position += 1  # Move past '->'
                    while self.tokens[self.current_position].type != "RIGHT_CRLY_BRACKET":
                        if self.tokens[self.current_position].type == "NUMBER":
                            array_values.append(self.tokens[self.current_position].value)  # Add value to list
                        self.current_position += 1  # Move past value
                    self.current_position += 1  # Move past '}'
            else:
                variable_value = self.tokens[self.current_position].value
                self.current_position += 1

            dec_node = DECnode(variable_type, variable_name, variable_value if not is_array else array_size, is_constant, is_array, array_values) 
            self.nodes.append(dec_node)

            # Add variable to symbol table
            self.symbol_table[variable_name] = {
                "type": variable_type,
                "is_constant": is_constant,
                "is_array": is_array,
                "array_values": array_values if is_array else None,
                "array_size": array_size if is_array else 0  # Use array_size instead of variable_value
            }


    def parse_set(self):
        self.current_position += 1 # Move past 'SET'
        target = self.tokens[self.current_position].value # Get the variable name
        self.current_position += 1 # Move past variable name
        
        # Array handling
        target_is_array = False
        target_index = None
        if self.tokens[self.current_position].type == "LEFT_SQR_BRACKET": # Target is an array
            target_is_array = True
            self.current_position += 1 # Move past '['
            target_index = self.tokens[self.current_position].value # Get the index

            # Error handling
            if int(target_index) > int(self.symbol_table[target]["array_size"]) - 1:
                raise JoshLangError(f"Index {target_index} out of range for array {target}", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)

            self.current_position += 1 # Move past index
            self.current_position += 1 # Move past ']'
            
            value = self.tokens[self.current_position].value # Get the value
            self.current_position += 1 # Move past value
            if self.tokens[self.current_position].type == "LEFT_SQR_BRACKET": # Value is an array
                self.current_position += 1 # Move past '['
                value_index = self.tokens[self.current_position].value # Get the value index
                self.current_position += 1
                self.current_position += 1
                try:
                    value = self.symbol_table[value]["array_values"][int(value_index)] # Get the value from the array
                except IndexError:
                    raise JoshLangError(f"Index {value_index} out of range for array {value}", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)
            else: # Value is a variable
                value = self.symbol_table[value]["array_values"][int(value)]
        else: # Target is a variable
            value = self.tokens[self.current_position].value
            self.current_position += 1
        
        # Error checking
        if target not in self.symbol_table: # Check if variable is declared
            line_num = self.tokens[self.current_position].line_num
            current_char = self.tokens[self.current_position].char_pos
            raise JoshLangError(f"Variable '{target}' not declared", line_num, current_char)

        if self.symbol_table[target]["is_constant"]: # Check if variable is constant
            line_num = self.tokens[self.current_position].line_num
            current_char = self.tokens[self.current_position].char_pos
            raise JoshLangError(f"Cannot set constant variable '{target}' (remember variables are constant by default)", line_num, current_char)

        if self.symbol_table[target]["type"]:
            # Checking if the value is a variable
            if value in self.symbol_table:
                # Checking if the variable types match
                if self.symbol_table[target]["type"] != self.symbol_table[value]["type"]:
                    line_num = self.tokens[self.current_position].line_num
                    current_char = self.tokens[self.current_position].char_pos
                    raise JoshLangError(f"Cannot set variable '{target}' of type '{self.symbol_table[target]['type']}' to variable '{value}' of type '{self.symbol_table[value]['type']}'", line_num, current_char)
            else:
                # Checking if the value is a number
                if not value.isnumeric():
                    line_num = self.tokens[self.current_position].line_num
                    current_char = self.tokens[self.current_position].char_pos
                    raise JoshLangError(f"Cannot set variable '{target}' of type '{self.symbol_table[target]['type']}' to '{value}' of type 'NUMBER'", line_num, current_char)


        set_node = SETnode(target, value, target_is_array, target_index)
        self.nodes.append(set_node) # Add the node to the AST

    def parse_out(self):
        self.current_position += 1
        variable_name = self.tokens[self.current_position].value
        self.current_position += 1
        
        # Check for array access
        if self.current_position < len(self.tokens) and self.tokens[self.current_position].type == "LEFT_SQR_BRACKET":
            self.current_position += 1 # Move past '['
            array_index = self.tokens[self.current_position].value # Get the array index
            self.current_position += 2 # Move past array index and ']' 

            out_node = OUTnode(variable_name, True, array_index)
        else:
            out_node = OUTnode(variable_name)

        self.nodes.append(out_node)
        
    def parse_if(self):
        self.current_position += 1
        left = self.tokens[self.current_position].value
        self.current_position += 1
        operator = self.tokens[self.current_position].value
        self.current_position += 1
        right = self.tokens[self.current_position].value
        self.current_position += 1

        condition_node = CONDITIONnode(left, operator, right)
        if_node = IFnode(condition_node)

        # Temporarily store the current list of nodes
        current_nodes = self.nodes
        self.nodes = []  # Create a new list for nodes inside the if block

        # Parse the code inside the if statement
        while self.current_position < len(self.tokens) and self.tokens[self.current_position].type != "END":
            self.parse_statement()
        
        # Add the parsed nodes to the if_node and restore the original nodes list
        if_node.children = self.nodes
        self.nodes = current_nodes
        self.nodes.append(if_node)

        # Parsing the END token 
        self.parse_end()

    def parse_end(self):
        self.current_position += 1

        end_node = ENDnode()
        self.nodes.append(end_node)
    
    def parse_around(self):
        self.current_position += 1 # Move past "AROUND" token
        variable = self.tokens[self.current_position].value # Get the loop variable
        self.current_position += 1 # Move past the loop variable
        
        # Checking for a range
        starting_index = 0
        ending_index = 0
        if self.tokens[self.current_position + 1].type == "DOTDOT":
            starting_index = self.tokens[self.current_position].value # Get the starting index
            self.current_position += 2 # Move past the starting index and '..'
            ending_index = self.tokens[self.current_position].value # Get the ending index
            self.current_position += 1 # Move past the ending index
        else:
            ending_index = self.tokens[self.current_position].value # Get the ending index
            self.current_position += 1 # Move past the ending index

        # Parsing everything inside the loop
        around_node = AROUNDnode(variable, ending_index, starting_index)
        current_nodes = self.nodes # Temporarily store the current list of nodes
        self.nodes = [] # Create a new list for nodes inside the loop

        while self.current_position < len(self.tokens) and self.tokens[self.current_position].type != "ROLL":
            self.parse_statement()

        around_node.children = self.nodes # Add the parsed nodes to the around_node
        self.nodes = current_nodes # Restore the original nodes list
        self.nodes.append(around_node) # Adding the children to the AST

        # Parsing the ROLL token
        self.parse_roll()

    def parse_roll(self):
        self.current_position += 1 # Skipping the token
        
        roll_node = ROLLnode()
        self.nodes.append(roll_node)

    def parse_back(self):
        self.current_position += 1 # Skipping the token
        variable_name = self.tokens[self.current_position].value # Get the variable name
        self.current_position += 1 # Move past the variable name

        back_node = BACKnode(variable_name)
        self.nodes.append(back_node)

    def parse_load(self):
        self.current_position += 1
        variable_name = self.tokens[self.current_position].value
        self.current_position += 1

        load_node = LOADnode(variable_name)
        self.nodes.append(load_node)
    
    def parse_fnc(self):
        self.current_position += 1 # Move past the "FUNCTION" token
        function_type = self.tokens[self.current_position].value # Get the function type
        self.current_position += 1 # Move past the function type
        function_name = self.tokens[self.current_position].value # Get the function name
        self.current_position += 1 # Move past the function name
        if self.tokens[self.current_position].type == "COLON": # Check for the ':' token
            self.current_position += 1 # Move past the ':' token
        else:
            raise JoshLangError(f"Expected ':' after function name, got '{self.tokens[self.current_position].value}'", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)

        # Parsing the arguments
        arguments = {}
        while self.current_position < len(self.tokens) and self.tokens[self.current_position].type != "COLON":
            argument_type = self.tokens[self.current_position].value # Get the argument type
            self.current_position += 1 # Move past the argument type
            argument_name = self.tokens[self.current_position].value # Get the argument name
            self.current_position += 1 # Move past the argument name
            arguments[argument_name] = argument_type # Add the argument to the dictionary
            if self.current_position < len(self.tokens) and self.tokens[self.current_position].type == "COMMA":
                self.current_position += 1 # Move past the ',' token:

        # Parsing the function body
        function_node = FNCnode(function_type, function_name, arguments)
        current_nodes = self.nodes # Temporarily store the current list of nodes
        self.nodes = [] # Create a new list for nodes inside the function

        while self.current_position < len(self.tokens) and self.tokens[self.current_position].type != "END":
            self.parse_statement()

        function_node.body = self.nodes # Add the parsed nodes to the function_node
        self.nodes = current_nodes
        self.nodes.append(function_node) # Add the function_node to the AST

        # Parsing the END token
        self.parse_end()

    def parse_return(self):
        self.current_position += 1 # Move past the "RETURN" token
        value = self.tokens[self.current_position].value # Get the return value
        return_node = RETURNnode(value)
        self.nodes.append(return_node)

    def parse_call(self):
        function_name = self.tokens[self.current_position].value # Get the function name
        self.current_position += 2 # Move past the function name and ":" token

        # Parsing the arguments
        arguments = []
        while self.current_position < len(self.tokens) and self.tokens[self.current_position].type != "COLON":
            argument = self.tokens[self.current_position].value # Get the argument
            arguments.append(argument)
            self.current_position += 1
            if self.current_position < len(self.tokens) and self.tokens[self.current_position].type == "COMMA":
                self.current_position += 1

        call_node = CALLnode(function_name, arguments)
        return call_node
        
class JoshLangTranspiler:
    def __init__(self, ast):
        self.ast = ast
        self.cpp_code = ""

    def transpile(self):

        # Write includes and start of main function
        self.cpp_code += "#include <iostream>\n#include <string>\n#include <vector>\n#include <fstream>\n#include <sstream>\n#include <algorithm>\n#include <random>\n#include <chrono>\n#include <map>\n#include <cstdint>\n\n"
        
        # We will then transpile the function definitions (we need the types)
        for node in self.ast:
            if node.type == "FUNC":
                self.transpile_node(node)

        self.cpp_code += "int main() {\n"
        self.cpp_code += "std::map<std::string, int8_t> backups;\n"

        # Then transpile the rest of the nodes
        for node in self.ast:
            if node.type != "FUNC":
                self.transpile_node(node)

        self.cpp_code += "\nstd::cin.get();\nreturn 0;\n}"
        return self.cpp_code

    def transpile_node(self, node):
        if node.type == "RUN":
            self.transpile_RUNnode(node)
        elif node.type == "DEC":
            self.transpile_DECnode(node)
        elif node.type == "OUT":
            self.transpile_OUTnode(node)
        elif node.type == "IF":
            self.transpile_IFnode(node)
        elif node.type == "END":
            self.transpile_ENDnode(node)
        elif node.type == "SET":
            self.transpile_SETnode(node)
        elif node.type == "AROUND":
            self.transpile_AROUNDnode(node)
        elif node.type == "ROLL":
            self.transpile_ROLLnode(node)
        elif node.type == "BACK":
            self.transpile_BACKnode(node)
        elif node.type == "LOAD":
            self.transpile_LOADnode(node)
        elif node.type == "FUNC":
            self.transpile_FNCnode(node)
        elif node.type == "RETURN":
            self.transpile_RETURNnode(node)
        elif node.type == "CALL":
            self.transpile_CALLnode(node)
        else:
            raise Exception(f"Invalid node type: {node.type}")

    def transpile_RUNnode(self, node):
        self.cpp_code += f"for (int run = 0; run < {node.times_to_run}; run++) {{\n"

    def transpile_DECnode(self, node):
        print(node)
        cpp_type = type_dic[node.variable_type]
        const_str = "const " if node.is_constant else ""
        array_str = f"[{node.variable_value}]" if node.is_array else ""
        
        # Check if variable_value is a CALLnode and handle accordingly
        if isinstance(node.variable_value, CALLnode):
            call_node = node.variable_value
            args_str = ', '.join(call_node.args)
            value_str = f" = {call_node.function_name}({args_str})"
        else:
            value_str = f" = {node.variable_value}" if not node.is_array else ""
        
        if node.is_array and node.array_values is not None:
            value_str = " = {" + ", ".join(node.array_values) + "}"
        
        self.cpp_code += f"{const_str}{cpp_type} {node.variable_name}{array_str}{value_str};\n"

    
    def transpile_SETnode(self, node):
        if node.target_is_array:
            self.cpp_code += f"{node.target}[{node.target_array_index}] = {node.value};\n"
        else:
            self.cpp_code += f"{node.target} = {node.value};\n"

    def transpile_OUTnode(self, node):
        if node.is_array:
            self.cpp_code += f"std::cout << {node.variable_name}[{node.array_index}] << std::endl;\n"
        else:
            self.cpp_code += f"std::cout << {node.variable_name} << std::endl;\n"

    def transpile_IFnode(self, node):
        self.cpp_code += f"if ({node.condition.left} {node.condition.operator} {node.condition.right}) {{\n"
        for child in node.children:
            self.transpile_node(child)

    def transpile_ENDnode(self, node):
        self.cpp_code += "}\n"

    def transpile_AROUNDnode(self, node):
        self.cpp_code += f"for (int {node.variable} = {node.start_index}; {node.variable} < {node.times_to_run}; {node.variable}++) {{\n" 
        for child in node.children:
            self.transpile_node(child)

    def transpile_ROLLnode(self, node):
        self.cpp_code += "}\n"

    def transpile_BACKnode(self, node):
        # Backing up the state of the variable
        self.cpp_code += f"backups[\"{node.variable_name}\"] = {node.variable_name};\n"
    
    def transpile_LOADnode(self, node):
        # Restoring the state of the variable
        self.cpp_code += f"{node.variable_name} = backups[\"{node.variable_name}\"];\n"

    def transpile_FNCnode(self, node):
        function_type = node.function_type 
        function_name = node.function_name
        arguments = node.args
        function_body = node.body
        
        # Creating the function header
        function_type = type_dic[function_type] # Converting the type to C++ type    
        self.cpp_code += f"{function_type} {function_name}("
        for argument_name, argument_type in arguments.items():
            argument_type = type_dic[argument_type] # Converting the type to C++ type
            self.cpp_code += f"{argument_type} {argument_name}, "
        self.cpp_code = self.cpp_code[:-2] + ") {\n" # Remove the last comma and space and add the closing bracket

        # Adding the function body
        for child in function_body:
            self.transpile_node(child)

        # Adding the closing bracket
        self.cpp_code += "}\n"

    def transpile_RETURNnode(self, node):
        self.cpp_code += f"return {node.value};\n"

    def transpile_CALLnode(self, node):
        self.cpp_code += f"{node.function_name}("
        for argument in node.args:
            self.cpp_code += f"{argument}, "
        self.cpp_code = self.cpp_code[:-2] + ");\n" # Remove the last comma and space and add the closing bracket

def compile(file) -> None:
    with open(file, "r") as file:
        source_code = file.read()
        
    lexer = JoshLangLexer(source_code)
    tokens = lexer.tokenize()
    print(tokens)
    parser = JoshLangParser(tokens)
    ast = parser.parse() # Abstract Syntax Tree
    transpiler = JoshLangTranspiler(ast)
    cpp_code = transpiler.transpile() 
    
    with open(r"C:\Users\jizos\Documents\Programming\Python\JoshLang\JoshLang.cpp", "w") as file_cpp:
        file_cpp.write(cpp_code)

    os.system("g++ JoshLang.cpp -o JoshLang.exe")
    os.system("JoshLang.exe")

if __name__ == "__main__":
    compile(r"C:\Users\jizos\Documents\Programming\Python\JoshLang\Test.josh")
