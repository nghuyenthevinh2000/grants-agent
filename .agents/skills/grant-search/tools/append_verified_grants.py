#!/usr/bin/env python3
"""
Safely append verified grants to found_grants.json
1. Load staging file (temporary file with new grants)
2. Validate schema
3. Check for duplicates using GrantDuplicateChecker
4. Clean staging-only fields (e.g., source_category) and normalize nulls
5. Append to found_grants.json only if all checks pass
6. Clean up staging file
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Ensure tools directory is in sys.path
_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from validate_grant_schema import GrantValidator
from is_existing import GrantDuplicateChecker, resolve_found_grants_path


def resolve_file_path(path_str: str) -> Path:
    p = Path(path_str)
    if p.exists():
        return p
    parent_p = Path(__file__).resolve().parent.parent / path_str
    if parent_p.exists():
        return parent_p
    return p


def append_verified_grants(staging_file: str, target_file: str = "found_grants.json"):
    """
    Verify and append grants from staging file to target file.

    Returns:
        (success: bool, added_count: int, errors: list)
    """

    staging_path = resolve_file_path(staging_file)
    target_path = resolve_found_grants_path(target_file)

    # Step 1: Load staging file
    print(f"📋 Step 1: Loading staging file: {staging_path}...")
    if not staging_path.exists():
        return False, 0, [f"Staging file not found: {staging_file}"]

    try:
        with open(staging_path) as f:
            staging_data = json.load(f)
    except json.JSONDecodeError as e:
        return False, 0, [f"Invalid JSON in staging file: {e}"]

    # Get grants from staging
    if isinstance(staging_data, dict):
        staging_grants = staging_data.get("grants", [staging_data])
    elif isinstance(staging_data, list):
        staging_grants = staging_data
    else:
        return False, 0, ["Staging file must contain array or object with 'grants' field"]

    print(f"   ✓ Loaded {len(staging_grants)} grants")

    # Step 2: Validate schema
    print(f"\n🔍 Step 2: Validating schema...")
    validator = GrantValidator()
    schema_errors = []

    for idx, grant in enumerate(staging_grants, 1):
        valid, errors, warnings = validator.validate_grant(grant)
        if not valid:
            grant_name = grant.get("name", f"Grant #{idx}") if isinstance(grant, dict) else f"Grant #{idx}"
            schema_errors.append(f"{grant_name}: {'; '.join(errors)}")

    if schema_errors:
        print(f"   ❌ Schema validation failed:")
        for error in schema_errors[:5]:
            print(f"      {error}")
        if len(schema_errors) > 5:
            print(f"      ... and {len(schema_errors) - 5} more errors")
        return False, 0, schema_errors

    print(f"   ✓ Schema valid for all {len(staging_grants)} grants")

    # Step 3: Check for duplicates in target using GrantDuplicateChecker
    print(f"\n📊 Step 3: Checking for duplicates against {target_path}...")
    checker = GrantDuplicateChecker(str(target_path))
    batch_results = checker.batch_check(staging_grants)

    duplicates = batch_results['duplicates']
    raw_new_grants = batch_results['new']

    if duplicates:
        print(f"   ⚠️  Found {len(duplicates)} duplicates (skipping):")
        for dup in duplicates[:5]:
            d_name = dup['entry'].get('name', 'Unknown')
            d_reason = dup.get('reason', '')
            print(f"      - {d_name} ({d_reason})")
        if len(duplicates) > 5:
            print(f"      ... and {len(duplicates) - 5} more")

    if not raw_new_grants:
        return False, 0, ["All grants in staging are duplicates of existing records"]

    print(f"   ✓ {len(raw_new_grants)} new unique grants to add")

    # Step 4: Clean staging-only fields and normalize nulls
    print(f"\n🧹 Step 4: Cleaning staging fields & normalizing...")
    cleaned_new_grants = []
    for grant in raw_new_grants:
        cleaned = dict(grant)
        # Strip discovery-only staging fields
        cleaned.pop("source_category", None)

        # Normalize optional nulls to schema defaults
        if cleaned.get("notes") is None:
            cleaned["notes"] = ""
        if cleaned.get("tags") is None:
            cleaned["tags"] = []

        if isinstance(cleaned.get("eligibility"), dict):
            if cleaned["eligibility"].get("special_requirements") is None:
                cleaned["eligibility"]["special_requirements"] = []

        if isinstance(cleaned.get("requirements"), dict):
            if cleaned["requirements"].get("key_requirements") is None:
                cleaned["requirements"]["key_requirements"] = []
            if cleaned["requirements"].get("focus_areas") is None:
                cleaned["requirements"]["focus_areas"] = []

        cleaned_new_grants.append(cleaned)

    # Step 5: Append to target
    print(f"\n💾 Step 5: Appending to {target_path}...")

    if target_path.exists():
        with open(target_path) as f:
            target_data = json.load(f)
    else:
        target_data = {
            "schema_version": "1.0",
            "total_grants": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "grants": []
        }

    target_data.setdefault("grants", [])
    target_data["grants"].extend(cleaned_new_grants)
    target_data["total_grants"] = len(target_data["grants"])
    target_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    with open(target_path, "w") as f:
        json.dump(target_data, f, indent=2)

    print(f"   ✓ Appended {len(cleaned_new_grants)} grants")
    print(f"   ✓ Total grants in {target_path.name}: {target_data['total_grants']}")

    # Step 6: Cleanup staging file
    try:
        staging_path.unlink()
        print(f"\n🗑️  Cleaned up staging file: {staging_path.name}")
    except Exception as e:
        print(f"\n⚠️  Could not remove staging file: {e}")

    return True, len(cleaned_new_grants), []


def main():
    if len(sys.argv) < 2:
        print("Usage: python append_verified_grants.py <staging_file.json> [target_file.json]")
        print("\nSafely appends verified grants to found_grants.json")
        sys.exit(1)

    staging_file = sys.argv[1]
    target_file = sys.argv[2] if len(sys.argv) > 2 else "found_grants.json"

    print("🔐 Safe Grant Append with Verification")
    print("=" * 60)

    success, added, errors = append_verified_grants(staging_file, target_file)

    print("\n" + "=" * 60)
    if success:
        print(f"✅ Success! Added {added} grants")
        sys.exit(0)
    else:
        print(f"❌ Failed to append grants:")
        for error in errors[:5]:
            print(f"   {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")
        sys.exit(1)


if __name__ == "__main__":
    main()
