"""TMDL Lexical Analyzer

This module implements a lexer for the Tabular Model Definition Language (TMDL).
TMDL is an indentation-based language used to define tabular models in Microsoft
Analysis Services.

Key syntax rules:
- Object names must be quoted with single quotes if they contain special characters
- Properties are specified with colon delimiter (key: value)
- Default properties use equals delimiter (measure x = ...)
- Indentation defines parent-child relationships
- Triple-slash comments (///) are used for descriptions
- String values support double-quote escaping with doubled quotes

Example TMDL:
    table Sales
        column Quantity
            dataType: int64
            isHidden
            sourceColumn: Quantity

        measure 'Sales Amount' =
            var result = SUMX(...)
            return result
            formatString: "$ #,##0"
"""

from enum import Enum, auto
from typing import List, Optional, NamedTuple


class TokenType(Enum):
    """Token types for TMDL lexical analysis"""

    INDENT = auto()  # Increased indentation level
    DEDENT = auto()  # Decreased indentation level
    NEWLINE = auto()  # Line break
    IDENTIFIER = auto()  # Table/column/measure names
    COLON = auto()  # Property delimiter ':'
    EQUALS = auto()  # Default property delimiter '='
    STRING = auto()  # Quoted string value
    NUMBER = auto()  # Integer or decimal
    BOOL = auto()  # true/false
    DESCRIPTION = auto()  # /// Description comment
    COMMENT = auto()  # Regular comment
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    COMMA = auto()  # ,
    EOF = auto()  # End of file


class Token(NamedTuple):
    """Represents a lexical token with type, value and position"""

    type: TokenType
    value: str
    line: int
    column: int


class LexerError(Exception):
    """Custom exception for lexer errors"""

    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{message} at line {line}, column {column}")


class TmdlLexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0  # Current position in text
        self.line = 1  # Current line number
        self.column = 1  # Current column number
        self.indent_stack = [0]  # Stack of indentation levels
        self.tokens: List[Token] = []
        self.current_indent = 0  # Current line's indentation

    def peek(self, n: int = 1) -> str:
        """Look ahead n characters without advancing position"""
        if self.pos + n <= len(self.text):
            return self.text[self.pos : self.pos + n]
        return ""

    def advance(self, n: int = 1) -> None:
        """Advance position by n characters"""
        for _ in range(n):
            if self.pos < len(self.text):
                if self.text[self.pos] == "\n":
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

    def skip_whitespace(self) -> None:
        """Skip whitespace except for newlines and indentation"""
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            if self.text[self.pos] == "\n":
                return
            self.advance()

    def handle_indentation(self) -> None:
        """Process indentation changes at the start of a line"""
        if self.pos >= len(self.text):
            # Add DEDENT tokens at EOF if needed
            while len(self.indent_stack) > 1:
                self.tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))
                self.indent_stack.pop()
            return

        # Count spaces for indentation
        spaces = 0
        while self.pos < len(self.text) and self.text[self.pos] in " \t":
            if self.text[self.pos] == "\t":
                spaces += 8 - (spaces % 8)  # Convert tabs to spaces
            else:
                spaces += 1
            self.advance()

        if self.pos < len(self.text) and self.text[self.pos] != "\n":
            if spaces > self.indent_stack[-1]:
                self.indent_stack.append(spaces)
                self.tokens.append(
                    Token(TokenType.INDENT, " " * spaces, self.line, self.column)
                )
            while spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))
            if spaces != self.indent_stack[-1]:
                raise LexerError("Inconsistent indentation", self.line, self.column)

    def scan_identifier(self) -> Token:
        """Scan an identifier or keyword"""
        start_pos = self.pos
        start_col = self.column

        # Check for quoted identifier
        if self.text[self.pos] == "'":
            self.advance()  # Skip opening quote
            value = ""
            while self.pos < len(self.text):
                if self.text[self.pos] == "'":
                    if self.peek(2) == "''":  # Escaped single quote
                        value += "'"
                        self.advance(2)
                    else:
                        self.advance()  # Skip closing quote
                        break
                else:
                    value += self.text[self.pos]
                    self.advance()
            return Token(TokenType.IDENTIFIER, value, self.line, start_col)

        # Unquoted identifier
        # First character can be alpha, underscore, or dot
        if not self.text[self.pos] == "'":
            if not (self.text[self.pos].isalpha() or self.text[self.pos] in "_."):
                raise LexerError(
                    f"Invalid identifier start: {self.text[self.pos]}",
                    self.line,
                    self.column,
                )
            self.advance()

        # Rest can include alphanumeric, underscore, dot, hyphen
        while self.pos < len(self.text) and (
            self.text[self.pos].isalnum() or self.text[self.pos] in "_-."
        ):
            self.advance()

        value = self.text[start_pos : self.pos]

        # Check for boolean values
        if value.lower() in ("true", "false"):
            return Token(TokenType.BOOL, value.lower(), self.line, start_col)

        return Token(TokenType.IDENTIFIER, value, self.line, start_col)

    def scan_number(self) -> Token:
        """Scan a numeric literal including version numbers"""
        start_pos = self.pos
        start_col = self.column

        # Handle negative numbers
        if self.text[self.pos] == "-":
            self.advance()

        # Handle full version numbers like 2.103.661.0
        while self.pos < len(self.text):
            if self.text[self.pos].isdigit():
                self.advance()
            elif self.text[self.pos] == "." and self.peek(2)[1].isdigit():
                # Continue for version numbers with multiple dots
                self.advance()
            else:
                break

        return Token(
            TokenType.NUMBER, self.text[start_pos : self.pos], self.line, start_col
        )

    def scan_string(self) -> Token:
        """Scan a double-quoted string literal"""
        start_col = self.column
        self.advance()  # Skip opening quote
        value = ""

        while self.pos < len(self.text):
            if self.text[self.pos] == '"':
                if self.peek(2) == '""':  # Escaped double quote
                    value += '"'
                    self.advance(2)
                else:
                    self.advance()  # Skip closing quote
                    break
            else:
                value += self.text[self.pos]
                self.advance()

        return Token(TokenType.STRING, value, self.line, start_col)

    def scan_description(self) -> Optional[Token]:
        """Scan a /// description comment"""
        if self.peek(3) != "///":
            return None

        start_col = self.column
        self.advance(3)  # Skip ///

        # Skip one space after /// if present
        if self.pos < len(self.text) and self.text[self.pos] == " ":
            self.advance()

        # Collect description text until end of line
        value = ""
        while self.pos < len(self.text) and self.text[self.pos] != "\n":
            value += self.text[self.pos]
            self.advance()

        return Token(TokenType.DESCRIPTION, value.strip(), self.line, start_col)

    def tokenize(self) -> List[Token]:
        """Convert input text into a list of tokens"""
        self.tokens = []

        while self.pos < len(self.text):
            # Handle indentation at start of line
            if self.column == 1:
                self.handle_indentation()

            # Skip whitespace
            self.skip_whitespace()

            # Check for EOF
            if self.pos >= len(self.text):
                break

            char = self.text[self.pos]

            # Handle different characters
            if char == "\n":
                self.tokens.append(
                    Token(TokenType.NEWLINE, "\n", self.line, self.column)
                )
                self.advance()
                continue

            if char == "#":  # Skip comments
                while self.pos < len(self.text) and self.text[self.pos] != "\n":
                    self.advance()
                continue

            if char == "/":  # Check for description
                desc_token = self.scan_description()
                if desc_token:
                    self.tokens.append(desc_token)
                    continue

            if char == ":":
                self.tokens.append(Token(TokenType.COLON, ":", self.line, self.column))
                self.advance()
                continue

            if char == "=":
                self.tokens.append(Token(TokenType.EQUALS, "=", self.line, self.column))
                self.advance()
                continue

            if char == '"':
                self.tokens.append(self.scan_string())
                continue

            if char == "[":
                self.tokens.append(
                    Token(TokenType.LBRACKET, "[", self.line, self.column)
                )
                self.advance()
                continue

            if char == "]":
                self.tokens.append(
                    Token(TokenType.RBRACKET, "]", self.line, self.column)
                )
                self.advance()
                continue

            if char == "(":
                self.tokens.append(Token(TokenType.LPAREN, "(", self.line, self.column))
                self.advance()
                continue

            if char == ")":
                self.tokens.append(Token(TokenType.RPAREN, ")", self.line, self.column))
                self.advance()
                continue

            if char == ",":
                self.tokens.append(Token(TokenType.COMMA, ",", self.line, self.column))
                self.advance()
                continue

            # Identifier can start with alpha, underscore, dot, or single quote
            if char in ("'", "_", ".") or char.isalpha():
                self.tokens.append(self.scan_identifier())
                continue

            if char.isdigit() or (char == "-" and self.peek(2)[1].isdigit()):
                self.tokens.append(self.scan_number())
                continue

            raise LexerError(
                f"Unexpected character: {char} in text {self.text}",
                self.line,
                self.column,
            )

        # Handle any remaining dedents at EOF
        while len(self.indent_stack) > 1:
            self.tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))
            self.indent_stack.pop()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens


def lex_tmdl(text: str) -> List[Token]:
    """Helper function to create lexer and get tokens"""
    lexer = TmdlLexer(text)
    return lexer.tokenize()
