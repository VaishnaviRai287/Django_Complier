"""
Phase 6 — Semantic Analyzer Pass.

Validates parsed AST structures for lexical correctness, casing conventions,
duplicate definitions, and type correctness prior to backend generation.
"""

import difflib
from apiforge.compiler.ast import ResourceNode

VALID_TYPES = {"string", "integer", "decimal", "boolean", "email"}


class SemanticAnalyzer:
    """Analyzes AST nodes to enforce semantic rules of the DSL."""

    def analyze(self, resource: ResourceNode) -> None:
        """Run all semantic analysis rules against the parsed resource AST node."""
        self._validate_resource_name(resource)
        self._validate_empty_resource(resource)
        self._validate_fields(resource)

    def _validate_resource_name(self, resource: ResourceNode) -> None:
        """Enforce that resource names start with an uppercase letter."""
        if not resource.name or not resource.name[0].isupper():
            raise ValueError(
                f"Semantic error on line {resource.line}: "
                f"Resource name '{resource.name}' must start with an uppercase letter."
            )

    def _validate_empty_resource(self, resource: ResourceNode) -> None:
        """Enforce that resources contain at least one field."""
        if not resource.fields:
            raise ValueError(
                f"Semantic error on line {resource.line}: "
                f"Resource '{resource.name}' must define at least one field."
            )

    def _validate_fields(self, resource: ResourceNode) -> None:
        """Enforce field type checking, casing, and uniqueness constraint checks."""
        seen_fields = set()

        for field in resource.fields:
            # 1. Uniqueness constraint check
            if field.name in seen_fields:
                raise ValueError(
                    f"Semantic error on line {field.line}: "
                    f"Duplicate field '{field.name}' defined in resource '{resource.name}'."
                )
            seen_fields.add(field.name)

            # 2. Field casing check (must start with lowercase letter)
            if not field.name or not field.name[0].islower():
                raise ValueError(
                    f"Semantic error on line {field.line}: "
                    f"Field name '{field.name}' must start with a lowercase letter."
                )

            # 3. Type correctness check with spelling corrector recommendations
            if field.type not in VALID_TYPES:
                close_matches = difflib.get_close_matches(field.type, VALID_TYPES, n=1)
                suggestion = f" Did you mean '{close_matches[0]}'?" if close_matches else ""
                raise ValueError(
                    f"Semantic error on line {field.line}: "
                    f"Unknown type '{field.type}'.{suggestion}"
                )
