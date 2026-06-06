"""
Phase 6 — Semantic validation tests.
"""

import pytest
from apiforge.compiler.ast import ResourceNode, FieldNode
from apiforge.compiler.semantic import SemanticAnalyzer
from apiforge.compiler.parser import parse_api_file


class TestSemanticValidationRules:
    """Test individual semantic validation passes."""

    def setup_method(self):
        self.analyzer = SemanticAnalyzer()

    def test_valid_resource_passes(self):
        # Resource Product { name string }
        ast = ResourceNode("Product", [FieldNode("name", "string", 2)], 1)
        # Should not raise any exception
        self.analyzer.analyze(ast)

    def test_resource_lowercase_name_fails(self):
        ast = ResourceNode("product", [FieldNode("name", "string", 2)], 1)
        with pytest.raises(ValueError, match="Resource name 'product' must start with an uppercase letter"):
            self.analyzer.analyze(ast)

    def test_empty_resource_fields_fails(self):
        ast = ResourceNode("Product", [], 1)
        with pytest.raises(ValueError, match="Resource 'Product' must define at least one field"):
            self.analyzer.analyze(ast)

    def test_duplicate_fields_fails(self):
        ast = ResourceNode(
            "Product",
            [
                FieldNode("name", "string", 2),
                FieldNode("name", "integer", 3),
            ],
            1
        )
        with pytest.raises(ValueError, match="Duplicate field 'name' defined in resource 'Product'"):
            self.analyzer.analyze(ast)

    def test_field_name_uppercase_fails(self):
        ast = ResourceNode("Product", [FieldNode("Name", "string", 2)], 1)
        with pytest.raises(ValueError, match="Field name 'Name' must start with a lowercase letter"):
            self.analyzer.analyze(ast)

    def test_unknown_field_type_with_spelling_suggestion(self):
        ast = ResourceNode("Product", [FieldNode("name", "strng", 2)], 1)
        with pytest.raises(ValueError, match="Unknown type 'strng'. Did you mean 'string'?"):
            self.analyzer.analyze(ast)

    def test_unknown_field_type_without_suggestion(self):
        ast = ResourceNode("Product", [FieldNode("name", "xyz", 2)], 1)
        # xyz is too far from any valid type, so no suggestion is appended
        with pytest.raises(ValueError, match="Unknown type 'xyz'\\.$"):
            self.analyzer.analyze(ast)


class TestIntegrationSemantic:
    """Test semantic analysis end-to-end using file parsers."""

    def test_parser_runs_semantic_pass(self, tmp_path):
        api_file = tmp_path / "test.api"
        # Write duplicate fields in file
        api_file.write_text("resource Product {\n    title string\n    title integer\n}\n")
        
        with pytest.raises(ValueError, match="Duplicate field 'title'"):
            parse_api_file(str(api_file))
