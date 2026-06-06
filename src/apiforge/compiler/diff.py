"""
Phase 13 — Intelligent Schema Diff Engine.

Compares two APIForge schemas, detecting field renames, resource renames,
and type changes, with heuristic confidence scoring.
"""

import difflib


def compute_diff(old_schema: dict, new_schema: dict) -> dict:
    """Compare old and new schema structures, returning structured changes.

    Args:
        old_schema: Stored dictionary representation of the baseline schema.
        new_schema: Freshly parsed dictionary representation of the active schema.

    Returns:
        A dictionary containing lists of added/removed/renamed resources and fields,
        as well as field type changes.
    """
    old_resources = {r["resource"]: r for r in old_schema.get("resources", [])}
    new_resources = {r["resource"]: r for r in new_schema.get("resources", [])}

    added_resource_names = [rname for rname in new_resources if rname not in old_resources]
    removed_resource_names = [rname for rname in old_resources if rname not in new_resources]

    renamed_resources = []
    actual_added_resources = []
    actual_removed_resources = []

    # Heuristic Resource Rename Detection
    matched_added_resources = set()
    for old_rname in removed_resource_names:
        old_res = old_resources[old_rname]
        old_fields = {f["name"]: f for f in old_res.get("fields", [])}
        
        best_new_rname = None
        best_confidence = 0.0

        for new_rname in added_resource_names:
            if new_rname not in matched_added_resources:
                new_res = new_resources[new_rname]
                new_fields = {f["name"]: f for f in new_res.get("fields", [])}

                # Compute field overlap intersection
                common_fields = set(old_fields.keys()) & set(new_fields.keys())
                intersection_ratio = len(common_fields) / max(1, max(len(old_fields), len(new_fields)))
                
                # Compute name similarity ratio
                name_ratio = difflib.SequenceMatcher(None, old_rname, new_rname).ratio()
                
                confidence = 0.60 * intersection_ratio + 0.40 * name_ratio
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_new_rname = new_rname

        if best_confidence >= 0.60:
            renamed_resources.append({
                "old_name": old_rname,
                "new_name": best_new_rname,
                "confidence": best_confidence
            })
            matched_added_resources.add(best_new_rname)
        else:
            actual_removed_resources.append(old_rname)

    actual_added_resources = [rname for rname in added_resource_names if rname not in matched_added_resources]

    # Map renamed resources for field checking
    resource_mappings = {rr["old_name"]: rr["new_name"] for rr in renamed_resources}

    added_fields = []
    removed_fields = []
    renamed_fields = []
    changed_types = []

    # Compare fields for resources present in both schemas
    common_resource_pairs = []
    for rname in old_resources:
        if rname in new_resources:
            common_resource_pairs.append((rname, rname))
        elif rname in resource_mappings:
            common_resource_pairs.append((rname, resource_mappings[rname]))

    for old_rname, new_rname in common_resource_pairs:
        old_res = old_resources[old_rname]
        new_res = new_resources[new_rname]

        old_fields = old_res.get("fields", [])
        new_fields = new_res.get("fields", [])

        old_fields_dict = {f["name"]: f for f in old_fields}
        new_fields_dict = {f["name"]: f for f in new_fields}

        # Find fields with identical names
        common_field_names = set(old_fields_dict.keys()) & set(new_fields_dict.keys())
        for fname in common_field_names:
            old_f = old_fields_dict[fname]
            new_f = new_fields_dict[fname]
            if old_f["type"] != new_f["type"]:
                changed_types.append({
                    "resource": new_rname,
                    "name": fname,
                    "old_type": old_f["type"],
                    "new_type": new_f["type"]
                })

        # Calculate added/removed field lists
        added_field_names = [f["name"] for f in new_fields if f["name"] not in common_field_names]
        removed_field_names = [f["name"] for f in old_fields if f["name"] not in common_field_names]

        # Heuristic Field Rename Detection
        matched_added_fields = set()
        for old_fname in removed_field_names:
            old_f = old_fields_dict[old_fname]
            old_idx = old_fields.index(old_f)

            best_new_fname = None
            best_confidence = 0.0

            for new_fname in added_field_names:
                if new_fname not in matched_added_fields:
                    new_f = new_fields_dict[new_fname]
                    new_idx = new_fields.index(new_f)

                    # 1. Type Match base
                    if old_f["type"] == new_f["type"]:
                        base = 0.70
                    else:
                        base = 0.20

                    # 2. Name Ratio
                    name_ratio = difflib.SequenceMatcher(None, old_fname, new_fname).ratio()

                    # 3. Position Ratio
                    pos_old = old_idx / max(1, len(old_fields))
                    pos_new = new_idx / max(1, len(new_fields))
                    pos_ratio = 1.0 - abs(pos_old - pos_new)

                    confidence = base + 0.22 * name_ratio + 0.08 * pos_ratio
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_new_fname = new_fname

            if best_confidence >= 0.65:
                renamed_fields.append({
                    "resource": new_rname,
                    "old_name": old_fname,
                    "new_name": best_new_fname,
                    "confidence": best_confidence
                })
                matched_added_fields.add(best_new_fname)
            else:
                removed_fields.append(f"{new_rname}.{old_fname}")

        for new_fname in added_field_names:
            if new_fname not in matched_added_fields:
                added_fields.append(f"{new_rname}.{new_fname}")

    return {
        "added_resources": actual_added_resources,
        "removed_resources": actual_removed_resources,
        "renamed_resources": renamed_resources,
        "added_fields": added_fields,
        "removed_fields": removed_fields,
        "renamed_fields": renamed_fields,
        "changed_types": changed_types,
    }


def format_diff(diff: dict) -> str:
    """Format structural schema changes into human-readable console outputs."""
    lines = []

    if diff.get("added_resources"):
        lines.append("Added resource:")
        for r in diff["added_resources"]:
            lines.append(f"  {r}")
        lines.append("")

    if diff.get("removed_resources"):
        lines.append("Removed resource:")
        for r in diff["removed_resources"]:
            lines.append(f"  {r}")
        lines.append("")

    if diff.get("renamed_resources"):
        lines.append("Possible Resource Rename Detected:")
        for rr in diff["renamed_resources"]:
            lines.append(f"  {rr['old_name']} → {rr['new_name']}")
            lines.append(f"  Confidence: {int(rr['confidence'] * 100)}%")
        lines.append("")

    if diff.get("added_fields"):
        lines.append("Added field:")
        for f in diff["added_fields"]:
            lines.append(f"  {f}")
        lines.append("")

    if diff.get("removed_fields"):
        lines.append("Removed field:")
        for f in diff["removed_fields"]:
            lines.append(f"  {f}")
        lines.append("")

    if diff.get("renamed_fields"):
        lines.append("Possible Rename Detected")
        lines.append("")
        for rf in diff["renamed_fields"]:
            lines.append(f"  {rf['resource']}.{rf['old_name']}")
            lines.append("  →")
            lines.append(f"  {rf['resource']}.{rf['new_name']}")
            lines.append("")
            lines.append(f"  Confidence: {int(rf['confidence'] * 100)}%")
        lines.append("")

    if diff.get("changed_types"):
        lines.append("Field Type Changed")
        lines.append("")
        for ct in diff["changed_types"]:
            lines.append(f"  {ct['resource']}.{ct['name']}")
            lines.append("")
            lines.append(f"  {ct['old_type']}")
            lines.append("  →")
            lines.append(f"  {ct['new_type']}")
        lines.append("")

    if not lines:
        return "No changes detected."

    return "\n".join(lines).strip()
