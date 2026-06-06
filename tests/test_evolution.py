"""
Phase 13 — Intelligent Schema Evolution unit and integration tests.
"""

from click.testing import CliRunner
import pytest

from apiforge.cli.main import cli
from apiforge.compiler.diff import compute_diff, format_diff
from apiforge.compiler.planner import (
    generate_migration_plan,
    format_migration_plan,
    format_impact_report,
    AddResource,
    RemoveResource,
    RenameResource,
    AddField,
    RemoveField,
    RenameField,
    ChangeFieldType,
)
from apiforge.compiler.snapshot import save_snapshot, SNAPSHOT_FILE


@pytest.fixture(autouse=True)
def clean_snapshot_env():
    """Ensure snapshot baseline is cleared before and after each test execution."""
    if SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.unlink()
    yield
    if SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.unlink()


class TestEvolutionRenameHeuristics:
    """Test field and resource rename algorithms and confidence levels."""

    def test_detects_field_rename(self):
        old_schema = {
            "resources": [{
                "resource": "Product",
                "fields": [{"name": "price", "type": "decimal"}]
            }]
        }
        new_schema = {
            "resources": [{
                "resource": "Product",
                "fields": [{"name": "unit_price", "type": "decimal"}]
            }]
        }

        diff = compute_diff(old_schema, new_schema)
        
        # Verify renamed field is output
        assert len(diff["renamed_fields"]) == 1
        rf = diff["renamed_fields"][0]
        assert rf["resource"] == "Product"
        assert rf["old_name"] == "price"
        assert rf["new_name"] == "unit_price"
        assert rf["confidence"] >= 0.80  # Heuristic position and type matches should give high score

        formatted = format_diff(diff)
        assert "Possible Rename Detected" in formatted
        assert "Product.price" in formatted
        assert "→" in formatted
        assert "Product.unit_price" in formatted
        assert "Confidence: 92%" in formatted

    def test_detects_resource_rename(self):
        old_schema = {
            "resources": [{
                "resource": "Product",
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "price", "type": "decimal"}
                ]
            }]
        }
        new_schema = {
            "resources": [{
                "resource": "CatalogItem",
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "price", "type": "decimal"}
                ]
            }]
        }

        diff = compute_diff(old_schema, new_schema)
        
        assert len(diff["renamed_resources"]) == 1
        rr = diff["renamed_resources"][0]
        assert rr["old_name"] == "Product"
        assert rr["new_name"] == "CatalogItem"
        assert rr["confidence"] >= 0.60

        formatted = format_diff(diff)
        assert "Possible Resource Rename Detected:" in formatted
        assert "Product → CatalogItem" in formatted


class TestEvolutionTypeChanges:
    """Test type change detection logic."""

    def test_detects_type_changes(self):
        old_schema = {
            "resources": [{
                "resource": "Product",
                "fields": [{"name": "price", "type": "decimal"}]
            }]
        }
        new_schema = {
            "resources": [{
                "resource": "Product",
                "fields": [{"name": "price", "type": "integer"}]
            }]
        }

        diff = compute_diff(old_schema, new_schema)
        
        assert len(diff["changed_types"]) == 1
        ct = diff["changed_types"][0]
        assert ct["resource"] == "Product"
        assert ct["name"] == "price"
        assert ct["old_type"] == "decimal"
        assert ct["new_type"] == "integer"

        formatted = format_diff(diff)
        assert "Field Type Changed" in formatted
        assert "Product.price" in formatted
        assert "decimal" in formatted
        assert "integer" in formatted


class TestEvolutionRiskAnalysis:
    """Test automated risk level mapping and plan reports."""

    def test_plan_risk_levels(self):
        old_schema = {
            "resources": [{
                "resource": "Product",
                "fields": [
                    {"name": "price", "type": "decimal"},
                    {"name": "old_price", "type": "decimal"}
                ]
            }]
        }
        new_schema = {
            "resources": [{
                "resource": "Product",
                "fields": [
                    {"name": "price", "type": "integer"},
                    {"name": "stock", "type": "integer"}
                ]
            }]
        }

        plan = generate_migration_plan(old_schema, new_schema)
        
        # We expect:
        # - AddField(Product.stock) -> SAFE
        # - RemoveField(Product.old_price) -> DESTRUCTIVE
        # - ChangeType(Product.price) -> WARNING
        assert len(plan) == 3
        
        safe_op = [op for op in plan if op.get_risk() == "SAFE"][0]
        warning_op = [op for op in plan if op.get_risk() == "WARNING"][0]
        destructive_op = [op for op in plan if op.get_risk() == "DESTRUCTIVE"][0]

        assert isinstance(safe_op, AddField)
        assert isinstance(warning_op, ChangeFieldType)
        assert isinstance(destructive_op, RemoveField)

        assert "Potential precision loss" in warning_op.get_risk_details()
        assert "Data loss possible" in destructive_op.get_risk_details()

        formatted = format_migration_plan(plan)
        assert "[SAFE]\nAddField(Product.stock)" in formatted
        assert "[WARNING]\nChangeType(Product.price)\ndecimal → integer" in formatted
        assert "Potential precision loss" in formatted
        assert "[DESTRUCTIVE]\nRemoveField(Product.old_price)" in formatted


class TestEvolutionImpactAnalysis:
    """Test belongs_to relationship dependency traversal paths."""

    def test_relationship_impact_traversal(self):
        old_schema = {
            "resources": [
                {
                    "resource": "Customer",
                    "fields": [{"name": "name", "type": "string"}]
                },
                {
                    "resource": "Order",
                    "fields": [
                        {"name": "customer", "type": "belongs_to", "target": "Customer"},
                        {"name": "amount", "type": "decimal"}
                    ]
                }
            ]
        }
        new_schema = {
            "resources": [
                {
                    "resource": "Customer",
                    "fields": [{"name": "full_name", "type": "string"}]
                },
                {
                    "resource": "Order",
                    "fields": [
                        {"name": "customer", "type": "belongs_to", "target": "Customer"},
                        {"name": "amount", "type": "decimal"}
                    ]
                }
            ]
        }

        plan = generate_migration_plan(old_schema, new_schema)
        assert len(plan) == 1
        assert isinstance(plan[0], RenameField)

        impact_report = format_impact_report(old_schema, new_schema, plan)
        
        # Changing Customer.name should affect both Customer and Order (because Order belongs_to Customer)
        assert "Affected Resources" in impact_report
        assert "Customer" in impact_report
        assert "Order" in impact_report

        assert "customer/models.py" in impact_report
        assert "customer/serializers.py" in impact_report
        assert "order/models.py" in impact_report
        assert "order/serializers.py" in impact_report
        assert "order/views.py" in impact_report  # Order has belongs_to, so it lists views.py


class TestEvolutionCompilationReport:
    """Test generation command compiles metrics and logs reports."""

    def test_cli_generate_displays_compilation_report(self, tmp_path):
        api_file = tmp_path / "blog.api"
        api_file.write_text(
            "resource Author {\n"
            "    name string\n"
            "}\n"
            "resource Post {\n"
            "    title string\n"
            "    author belongs_to Author\n"
            "}"
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["generate", str(api_file), "-o", str(tmp_path / "gen")])
        
        assert result.exit_code == 0
        assert "Compilation Report" in result.output
        assert "Resources: 2" in result.output
        assert "Fields: 3" in result.output
        assert "Relationships: 1" in result.output
        assert "✓ models.py" in result.output
        assert "✓ serializers.py" in result.output
        assert "✓ views.py" in result.output
        assert "✓ urls.py" in result.output
        assert "Compilation Time:" in result.output
