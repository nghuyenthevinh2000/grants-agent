#!/usr/bin/env python3
"""
Generate a summary JSON report of the total number of grants (and funders)
in each region under the grants directory.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def resolve_grants_dir(path_str: str = "grants") -> Path:
    p = Path(path_str)
    if p.exists() and p.is_dir():
        return p.resolve()
    # Check relative to script directory
    script_parent = Path(__file__).resolve().parent.parent.parent.parent.parent / "grants"
    if script_parent.exists():
        return script_parent.resolve()
    return p.resolve()


def generate_regional_report(grants_dir: Path) -> dict:
    """Scan all regional folders in grants_dir and aggregate grant counts."""
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_regions": 0,
        "total_grants": 0,
        "total_funders": 0,
        "regions": {}
    }

    # Find all subdirectories that contain grants.json or funders.json
    region_dirs = sorted([d for d in grants_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])

    for r_dir in region_dirs:
        grants_file = r_dir / "grants.json"
        funders_file = r_dir / "funders.json"

        # If neither exists, skip non-region subdirectories
        if not grants_file.exists() and not funders_file.exists():
            continue

        region_slug = r_dir.name
        region_code = region_slug.upper().replace("-", "_")
        region_name = region_slug.replace("-", " ").title()
        grants_list = []
        funders_list = []

        if grants_file.exists():
            try:
                with open(grants_file, "r", encoding="utf-8") as f:
                    g_data = json.load(f)
                    region_code = g_data.get("region", region_code)
                    region_name = g_data.get("name", region_name)
                    grants_list = g_data.get("grants", [])
            except Exception as e:
                print(f"⚠️ Error reading {grants_file}: {e}", file=sys.stderr)

        if funders_file.exists():
            try:
                with open(funders_file, "r", encoding="utf-8") as f:
                    f_data = json.load(f)
                    funders_list = f_data.get("funders", [])
            except Exception as e:
                print(f"⚠️ Error reading {funders_file}: {e}", file=sys.stderr)

        report["regions"][region_slug] = {
            "region_code": region_code,
            "region_name": region_name,
            "grants_count": len(grants_list),
            "funders_count": len(funders_list),
            "grant_ids": [g.get("id") for g in grants_list if isinstance(g, dict) and "id" in g]
        }

        report["total_grants"] += len(grants_list)
        report["total_funders"] += len(funders_list)

    report["total_regions"] = len(report["regions"])
    return report


def main():
    parser = argparse.ArgumentParser(description="Report total number of grants in each region as JSON")
    parser.add_argument("--grants-dir", default="grants", help="Path to grants directory (default: grants)")
    parser.add_argument("--output", "-o", default="grants/regional_summary.json",
                        help="Output path for the report JSON file (default: grants/regional_summary.json)")
    parser.add_argument("--print", action="store_true", help="Print report JSON directly to stdout")
    args = parser.parse_args()

    grants_dir = resolve_grants_dir(args.grants_dir)
    if not grants_dir.exists():
        print(f"❌ Grants directory not found: {grants_dir}", file=sys.stderr)
        sys.exit(1)

    report = generate_regional_report(grants_dir)

    # Save to file
    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = Path.cwd() / out_path

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✓ Regional summary report written to: {out_path}")
    print(f"  Total Regions: {report['total_regions']}")
    print(f"  Total Grants : {report['total_grants']}")
    print(f"  Total Funders: {report['total_funders']}")
    print()
    print("Breakdown by Region:")
    for slug, info in report["regions"].items():
        print(f"  • {slug:<20} ({info['region_code']}): {info['grants_count']} grants, {info['funders_count']} funders")

    if args.print:
        print("\n" + json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
