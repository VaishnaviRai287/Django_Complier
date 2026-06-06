"""
Phase 5 — Lexer and Parser frontend tests.
"""

import pytest
from apiforge.compiler.lexer import Lexer, Token, TokenType
from apiforge.compiler.parser import Parser, parse_api_file


class TestLexer:
    """Test scanner lexical analysis correctness."""

    def test_tokenizes_simple_resource(self):
        source = "resource Product {\n    name string\n}"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        # Expected: resource, Product, {, name, string, }, EOF
        assert len(tokens) == 7
        assert tokens[0].type == TokenType.RESOURCE
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == "Product"
        assert tokens[2].type == TokenType.LBRACE
        assert tokens[3].type == TokenType.IDENTIFIER
        assert tokens[3].value == "name"
        assert tokens[4].type == TokenType.IDENTIFIER
        assert tokens[4].value == "string"
        assert tokens[5].type == TokenType.RBRACE
        assert tokens[6].type == TokenType.EOF

    def test_lexical_error(self):
        source = "resource Product @ {\n}"
        lexer = Lexer(source)
        with pytest.raises(ValueError, match="Lexical error: Unexpected character '@' on line 1"):
            lexer.tokenize()


class TestParser:
    """Test LL(1) syntax grammar rules parsing and diagnostic errors."""

    def test_syntax_error_missing_brace(self):
        tokens = [
            Token(TokenType.RESOURCE, "resource", 1),
            Token(TokenType.IDENTIFIER, "Product", 1),
            Token(TokenType.EOF, "", 1),
        ]
        parser = Parser(tokens)
        with pytest.raises(ValueError, match="Syntax error on line 1: Expected '{' to start resource body"):
            parser.parse()

    def test_syntax_error_invalid_field(self):
        tokens = [
            Token(TokenType.RESOURCE, "resource", 1),
            Token(TokenType.IDENTIFIER, "Product", 1),
            Token(TokenType.LBRACE, "{", 1),
            Token(TokenType.IDENTIFIER, "name", 2),
            Token(TokenType.RBRACE, "}", 3),
            Token(TokenType.EOF, "", 3),
        ]
        parser = Parser(tokens)
        with pytest.raises(ValueError, match="Syntax error on line 3: Expected field type identifier"):
            parser.parse()


class TestIntegrationFrontend:
    """Verify that serialization matches original dictionary structures exactly."""

    def test_ast_converts_to_compatible_dict(self, tmp_path):
        api_file = tmp_path / "test.api"
        api_file.write_text("resource Item {\n    id integer\n    title string\n}\n")

        result = parse_api_file(str(api_file))

        assert result["resource"] == "Item"
        assert len(result["fields"]) == 2
        assert result["fields"][0] == {"name": "id", "type": "integer"}
        assert result["fields"][1] == {"name": "title", "type": "string"}
