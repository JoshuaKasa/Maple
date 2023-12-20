import re

from MapleError import MapleError

class Token:
    def __init__(self, type_, value, line_num, char_pos):
        self.type = type_
        self.value = value
        self.line_num = line_num
        self.char_pos = char_pos

    def __repr__(self):
        return f"Token({repr(self.type)}, {repr(self.value)}, {repr(self.line_num)}, {repr(self.char_pos)})"

class MapleLexer:
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
            ("STRING", r"\bstr\b"), # String keyword
            ("FLOAT32", r"\bf32\b"), # 32-bit float keyword
            ("FLOAT64", r"\bf64\b"), # 64-bit float keyword
            ("CHAR", r"\bchar\b"), # Character keyword
            ("EMPTY", r"\bempty\b"), # No return
            ("TRUE", r"\btrue\b"), # True keyword
            ("FALSE", r"\bfalse\b"), # False keyword
            ("OUT", r"\bout\b"), # Output keyword
            ("IF", r"\bif\b"), # If keyword            ("END", r"\bend\b"), # End keyword (end of if statement)
            ("ELSE", r"\belse\b"), # Else keyword
            ("ELIF", r"\belif\b"), # Elif keyword
            ("END", r"\bend\b"), # End keyword (end of if statement)
            ("LOOP", r"\bloop\b"), # Loop keyword (for loops)
            ("ROLL", r"\broll\b"), # Roll keyword (end of for loop)
            ("BACK", r"\bback\b"), # Back keyword (save current variable value)
            ("LOAD", r"\bload\b"), # Load keyword (load saved variable value)
            ("LIB", r"\blib @\w+"), # Library keyword (import libraries)
            ("LIBACCESS", r"@(\w+)::"), # Library access keyword (access library namespace)
            ("INIT", r"\binit @\w+"), # Init keyword (initialize library namespace)
            ("RANGE", r"([A-Za-z0-9_]+|\d+(\.\d*)?)\.\.([A-Za-z0-9_]+|\d+(\.\d*)?)"), # Range expression
            ("ADD", r"\badd\b"), # Add keyword (add to variable)
            ("SUB", r"\bsub\b"), # Subtract keyword (subtract from variable)
            ("MUL", r"\bmul\b"), # Multiply keyword (multiply variable)
            ("DIV", r"\bdiv\b"), # Divide keyword (divide variable)
            ("MOD", r"\bmod\b"), # Modulo keyword (modulo variable)
            ("FUNC", r"\bfnc\b"), # Function keyword
            ("RETURN", r"\brtn\b"), # Return keyword
            ("GREATER_EQUAL", r">="), # Greater than or equal to operator
            ("LESS_EQUAL", r"<="), # Less than or equal to operator
            ("NOT_EQUAL", r"!="), # Not equal operator
            ("EQUAL", r"=="), # Equal operator
            ("GREATER", r">"), # Greater than operator
            ("LESS", r"<"), # Less than operator
            ("ARROW", r"->"), # Array assign operator
            ("INSIDE", "=>" ), # Inside variable operator
            ("COMMA", r","), # Comma
            ("COLON", r":"), # Colon
            ("DOTDOT", r"\.\."), # Dot dot operator, used for ranges
            ("LEFT_PAREN", r"\("), # Left parenthesis
            ("LEFT_SQR_BRACKET", r"\["), # Left square bracket
            ("RIGHT_SQR_BRACKET", r"\]"), # Right square bracket
            ("LEFT_CRLY_BRACKET", r"\{"), # Left curly bracket
            ("RIGHT_CRLY_BRACKET", r"\}"), # Right curly bracket
            ("COMPARISON", r"\b==\b"), # Equal comparison operator
            ("COMMENT" , r"//.*"), # Comment

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
                raise MapleError("Illegal character '%s'" % self.source_code[self.current_position], line_num, self.current_position)
                self.current_position += 1

        return self.tokens

