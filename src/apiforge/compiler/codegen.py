"""
Phase 2 — Django Model Code Generator.

Translates the parsed resource dictionary into valid Django models.py code.
"""

import os
from pathlib import Path


def generate_django_model(parsed_data: dict) -> str:
    """Translate parsed DSL dictionary into Django models.py source code.

    Args:
        parsed_data: Dictionary representing the resource, e.g.:
            {
                "resource": "Product",
                "fields": [{"name": "name", "type": "string"}]
            }

    Returns:
        String of Python source code.
    """
    resource_name = parsed_data["resource"]
    fields = parsed_data["fields"]

    # Generate the class header
    lines = [
        "from django.db import models",
        "",
        "",
        f"class {resource_name}(models.Model):",
    ]

    # Generate each field line
    for field in fields:
        name = field["name"]
        field_type = field["type"]

        if field_type == "string":
            django_field = "models.CharField(max_length=255)"
        else:
            raise ValueError(f"Unsupported field type: '{field_type}'")

        lines.append(f"    {name} = {django_field}")

    # Add spacing
    lines.append("")

    # Generate __str__ method (good Django practice)
    # We look for a 'name' field to print, or default to the first field
    str_field = "pk"
    field_names = [f["name"] for f in fields]
    if "name" in field_names:
        str_field = "name"
    elif field_names:
        str_field = field_names[0]

    lines.extend([
        "    def __str__(self):",
        f"        return str(self.{str_field})",
        "",
    ])

    return "\n".join(lines)


def write_generated_code(source_code: str, output_dir: str = "generated") -> str:
    """Write generated Python code to generated/models.py.

    Creates the output directory if it does not exist.
    """
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    file_path = out_path / "models.py"
    file_path.write_text(source_code)

    return str(file_path.absolute())
