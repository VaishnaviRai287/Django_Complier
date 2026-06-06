"""
Phase 9 — Diff Engine.

Compares two APIForge schemas and extracts structural additions and removals.
"""


def compute_diff(old_schema: dict, new_schema: dict) -> dict:
    """Compare old and new schema structures, returning additions and removals.

    Args:
        old_schema: Stored dictionary representation of the baseline schema.
        new_schema: Freshly parsed dictionary representation of the active schema.

    Returns:
        A dictionary containing lists of added/removed resources and fields.
    """
    old_resources = {r["resource"]: r for r in old_schema.get("resources", [])}
    new_resources = {r["resource"]: r for r in new_schema.get("resources", [])}

    added_resources = []
    removed_resources = []
    added_fields = []
    removed_fields = []

    # 1. Compare resource names
    for name in new_resources:
        if name not in old_resources:
            added_resources.append(name)

    for name in old_resources:
        if name not in new_resources:
            removed_resources.append(name)

    # 2. Compare fields for resources present in both schemas
    for name in new_resources:
        if name in old_resources:
            old_fields = {f["name"]: f for f in old_resources[name].get("fields", [])}
            new_fields = {f["name"]: f for f in new_resources[name].get("fields", [])}

            for fname in new_fields:
                if fname not in old_fields:
                    added_fields.append(f"{name}.{fname}")

            for fname in old_fields:
                if fname not in new_fields:
                    removed_fields.append(f"{name}.{fname}")

    return {
        "added_resources": added_resources,
        "removed_resources": removed_resources,
        "added_fields": added_fields,
        "removed_fields": removed_fields,
    }


def format_diff(diff: dict) -> str:
    """Format the calculated diff structure into human-readable terminal output.

    Args:
        diff: The difference dictionary calculated by compute_diff().

    Returns:
        Formatted multi-line string ready for stdout.
    """
    lines = []

    if diff["added_resources"]:
        lines.append("Added resource:")
        for r in diff["added_resources"]:
            lines.append(f"  {r}")
        lines.append("")

    if diff["removed_resources"]:
        lines.append("Removed resource:")
        for r in diff["removed_resources"]:
            lines.append(f"  {r}")
        lines.append("")

    if diff["added_fields"]:
        lines.append("Added field:")
        for f in diff["added_fields"]:
            lines.append(f"  {f}")
        lines.append("")

    if diff["removed_fields"]:
        lines.append("Removed field:")
        for f in diff["removed_fields"]:
            lines.append(f"  {f}")
        lines.append("")

    if not lines:
        return "No changes detected."

    return "\n".join(lines).strip()
