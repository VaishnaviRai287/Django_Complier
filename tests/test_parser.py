"""
Phase 1 — Parser Tests.

Tests the simple regex parser that reads .api files.
"""

import json
import pytest

from apiforge.compiler.parser import parse_api_file, parse_to_json


class TestParseApiFile:
    """Test the core parsing function."""

    def test_parses_single_field_resource(self, tmp_path):
        """Most basic case: one resource, one field."""
        api_file = tmp_path / "product.api"
        api_file.write_text("resource Product {\n    name string\n}\n")

        result = parse_api_file(str(api_file))

        assert result["resource"] == "Product"
        assert len(result["fields"]) == 1
        assert result["fields"][0]["name"] == "name"
        assert result["fields"][0]["type"] == "string"

    def test_parses_multiple_fields(self, tmp_path):
        """A resource can have more than one field."""
        api_file = tmp_path / "user.api"
        api_file.write_text(
            "resource User {\n"
            "    username string\n"
            "    email string\n"
            "}\n"
        )

        result = parse_api_file(str(api_file))

        assert result["resource"] == "User"
        assert len(result["fields"]) == 2
        assert result["fields"][0]["name"] == "username"
        assert result["fields"][1]["name"] == "email"

    def test_handles_extra_whitespace(self, tmp_path):
        """Parser should handle inconsistent spacing."""
        api_file = tmp_path / "item.api"
        api_file.write_text(
            "resource   Item  {\n"
            "    price   string\n"
            "}\n"
        )

        result = parse_api_file(str(api_file))

        assert result["resource"] == "Item"
        assert result["fields"][0]["name"] == "price"


class TestParseErrors:
    """Test that bad input produces clear errors."""

    def test_file_not_found(self):
        """Missing file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_api_file("nonexistent.api")

    def test_wrong_extension(self, tmp_path):
        """Non-.api files should be rejected."""
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("resource Foo { name string }")

        with pytest.raises(ValueError, match="Expected .api file"):
            parse_api_file(str(bad_file))

    def test_invalid_format(self, tmp_path):
        """Garbage input should raise ValueError."""
        api_file = tmp_path / "bad.api"
        api_file.write_text("this is not valid")

        with pytest.raises(ValueError, match="Invalid format"):
            parse_api_file(str(api_file))

    def test_invalid_field_definition(self, tmp_path):
        """Fields must be exactly: name type."""
        api_file = tmp_path / "bad_field.api"
        api_file.write_text("resource X {\n    just_one_word\n}\n")

        with pytest.raises(ValueError, match="Invalid field definition"):
            parse_api_file(str(api_file))


class TestParseToJson:
    """Test JSON output formatting."""

    def test_produces_valid_json(self, tmp_path):
        """Output should be parseable JSON."""
        api_file = tmp_path / "product.api"
        api_file.write_text("resource Product {\n    name string\n}\n")

        json_output = parse_to_json(str(api_file))
        parsed = json.loads(json_output)

        assert parsed["resource"] == "Product"
        assert len(parsed["fields"]) == 1
