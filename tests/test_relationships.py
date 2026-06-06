"""
Phase 7 — Relationships unit and integration tests.
"""

import pytest
from apiforge.compiler.lexer import Lexer, TokenType
from apiforge.compiler.parser import parse_api_file
from apiforge.compiler.codegen import generate_django_model


class TestRelationships:
    """Test tokenization, parsing, validation, and codegen for relations."""

    def test_tokenizes_belongs_to(self):
        source = "resource Order { customer belongs_to Customer }"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        belongs_token = [t for t in tokens if t.type == TokenType.BELONGS_TO]
        assert len(belongs_token) == 1
        assert belongs_token[0].value == "belongs_to"

    def test_parses_relationships(self, tmp_path):
        api_file = tmp_path / "relations.api"
        api_file.write_text(
            "resource Customer {\n"
            "    name string\n"
            "}\n"
            "resource Order {\n"
            "    customer belongs_to Customer\n"
            "}\n"
        )

        result = parse_api_file(str(api_file))

        assert len(result["resources"]) == 2
        customer = result["resources"][0]
        order = result["resources"][1]

        assert customer["resource"] == "Customer"
        assert order["resource"] == "Order"
        
        relation_field = order["fields"][0]
        assert relation_field["name"] == "customer"
        assert relation_field["type"] == "belongs_to"
        assert relation_field["target"] == "Customer"

    def test_semantic_validator_blocks_invalid_targets(self, tmp_path):
        api_file = tmp_path / "invalid_relation.api"
        api_file.write_text(
            "resource Order {\n"
            "    customer belongs_to NonExistent\n"
            "}\n"
        )

        with pytest.raises(ValueError, match="Unknown relation target 'NonExistent'"):
            parse_api_file(str(api_file))

    def test_generates_django_foreign_keys(self):
        parsed_data = {
            "resources": [
                {
                    "resource": "Customer",
                    "fields": [{"name": "name", "type": "string"}]
                },
                {
                    "resource": "Order",
                    "fields": [{"name": "customer", "type": "belongs_to", "target": "Customer"}]
                }
            ]
        }

        models_code = generate_django_model(parsed_data)
        assert "customer = models.ForeignKey('Customer', on_delete=models.CASCADE)" in models_code
