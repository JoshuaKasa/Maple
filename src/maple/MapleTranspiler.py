from MapleTypes import *

import MapleParser

class MapleTranspiler:
    def __init__(self, ast, is_library=False):
        self.ast = ast
        self.cpp_code = ""
        self.namesapce = ""
        self.is_library = is_library

    def transpile(self):

        # Write includes and start of main function
        self.cpp_code += "#include <iostream>\n#include <string>\n#include <vector>\n#include <fstream>\n#include <sstream>\n#include <algorithm>\n#include <random>\n#include <chrono>\n#include <map>\n#include <cstdint>\n\n"
        
        # BUT FIRST... let's transpile the function from the imported libraries
        for node in self.ast:
            if node.type == "LIB":
                self.transpile_node(node)

        # Actually, first of all before anything else (for real this time), we need to transpile the namespace
        node = self.ast[0] # The first node is always the namespace
        self.namespace = node.namespace_name # Get the namespace name
        self.transpile_INITnode(node) # Transpile the namespace

        # We will then transpile the function definitions (we need the types)
        for node in self.ast:
            if node.type == "FUNC":
                self.transpile_node(node)

        # Ending the namespace
        self.cpp_code += "}\n" # End of namespace

        # Main function transpilation
        if self.is_library == False: # If we are transpiling a library we don't need a main function
            self.cpp_code += "int main() {\n" 
            self.cpp_code += "std::map<std::string, int8_t> backups;\n"

        # Then transpile the rest of the nodes
        for node in self.ast:
            if node.type != "FUNC" and node.type != "LIB" and node.type != "INIT": # We already transpiled functions, libraries and namespaces
                self.transpile_node(node)
        
        if self.ast[0].type == "RUN":
            self.cpp_code += "}\n" # End of run function

        if self.is_library == False: # If we are transpiling a library we don't need a main function
            self.cpp_code += "\nstd::cin.get();\nreturn 0;\n}\n" # End of main function
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
        elif node.type == "ELSE":
            self.transpile_ELSEnode(node)
        elif node.type == "ELIF":
            self.transpile_ELIFnode(node)
        elif node.type == "END":
            self.transpile_ENDnode(node)
        elif node.type == "SET":
            self.transpile_SETnode(node)
        elif node.type == "LOOP":
            self.transpile_LOOPnode(node)
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
        elif node.type == "EXPRESSION":
            self.transpile_EXPRESSIONnode(node)
        elif node.type == "LIB":
            self.transpile_LIBnode(node)
        elif node.type == "INIT":
            self.transpile_INITnode(node)
        elif node.type == "LIBACCESS":
            self.transpile_LIBACCESSnode(node)
        else:
            raise Exception(f"Invalid node type: {node.type}")
   
    def transpile_LIBACCESSnode(self, node):
        self.cpp_code += f"{node.library_name}::{node.function_name}" + "("
        for argument in node.args:
            self.cpp_code += f"{argument}, "
        self.cpp_code = self.cpp_code[:-2] + ");\n" # Remove the last comma and space and add the closing bracket 

    def transpile_INITnode(self, node):
        self.cpp_code += "namespace " + node.namespace_name + " {\n"

    def transpile_RUNnode(self, node):
        self.cpp_code += f"for (int run = 0; run < {node.times_to_run}; run++) {{\n"

    def transpile_DECnode(self, node):
        print(node)
        cpp_type = type_dic[node.variable_type]
        const_str = "const " if node.is_constant else ""
        array_str = f"[{node.variable_value}]" if node.is_array else ""
        
        # Check if variable_value is a CALLnode and handle accordingly
        if isinstance(node.variable_value, MapleParser.CALLnode):
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

    def transpile_ELSEnode(self, node):
        self.cpp_code += "else {\n"
        for child in node.children:
            self.transpile_node(child)

    def transpile_ELIFnode(self, node):
        self.cpp_code += "else if ({node.condition.left} {node.condition.operator} {node.condition.right}) {{\n"
        for child in node.children:
            self.transpile_node(child)

    def transpile_ENDnode(self, node):
        self.cpp_code += "}\n"

    def transpile_LOOPnode(self, node):
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
        self.cpp_code += f"{self.namespace}::{node.function_name}("
        for argument in node.args:
            self.cpp_code += f"{argument}, "
        self.cpp_code = self.cpp_code[:-2] + ");\n" # Remove the last comma and space and add the closing bracket
    
    def transpile_EXPRESSIONnode(self, node):
        print(node)
        if node.store_variable is not None:
            self.cpp_code += f"{node.store_variable} = {node.left} {node.operator} {node.right};\n"
        else:
            self.cpp_code += f"{node.left} {node.operator}= {node.right};\n"
    
    def transpile_LIBnode(self, node):
        self.cpp_code += f"#include \"../../../lib/{node.library_name}.hpp\"\n"

