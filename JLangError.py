class JoshLangError(Exception):
    def __init__(self, message, line_num=None, char_pos=None):
        super().__init__(message)  # Call to base Exception class, useful for built-in exception handling
        self.message = message
        self.line_num = line_num
        self.char_pos = char_pos

    def __str__(self):
        location = ""
        if self.line_num is not None and self.char_pos is not None:
            location = f" at line {self.line_num}, char {self.char_pos}"
        return f"{self.message}{location}"

