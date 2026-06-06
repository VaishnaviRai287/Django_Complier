"""
Phase 5 — Lexical Analyzer (Scanner).

Converts raw character stream into a stream of structured Tokens.
"""

from enum import Enum, auto
from typing import List


class TokenType(Enum):
    RESOURCE = auto()     # Literal 'resource' keyword
    IDENTIFIER = auto()   # Resource/field names and types
    LBRACE = auto()       # '{'
    RBRACE = auto()       # '}'
    EOF = auto()          # End of file marker


class Token:
    """Represents a single lexical token with source coordinates."""

    def __init__(self, type_: TokenType, value: str, line: int):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line {self.line})"

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value and self.line == other.line


class Lexer:
    """Scans the source code and produces a list of Tokens."""

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.length = len(source)

    def _peek(self) -> str:
        """Look at the current character without consuming it."""
        if self.position >= self.length:
            return ""
        return self.source[self.position]

    def _advance(self) -> str:
        """Consume and return the current character, updating line coordinates."""
        if self.position >= self.length:
            return ""
        char = self.source[self.position]
        self.position += 1
        if char == "\n":
            self.line += 1
        return char

    def tokenize(self) -> List[Token]:
        """Scan the entire source string and return a list of tokens."""
        tokens = []

        while self.position < self.length:
            char = self._peek()

            # 1. Skip whitespace
            if char.isspace():
                self._advance()
                continue

            # 2. Match structural curly braces
            if char == "{":
                tokens.append(Token(TokenType.LBRACE, self._advance(), self.line))
                continue
            if char == "}":
                tokens.append(Token(TokenType.RBRACE, self._advance(), self.line))
                continue

            # 3. Match Words, Identifiers, and Keywords
            if char.isalpha() or char == "_":
                word = ""
                start_line = self.line
                while self._peek().isalnum() or self._peek() == "_":
                    word += self._advance()

                # Distinguish DSL keywords from standard user-defined identifiers
                if word == "resource":
                    tokens.append(Token(TokenType.RESOURCE, word, start_line))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, word, start_line))
                continue

            # 4. Unknown character handling
            raise ValueError(f"Lexical error: Unexpected character '{char}' on line {self.line}")

        # Ensure parser always receives a termination token
        tokens.append(Token(TokenType.EOF, "", self.line))
        return tokens
