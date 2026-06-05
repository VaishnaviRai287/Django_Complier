"""
Phase 1 — Simple Resource Parser.

Reads a .api file and extracts resource definitions using regex.
This is intentionally simple — no lexer, no AST, no tokens.
Phase 5 will replace this with proper compiler components.

Why regex for now?
- We only support ONE resource with simple fields
- Regex is good enough for this limited scope
- Building a full lexer/parser before we need one is over-engineering
- We'll feel the pain of regex in Phase 4-5, and THEN we'll refactor
"""

import json
import re
from pathlib import Path


def parse_api_file(file_path: str) -> dict:
    """Parse a .api file and return a dictionary representation.

    Args:
        file_path: Path to the .api file to parse.

    Returns:
        Dictionary with 'resource' name and 'fields' list.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is invalid.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.suffix == ".api":
        raise ValueError(f"Expected .api file, got: {path.suffix}")

    content = path.read_text().strip()

    # Match: resource ResourceName { ... }
    resource_match = re.match(
        r"resource\s+(\w+)\s*\{(.+?)\}",
        content,
        re.DOTALL,
    )

    if not resource_match:
        raise ValueError(
            f"Invalid format. Expected: resource Name {{ field type }}\n"
            f"Got: {content[:100]}"
        )

    resource_name = resource_match.group(1)
    fields_block = resource_match.group(2).strip()

    # Parse each line inside the braces as: field_name field_type
    fields = []
    for line in fields_block.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) != 2:
            raise ValueError(
                f"Invalid field definition: '{line}'\n"
                f"Expected: field_name field_type"
            )

        fields.append({
            "name": parts[0],
            "type": parts[1],
        })

    return {
        "resource": resource_name,
        "fields": fields,
    }


def parse_to_json(file_path: str) -> str:
    """Parse a .api file and return formatted JSON string.

    This is a convenience wrapper around parse_api_file()
    for CLI output.
    """
    result = parse_api_file(file_path)
    return json.dumps(result, indent=4)
