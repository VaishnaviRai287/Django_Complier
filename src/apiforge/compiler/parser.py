"""
Phase 5 — LL(1) Recursive Descent Parser.

Parses a stream of Lexer tokens into a type-safe AST representation.
"""

from pathlib import Path
from typing import List

from apiforge.compiler.lexer import Lexer, Token, TokenType
from apiforge.compiler.ast import ResourceNode, FieldNode, SchemaNode
from apiforge.compiler.semantic import SemanticAnalyzer


class Parser:
    """Parses a list of Tokens into an AST representation using LL(1) logic."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def _peek(self) -> Token:
        """Inspect the current token without consuming it."""
        return self.tokens[self.current]

    def _previous(self) -> Token:
        """Return the token just consumed."""
        return self.tokens[self.current - 1]

    def _is_at_end(self) -> bool:
        """Check if parser has reached the end of the token stream."""
        return self._peek().type == TokenType.EOF

    def _advance(self) -> Token:
        """Consume and return the current token, advancing the pointer."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check(self, type_: TokenType) -> bool:
        """Check if the current token matches the expected type."""
        if self._is_at_end():
            return False
        return self._peek().type == type_

    def _consume(self, type_: TokenType, error_message: str) -> Token:
        """Assert the current token matches type, consume it, or throw SyntaxError."""
        if self._check(type_):
            return self._advance()
        
        token = self._peek()
        raise ValueError(f"Syntax error on line {token.line}: {error_message} (Got: '{token.value}')")

    def parse(self) -> SchemaNode:
        """Parse the token stream into a SchemaNode AST."""
        resources = []
        while not self._is_at_end():
            resources.append(self._parse_resource())
        return SchemaNode(resources)

    def _parse_resource(self) -> ResourceNode:
        """Parse a single resource declaration: 'resource Name { ... }'."""
        resource_token = self._consume(TokenType.RESOURCE, "Expected keyword 'resource'")
        name_token = self._consume(TokenType.IDENTIFIER, "Expected resource identifier name")
        self._consume(TokenType.LBRACE, "Expected '{' to start resource body")

        fields = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            fields.append(self._parse_field())

        self._consume(TokenType.RBRACE, "Expected '}' to close resource body")
        return ResourceNode(name_token.value, fields, resource_token.line)

    def _parse_field(self) -> FieldNode:
        """Parse a single field or relation definition."""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected field name identifier")
        
        if self._check(TokenType.BELONGS_TO):
            self._advance()  # consume belongs_to
            target_token = self._consume(TokenType.IDENTIFIER, "Expected relation target identifier name")
            return FieldNode(name_token.value, "belongs_to", name_token.line, target=target_token.value)
        
        type_token = self._consume(TokenType.IDENTIFIER, "Expected field type identifier")
        return FieldNode(name_token.value, type_token.value, name_token.line)


def parse_api_file(file_path: str) -> dict:
    """Parse a .api file and return its dictionary representation for backend codegen.

    Args:
        file_path: Path to the .api file.

    Returns:
        Compatible dictionary with 'resource' name and 'fields' list.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.suffix == ".api":
        raise ValueError(f"Expected .api file, got: {path.suffix}")

    content = path.read_text()

    # 1. Run Lexical Analysis
    lexer = Lexer(content)
    tokens = lexer.tokenize()

    # 2. Run Syntax Analysis
    parser = Parser(tokens)
    ast_root = parser.parse()

    # 3. Run Semantic Analysis Pass
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast_root)

   # 4. Export AST using the compatibility bridge
    return ast_root.to_dict()


def parse_to_json(file_path: str) -> str:
    """Parse a .api file and return formatted JSON string for CLI compatibility."""
    import json
    result = parse_api_file(file_path)
    return json.dumps(result, indent=4)
