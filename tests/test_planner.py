"""
Phase 10 — Migration Planner tests.
"""

from click.testing import CliRunner
import pytest

from apiforge.cli.main import cli
from apiforge.compiler.planner import (
    generate_migration_plan,
    format_migration_plan,
    AddResource,
    RemoveResource,
    AddField,
    RemoveField,
    RenameField,
)
from apiforge.compiler.snapshot import save_snapshot, SNAPSHOT_FILE


@pytest.fixture(autouse=True)
def clean_snapshot_env():
    """Ensure baseline snapshot is cleared before and after each test execution."""
    if SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.unlink()
    yield
    if SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.unlink()


class TestPlannerLogic:
    """Test structural migration operations calculation."""

    def test_no_changes_detected(self):
        schema = {
            "resources": [{
                "resource": "Product",
                "fields": [{"name": "name", "type": "string"}]
            }]
        }
        plan = generate_migration_plan(schema, schema)
        assert len(plan) == 0
        assert format_migration_plan(plan) == "No migration steps needed."

    def test_add_and_remove_resources(self):
        old_schema = {
            "resources": [{
                "resource": "OldModel",
                "fields": [{"name": "id", "type": "integer"}]
            }]
        }
        new_schema = {
            "resources": [{
                "resource": "NewModel",
                "fields": [{"name": "title", "type": "string"}]
            }]
        }

        plan = generate_migration_plan(old_schema, new_schema)
        assert len(plan) == 2

        # Check types of generated operations
        add_ops = [op for op in plan if isinstance(op, AddResource)]
        remove_ops = [op for op in plan if isinstance(op, RemoveResource)]

        assert len(add_ops) == 1
        assert add_ops[0].name == "NewModel"
        assert add_ops[0].fields == [{"name": "title", "type": "string"}]
        assert "AddResource(name='NewModel', fields=[title: string])" in repr(add_ops[0])

        assert len(remove_ops) == 1
        assert remove_ops[0].name == "OldModel"
        assert "RemoveResource(name='OldModel')" in repr(remove_ops[0])

    def test_add_and_remove_fields(self):
        old_schema = {
            "resources": [{
                "resource": "User",
                "fields": [
                    {"name": "username", "type": "string"},
                    {"name": "price", "type": "decimal"}
                ]
            }]
        }
        new_schema = {
            "resources": [{
                "resource": "User",
                "fields": [
                    {"name": "username", "type": "string"},
                    {"name": "stock", "type": "integer"}
                ]
            }]
        }

        plan = generate_migration_plan(old_schema, new_schema)
        
        # In our logic, 'price' (decimal) and 'stock' (integer) have different types,
        # so they will NOT match as rename, but separate AddField and RemoveField
        assert len(plan) == 2
        add_ops = [op for op in plan if isinstance(op, AddField)]
        remove_ops = [op for op in plan if isinstance(op, RemoveField)]

        assert len(add_ops) == 1
        assert add_ops[0].resource == "User"
        assert add_ops[0].name == "stock"
        assert add_ops[0].field_type == "integer"
        assert "AddField(resource='User', name='stock', type='integer')" in repr(add_ops[0])

        assert len(remove_ops) == 1
        assert remove_ops[0].resource == "User"
        assert remove_ops[0].name == "price"
        assert "RemoveField(resource='User', name='price')" in repr(remove_ops[0])

    def test_rename_fields_heuristic(self):
        old_schema = {
            "resources": [{
                "resource": "User",
                "fields": [{"name": "username", "type": "string"}]
            }]
        }
        new_schema = {
            "resources": [{
                "resource": "User",
                "fields": [{"name": "handle", "type": "string"}]
            }]
        }

        plan = generate_migration_plan(old_schema, new_schema)
        
        # 'username' (string) and 'handle' (string) have matching type inside resource 'User'.
        # This triggers rename field operation.
        assert len(plan) == 1
        assert isinstance(plan[0], RenameField)
        assert plan[0].resource == "User"
        assert plan[0].old_name == "username"
        assert plan[0].new_name == "handle"
        assert "RenameField(resource='User', old_name='username', new_name='handle')" in repr(plan[0])

    def test_relationships_migration_ops(self):
        old_schema = {"resources": []}
        new_schema = {
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

        plan = generate_migration_plan(old_schema, new_schema)
        add_ops = [op for op in plan if isinstance(op, AddResource)]
        
        assert len(add_ops) == 2
        order_op = [op for op in add_ops if op.name == "Order"][0]
        assert "belongs_to to Customer" in repr(order_op)


class TestPlannerCLI:
    """Test CLI subcommand integration for migration planning."""

    def test_cli_plan_error_when_no_snapshot(self, tmp_path):
        api_file = tmp_path / "test.api"
        api_file.write_text("resource User { username string }")

        runner = CliRunner()
        result = runner.invoke(cli, ["plan", str(api_file)])
        
        assert result.exit_code == 1
        assert "Error: No previous schema snapshot found" in result.output

    def test_cli_plan_displays_formatted_list(self, tmp_path):
        # 1. Establish baseline
        old_schema = {
            "resources": [{
                "resource": "User",
                "fields": [{"name": "username", "type": "string"}]
            }]
        }
        save_snapshot(old_schema)

        # 2. Create updated file
        api_file = tmp_path / "test.api"
        api_file.write_text(
            "resource User {\n"
            "    username string\n"
            "    age integer\n"
            "}\n"
            "resource Role {\n"
            "    title string\n"
            "}"
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["plan", str(api_file)])
        
        assert result.exit_code == 0
        assert "Migration Plan" in result.output
        assert "AddResource(Role)" in result.output
        assert "AddField(User.age)" in result.output
