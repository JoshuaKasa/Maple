from MapleError import MapleError
from MapleLexer import MapleLexer
from MapleTranspiler import MapleTranspiler
from MapleTypes import *

import os

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

class LOOPnode(ASTnode):
    def __init__(self, variable, times_to_run, start_index=0):
        super().__init__('LOOP')
        self.variable = variable
        self.start_index = start_index
        self.times_to_run = times_to_run # This can also be thend indexx
        self.children = [] # List of nodes inside the for loop

    def __repr__(self):
        return f"LOOPnode(times_to_run={self.times_to_run})"

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

class EXPRESSIONnode(ASTnode): # If there's no store variable, the value will be stored inside the left variable
    def __init__(self, left, operator, right, store_variable=None):
        super().__init__('EXPRESSION')
        self.left = left
        self.operator = operator
        self.right = right
        self.store_variable = store_variable

    def __repr__(self):
        return f"EXPRESSIONnode(left={self.left}, operator={self.operator}, right={self.right}, store_variable={self.store_variable})"

class LIBnode(ASTnode):
    def __init__(self, library_name, main_function="main"): # The library name is basically the name of the file (hpp)
        super().__init__('LIB')
        self.library_name = library_name
        self.main_function = main_function

    def __repr__(self):
        return f"LIBnode(library_name={self.library_name})"

class INITnode(ASTnode):
    def __init__(self, namespace_name):
        super().__init__('INIT')
        self.namespace_name = namespace_name

    def __repr__(self):
        return f"INITnode(namespace_name={self.namespace_name})"

class LIBACCESSnode(ASTnode):
    def __init__(self, library_name, function_name, args: list):
        super().__init__('LIBACCESS')
        self.library_name = library_name
        self.function_name = function_name
        self.args = args

    def __repr__(self):
        return f"LIBACCESSnode(library_name={self.library_name}, function_name={self.function_name}, args={self.args})"

