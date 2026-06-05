"""
Phase 2 — Code Generator Tests.

Verifies translation of parsed dictionary to Django model code.
"""

import pytest
from apiforge.compiler.codegen import generate_django_model, write_generated_code


class TestGenerateDjangoModel:
    """Test translating parsed DSL schemas to Django models."""

    def test_generates_basic_django_model(self):
        """A simple resource with a string field should yield CharField."""
        parsed_data = {
            "resource": "Product",
            "fields": [{"name": "name", "type": "string"}]
        }

        code = generate_django_model(parsed_data)

        # Assert correct imports & classes
        assert "from django.db import models" in code
        assert "class Product(models.Model):" in code
        assert "name = models.CharField(max_length=255)" in code
        assert "def __str__(self):" in code
        assert "return str(self.name)" in code

    def test_unsupported_field_type_raises_error(self):
        """Types we haven't implemented yet (like int) should raise ValueError."""
        parsed_data = {
            "resource": "Product",
            "fields": [{"name": "stock", "type": "integer"}]
        }

        with pytest.raises(ValueError, match="Unsupported field type: 'integer'"):
            generate_django_model(parsed_data)

    def test_str_method_defaults_to_first_field(self):
        """If there is no 'name' field, __str__ should print the first field."""
        parsed_data = {
            "resource": "User",
            "fields": [
                {"name": "username", "type": "string"},
                {"name": "title", "type": "string"}
            ]
        }

        code = generate_django_model(parsed_data)
        assert "return str(self.username)" in code


class TestWriteGeneratedCode:
    """Test file writing logic."""

    def test_creates_directory_and_writes_file(self, tmp_path):
        """Must create directories as needed and write models.py."""
        code_content = "class MockModel:\n    pass\n"
        out_dir = tmp_path / "custom_gen"

        file_path = write_generated_code(code_content, output_dir=str(out_dir))

        assert out_dir.exists()
        assert out_dir.is_dir()
        
        written_file = out_dir / "models.py"
        assert written_file.exists()
        assert written_file.read_text() == code_content
