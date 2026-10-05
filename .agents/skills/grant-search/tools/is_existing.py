#!/usr/bin/env python3
"""
Duplicate detection helper for grants.

Checks if a new grant entry matches an existing entry in found_grants.json
using multiple matching strategies (ID, exact, URL, fuzzy).
"""

import json
import difflib
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def resolve_found_grants_path(path_str: str = "found_grants.json") -> Path:
    """Resolve found_grants.json path checking cwd, parent dir (if called from tools), or skill path."""
    p = Path(path_str)
    if p.exists():
        return p
    # Parent of tools folder
    tools_parent = Path(__file__).resolve().parent.parent / path_str
    if tools_parent.exists():
        return tools_parent
    # Skill relative path from repo root
    skill_p = Path(".agents/skills/grant-search") / path_str
    if skill_p.exists():
        return skill_p
    return p


class GrantDuplicateChecker:
    """Intelligent grant duplicate detection."""

    def __init__(self, found_grants_path: str = "found_grants.json"):
        """Initialize with path to found_grants.json."""
        self.found_grants_path = resolve_found_grants_path(found_grants_path)
        self.existing_grants: List[Dict] = []
        self._load_existing_grants()

    def _load_existing_grants(self):
        """Load existing grants from JSON."""
        if not self.found_grants_path.exists():
            print(f"⚠️  {self.found_grants_path} not found")
            return

        try:
            with open(self.found_grants_path, 'r') as f:
                data = json.load(f)
                raw_grants = data.get('grants', []) if isinstance(data, dict) else data
                self.existing_grants = [self._flat(g) for g in raw_grants]
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {self.found_grants_path}")
            self.existing_grants = []

    @staticmethod
    def _flat(entry: Dict) -> Dict:
        """Fill flat `organization`/`url` from nested `source` object if needed."""
        if not isinstance(entry, dict):
            return {}
        flat = dict(entry)
        source = entry.get('source') or {}
        if isinstance(source, dict):
            flat.setdefault('organization', source.get('name', ''))
            flat.setdefault('url', source.get('url', ''))
        return flat

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        return text.lower().strip() if text else ""

    def _id_match(self, new_entry: Dict, existing: Dict) -> bool:
        """Check if IDs match exactly."""
        new_id = new_entry.get("id")
        existing_id = existing.get("id")
        if new_id and existing_id and new_id == existing_id:
            return True
        return False

    def _exact_match(self, new_entry: Dict, existing: Dict) -> bool:
        """Check for exact name and org match."""
        new_name = self._normalize_text(new_entry.get('name', ''))
        new_org = self._normalize_text(new_entry.get('organization', ''))

        existing_name = self._normalize_text(existing.get('name', ''))
        existing_org = self._normalize_text(existing.get('organization', ''))

        if not new_name or not existing_name:
            return False

        if new_name == existing_name:
            if not new_org or not existing_org or new_org == existing_org:
                return True
        return False

    def _url_match(self, new_entry: Dict, existing: Dict) -> bool:
        """Check if URLs match or have significant overlap."""
        new_url = self._normalize_text(new_entry.get('url', '')).rstrip('/')
        existing_url = self._normalize_text(existing.get('url', '')).rstrip('/')

        if not new_url or not existing_url:
            return False

        # Direct match
        if new_url == existing_url:
            return True

        # Check domain and path overlap
        try:
            from urllib.parse import urlparse
            new_parsed = urlparse(new_url)
            existing_parsed = urlparse(existing_url)

            if new_parsed.netloc and new_parsed.netloc == existing_parsed.netloc:
                new_path = new_parsed.path.rstrip('/')
                existing_path = existing_parsed.path.rstrip('/')
                if new_path and new_path == existing_path:
                    return True
                path_ratio = difflib.SequenceMatcher(None, new_path, existing_path).ratio()
                return path_ratio > 0.85
        except Exception:
            pass

        return False

    def _organization_match(self, new_entry: Dict, existing: Dict, threshold: float = 0.8) -> bool:
        """Check for organization similarity."""
        new_org = self._normalize_text(new_entry.get('organization', ''))
        existing_org = self._normalize_text(existing.get('organization', ''))

        if not new_org or not existing_org:
            return True  # Don't reject if one side is missing org
        if new_org == existing_org:
            return True
        return difflib.SequenceMatcher(None, new_org, existing_org).ratio() >= threshold

    def _fuzzy_match(self, new_entry: Dict, existing: Dict, threshold: float = 0.85) -> bool:
        """Fuzzy match on grant name."""
        new_name = self._normalize_text(new_entry.get('name', ''))
        existing_name = self._normalize_text(existing.get('name', ''))

        if not new_name or not existing_name:
            return False

        name_ratio = difflib.SequenceMatcher(None, new_name, existing_name).ratio()
        return name_ratio >= threshold

    def check_duplicate(self, new_entry: Dict) -> Tuple[bool, Optional[Dict], str]:
        """
        Check if new entry is a duplicate.

        Returns:
            (is_duplicate, matching_existing_entry, reason)
        """
        if not new_entry:
            return False, None, "Empty entry"

        flat_entry = self._flat(new_entry)

        for existing in self.existing_grants:
            # 1. Matching ID
            if self._id_match(flat_entry, existing):
                return True, existing, "Matching grant ID"

            # 2. Exact match (highest confidence)
            if self._exact_match(flat_entry, existing):
                return True, existing, "Exact name and organization match"

            # 3. URL match (high confidence)
            if self._url_match(flat_entry, existing):
                return True, existing, "Same URL/program page"

            # 4. Fuzzy name match with compatible organization
            if self._fuzzy_match(flat_entry, existing, threshold=0.85):
                if self._organization_match(flat_entry, existing):
                    return True, existing, "Similar name and matching organization"

        return False, None, "No match found"

    def batch_check(self, entries: List[Dict]) -> Dict:
        """Check multiple entries and return report."""
        results = {
            'total': len(entries),
            'duplicates': [],
            'new': []
        }

        for entry in entries:
            is_dup, existing, reason = self.check_duplicate(entry)
            if is_dup:
                results['duplicates'].append({
                    'entry': entry,
                    'matched_existing': existing,
                    'reason': reason
                })
            else:
                results['new'].append(entry)

        return results

    def print_report(self, results: Dict):
        """Pretty print batch check results."""
        print(f"\n📊 Duplicate Check Report")
        print(f"{'='*60}")
        print(f"Total entries checked: {results['total']}")
        print(f"✅ New entries: {len(results['new'])}")
        print(f"⚠️  Duplicates found: {len(results['duplicates'])}\n")

        if results['duplicates']:
            print("Duplicates:")
            print("-" * 60)
            for item in results['duplicates']:
                entry = item['entry']
                existing = item['matched_existing']
                entry_name = entry.get('name', 'Unknown')
                entry_org = entry.get('organization') or (entry.get('source', {}) or {}).get('name', 'Unknown')
                exist_name = existing.get('name', 'Unknown')
                exist_org = existing.get('organization') or (existing.get('source', {}) or {}).get('name', 'Unknown')
                print(f"❌ {entry_name} ({entry_org})")
                print(f"   Reason: {item['reason']}")
                print(f"   Existing: {exist_name} ({exist_org})")
                print()

        if results['new']:
            print("New entries to add:")
            print("-" * 60)
            for item in results['new']:
                item_name = item.get('name', 'Unknown')
                item_org = item.get('organization') or (item.get('source', {}) or {}).get('name', 'Unknown')
                item_url = item.get('url') or (item.get('source', {}) or {}).get('url', 'N/A')
                print(f"✨ {item_name} ({item_org})")
                print(f"   URL: {item_url}")
                print()


def main():
    """CLI: python is_existing.py --check <entries.json> [found_grants.json]"""
    if len(sys.argv) < 3 or sys.argv[1] != "--check":
        print("Usage: python is_existing.py --check <entries.json> [found_grants.json]")
        sys.exit(1)

    input_file = Path(sys.argv[2])
    if not input_file.exists():
        # Try checking parent of tools
        alt_input = Path(__file__).resolve().parent.parent / sys.argv[2]
        if alt_input.exists():
            input_file = alt_input
        else:
            print(f"❌ File not found: {input_file}")
            sys.exit(1)

    try:
        with open(input_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in input file: {e}")
        sys.exit(1)

    if isinstance(data, dict):
        entries = data.get("grants", [data])
    elif isinstance(data, list):
        entries = data
    else:
        print("❌ Input must be JSON object or array")
        sys.exit(1)

    target_path_str = sys.argv[3] if len(sys.argv) > 3 else "found_grants.json"
    checker = GrantDuplicateChecker(target_path_str)
    results = checker.batch_check(entries)
    checker.print_report(results)
    sys.exit(1 if results["duplicates"] else 0)


if __name__ == "__main__":
    main()