class MapleParser:
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
        elif token.type == "LOOP":
            self.parse_loop()
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
        elif token.type == "ADD" or token.type == "SUB" or token.type == "MUL" or token.type == "DIV" or token.type == "MOD":
            self.parse_expression()
        elif token.type == "LIB":
            self.parse_lib()
        elif token.type == "INIT":
            self.parse_init()
        elif token.type == "LIBACCESS":
            self.parse_libaccess()
        else:
            self.current_position += 1
   
    def parse_libaccess(self):
        # Formatting is: @library_name::function_name : arg1, arg2 ... argn : (r"@(\w+)::")
        library_name = self.tokens[self.current_position].value.split("@")[1].split("::")[0]
        
        # Parsing function call
        self.parse_call() # This will append the call node to self.nodes

        access_node = LIBACCESSnode(library_name, self.nodes[-1].function_name, self.nodes[-1].args)
        self.nodes.pop() # Removing the call node
        self.nodes.append(access_node)
       
    def parse_init(self):
        if self.current_position != 0: # Error checking
            raise MapleError("INIT must be at the beginning of the file", self.tokens[self.current_position].line_num)
        elif self.current_position + 1 >= len(self.tokens):
            raise MapleError("Expected namespace name", self.tokens[self.current_position].line_num) # Error checking
        namespace_name = self.tokens[self.current_position].value.split("@")[1]
        self.nodes.append(INITnode(namespace_name))
        self.current_position += 1 # Skipping the namespace name

    def parse_lib(self):
        library_name = self.tokens[self.current_position].value.split("@")[1]
        
        # Error checking
        library_path = f"lib/{library_name}.mal"
        absolute_library_path = os.path.abspath(library_path)

        if not os.path.exists(absolute_library_path):
                raise MapleError(f"Library {library_name} does not exist", self.tokens[self.current_position].line_num)
        if library_name in self.symbol_table:
            raise MapleError(f"Library {library_name} already exists", self.tokens[self.current_position].line_num)

        # Transpiling the library into C++ code
        with open(absolute_library_path, "r") as f:
            code = f.read()
        tokens = MapleLexer(code).tokenize()
        nodes = MapleParser(tokens).parse()
        cpp_code = MapleTranspiler(nodes).transpile()

        # Writing the C++ code to a header file
        with open(f"{library_name}.hpp", "w") as f:
            f.write(cpp_code)

        # Adding the library to the symbol table
        self.symbol_table[library_name] = f"{library_name}.hpp"
        self.current_position += 1 # Move past library name

        lib_node = LIBnode(library_name) # Create the LIB node
        self.nodes.append(lib_node) 

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
                raise MapleError(f"Variable {variable_name} already exists", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)
            elif variable_type not in variable_types:  # Invalid variable type 
                raise MapleError(f"Invalid variable type {variable_type}", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)

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
    
    def parse_expression(self):
        op_map = {
            "ADD": "+",
            "SUB": "-",
            "MUL": "*",
            "DIV": "/",
        }
        
        operation = self.tokens[self.current_position].type # Get the operation
        self.current_position += 1 # Move past operation
        left = self.tokens[self.current_position].value
        self.current_position += 1
        right = self.tokens[self.current_position].value
        self.current_position += 1 # Move past right

        assign_to = None
        if self.tokens[self.current_position].type == "INSIDE":
            self.current_position += 1 # Move past 'INSIDE'
            assign_to = self.tokens[self.current_position].value # Get the variable name
            if assign_to not in self.symbol_table:
                raise MapleError(f"Variable {assign_to} does not exist", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)
            self.current_position += 1 # Move past variable name

        expression_node = EXPRESSIONnode(left, op_map[operation], right, assign_to)
        self.nodes.append(expression_node)

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
                raise MapleError(f"Index {target_index} out of range for array {target}", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)

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
                    raise MapleError(f"Index {value_index} out of range for array {value}", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)
            else: # Value is a variable
                value = self.symbol_table[value]["array_values"][int(value)]
        else: # Target is a variable
            value = self.tokens[self.current_position].value
            self.current_position += 1
        
        # Error checking
        if target not in self.symbol_table: # Check if variable is declared
            line_num = self.tokens[self.current_position].line_num
            current_char = self.tokens[self.current_position].char_pos
            raise MapleError(f"Variable '{target}' not declared", line_num, current_char)

        if self.symbol_table[target]["is_constant"]: # Check if variable is constant
            line_num = self.tokens[self.current_position].line_num
            current_char = self.tokens[self.current_position].char_pos
            raise MapleError(f"Cannot set constant variable '{target}' (remember variables are constant by default)", line_num, current_char)

        if self.symbol_table[target]["type"]:
            # Checking if the value is a variable
            if value in self.symbol_table:
                # Checking if the variable types match
                if self.symbol_table[target]["type"] != self.symbol_table[value]["type"]:
                    line_num = self.tokens[self.current_position].line_num
                    current_char = self.tokens[self.current_position].char_pos
                    raise MapleError(f"Cannot set variable '{target}' of type '{self.symbol_table[target]['type']}' to variable '{value}' of type '{self.symbol_table[value]['type']}'", line_num, current_char)
            else:
                # Checking if the value is a number
                if not value.isnumeric():
                    line_num = self.tokens[self.current_position].line_num
                    current_char = self.tokens[self.current_position].char_pos
                    raise MapleError(f"Cannot set variable '{target}' of type '{self.symbol_table[target]['type']}' to '{value}' of type 'NUMBER'", line_num, current_char)


        set_node = SETnode(target, value, target_is_array, target_index)
        self.nodes.append(set_node) # Add the node to the AST

    def parse_out(self):
        self.current_position += 1 # Move past 'OUT'
        variable_name = self.tokens[self.current_position].value # Get the variable name
        self.current_position += 1 # Move past variable name
        
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
    
    def parse_loop(self):
        self.current_position += 1 # Move past "LOOP" token
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
        loop_node = LOOPnode(variable, ending_index, starting_index)
        current_nodes = self.nodes # Temporarily store the current list of nodes
        self.nodes = [] # Create a new list for nodes inside the loop

        while self.current_position < len(self.tokens) and self.tokens[self.current_position].type != "END":
            self.parse_statement()

        loop_node.children = self.nodes # Add the parsed nodes to the loop_node
        self.nodes = current_nodes # Restore the original nodes list
        self.nodes.append(loop_node) # Adding the children to the AST

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
            raise MapleError(f"Expected ':' after function name, got '{self.tokens[self.current_position].value}'", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)

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
        if self.current_position < len(self.tokens) and self.tokens[self.current_position].type == "END":
            self.current_position += 1
        else:
            raise MapleError(f"Expected 'END' after function body, got '{self.tokens[self.current_position].value}'", self.tokens[self.current_position].line_num, self.tokens[self.current_position].char_pos)

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
