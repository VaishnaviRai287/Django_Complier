"""
Phase 5 — Abstract Syntax Tree (AST) Node definitions.
"""

from typing import List


class ASTNode:
    """Base class for all AST nodes in the compilation tree."""
    pass


class FieldNode(ASTNode):
    """Represents a single field definition, e.g., 'name string'."""

    def __init__(self, name: str, type_: str, line: int, target: str = None):
        self.name = name
        self.type = type_
        self.line = line
        self.target = target 

    def to_dict(self) -> dict:
        """Serializes the field node into a compatible dictionary structure."""
        result = {"name": self.name, "type": self.type}
        if self.target:
           result["target"] = self.target
        return result


class ResourceNode(ASTNode):
    """Represents a full resource definition, e.g., 'resource Product { ... }'."""

    def __init__(self, name: str, fields: List[FieldNode], line: int):
        self.name = name
        self.fields = fields
        self.line = line

    def to_dict(self) -> dict:
        """Serializes the resource node into a compatible dictionary structure."""
        return {
            "resource": self.name,
            "fields": [field.to_dict() for field in self.fields]
        }

class SchemaNode(ASTNode):
    """Represents a complete APIForge program containing multiple resources."""

    def __init__(self, resources: List[ResourceNode]):
        self.resources = resources

    def to_dict(self) -> dict:
        """Serializes all resources into a dictionary bridge."""
        return {"resources": [r.to_dict() for r in self.resources]}
