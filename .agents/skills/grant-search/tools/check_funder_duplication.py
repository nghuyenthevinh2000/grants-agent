#!/usr/bin/env python3
"""
Funder Duplication Checker
Checks for exact and fuzzy duplicates, shared URLs, and overlapping domains
in funder_websites.json.
"""

import json
import sys
import difflib
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from urllib.parse import urlparse


def resolve_funder_file_paths(path_str: str = None) -> List[Path]:
    """Resolve funder_websites.json or scan all regional grants/*/funders.json."""
    if path_str:
        p = Path(path_str)
        if p.exists():
            return [p.resolve()]
        if (Path("grants") / path_str).exists():
            return [(Path("grants") / path_str).resolve()]

    # Check for regional funders.json files across grants/*/funders.json
    candidates = [
        Path("grants"),
        Path(__file__).resolve().parent.parent.parent.parent.parent / "grants",
        Path(__file__).resolve().parent.parent / "../../grants",
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            regional_files = sorted(c.glob("*/funders.json"))
            if regional_files:
                return [f.resolve() for f in regional_files]

    return [Path(path_str)] if path_str else []


class FunderDuplicateChecker:
    """Detects duplicates and overlaps among funders across regional funders.json."""

    def __init__(self, file_path: str = None):
        self.file_paths = resolve_funder_file_paths(file_path)
        self.funders: List[Dict] = []
        self._load()

    def _load(self):
        if not self.file_paths:
            raise FileNotFoundError("No funder files found.")
        self.funders = []
        for p in self.file_paths:
            if not p.exists():
                raise FileNotFoundError(f"File not found: {p}")
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.funders.extend(data.get("funders", []))

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Strip punctuation, casing, and common corporate suffixes for comparison."""
        n = name.lower().strip()
        for char in "()[],.-/&":
            n = n.replace(char, " ")
        words = [w for w in n.split() if w not in ("the", "and", "foundation", "fund", "inc", "llc", "org", "program")]
        return " ".join(words)

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize URL: strip protocol, www, query params, and trailing slash."""
        if not url:
            return ""
        u = url.strip().lower()
        if u.startswith("https://"):
            u = u[8:]
        elif u.startswith("http://"):
            u = u[7:]
        if u.startswith("www."):
            u = u[4:]
        u = u.split("?")[0].split("#")[0].rstrip("/")
        return u

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract root domain from URL."""
        if not url:
            return ""
        parsed = urlparse(url if "://" in url else "https://" + url)
        netloc = parsed.netloc.lower().strip()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        # Get base domain if subdomain like new.nsf.gov -> nsf.gov
        parts = netloc.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return netloc

    def check_all(self, fuzzy_threshold: float = 0.82) -> Dict:
        """Run all duplicate and overlap checks."""
        report = {
            "total_funders": len(self.funders),
            "files": [str(p) for p in self.file_paths],
            "exact_id_duplicates": [],
            "exact_name_duplicates": [],
            "exact_url_duplicates": [],
            "fuzzy_name_matches": [],
            "shared_domains": [],
            "discovery_channel_overlaps": []
        }

        # 1. Exact ID duplicates
        id_map = defaultdict(list)
        for idx, f in enumerate(self.funders):
            fid = f.get("id", f"idx-{idx}")
            id_map[fid].append(f)
        for fid, entries in id_map.items():
            if len(entries) > 1:
                report["exact_id_duplicates"].append({
                    "id": fid,
                    "names": [e.get("name") for e in entries]
                })

        # 2. Exact Name duplicates
        name_map = defaultdict(list)
        for f in self.funders:
            raw_name = f.get("name", "").strip().lower()
            name_map[raw_name].append(f)
        for raw_name, entries in name_map.items():
            if len(entries) > 1:
                report["exact_name_duplicates"].append({
                    "name": raw_name,
                    "ids": [e.get("id") for e in entries]
                })

        # 3. Exact URL matches (homepage or portal)
        url_map = defaultdict(list)
        for f in self.funders:
            fid = f.get("id")
            hp = self._normalize_url(f.get("homepage_url", ""))
            portal = self._normalize_url(f.get("funding_portal_url", ""))
            if hp:
                url_map[("homepage", hp)].append(fid)
            if portal:
                url_map[("portal", portal)].append(fid)

        for (u_type, url_str), fids in url_map.items():
            if len(fids) > 1:
                report["exact_url_duplicates"].append({
                    "type": u_type,
                    "url": url_str,
                    "funder_ids": fids
                })

        # 4. Fuzzy Name matches & Shared Domains (pairwise)
        checked_pairs = set()
        for i in range(len(self.funders)):
            f1 = self.funders[i]
            n1_norm = self._normalize_name(f1.get("name", ""))
            d1 = self._extract_domain(f1.get("homepage_url", ""))

            for j in range(i + 1, len(self.funders)):
                f2 = self.funders[j]
                n2_norm = self._normalize_name(f2.get("name", ""))
                d2 = self._extract_domain(f2.get("homepage_url", ""))

                pair_key = (f1["id"], f2["id"])
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)

                # Fuzzy name
                if n1_norm and n2_norm and n1_norm != n2_norm:
                    ratio = difflib.SequenceMatcher(None, n1_norm, n2_norm).ratio()
                    if ratio >= fuzzy_threshold:
                        report["fuzzy_name_matches"].append({
                            "similarity": round(ratio, 2),
                            "funder1": {"id": f1["id"], "name": f1["name"], "category": f1.get("category")},
                            "funder2": {"id": f2["id"], "name": f2["name"], "category": f2.get("category")}
                        })

                # Shared root domain
                if d1 and d2 and d1 == d2 and d1 not in ("org", "com", "gov", "edu", "net", "io"):
                    report["shared_domains"].append({
                        "domain": d1,
                        "funder1": {"id": f1["id"], "name": f1["name"], "category": f1.get("category")},
                        "funder2": {"id": f2["id"], "name": f2["name"], "category": f2.get("category")}
                    })

        # 5. Overlapping Discovery Channels
        channel_map = defaultdict(list)
        for f in self.funders:
            for ch in f.get("discovery_channels", []):
                norm_ch = self._normalize_url(ch)
                if norm_ch:
                    channel_map[norm_ch].append(f["id"])

        for ch_url, fids in channel_map.items():
            if len(fids) > 1:
                report["discovery_channel_overlaps"].append({
                    "channel_url": ch_url,
                    "shared_by_funders": fids
                })

        return report

    def print_report(self, report: Dict, show_details: bool = True) -> int:
        """Pretty print the duplicate report. Returns exit code (1 if critical duplicates, 0 if clean)."""
        exact_id_count = len(report["exact_id_duplicates"])
        exact_name_count = len(report["exact_name_duplicates"])
        exact_url_count = len(report["exact_url_duplicates"])
        fuzzy_count = len(report["fuzzy_name_matches"])
        shared_domain_count = len(report["shared_domains"])
        channel_overlap_count = len(report["discovery_channel_overlaps"])

        critical_errors = exact_id_count + exact_name_count + exact_url_count

        print("=" * 70)
        print("🔍 FUNDER DUPLICATION REPORT")
        print("=" * 70)
        files_desc = ", ".join(Path(f).parent.name + "/funders.json" for f in report['files']) if len(report['files']) > 1 else (report['files'][0] if report['files'] else 'None')
        print(f"Target Files  : {files_desc}")
        print(f"Total Funders : {report['total_funders']}")
        print()
        print("CRITICAL ISSUES (Exact Duplicates):")
        print(f"  ❌ Duplicate IDs    : {exact_id_count}")
        print(f"  ❌ Duplicate Names  : {exact_name_count}")
        print(f"  ❌ Duplicate URLs   : {exact_url_count}")
        print()
        print("WARNINGS & POTENTIAL OVERLAPS:")
        print(f"  ⚠️  Fuzzy Name Matches         : {fuzzy_count}")
        print(f"  ⚠️  Shared Root Domains        : {shared_domain_count}")
        print(f"  ⚠️  Overlapping Channels       : {channel_overlap_count}")
        print("-" * 70)

        if critical_errors > 0:
            print("\n🚨 CRITICAL DUPLICATES FOUND:")
            for item in report["exact_id_duplicates"]:
                print(f"  - Duplicate ID '{item['id']}': used by {item['names']}")
            for item in report["exact_name_duplicates"]:
                print(f"  - Duplicate Name '{item['name']}': IDs {item['ids']}")
            for item in report["exact_url_duplicates"]:
                print(f"  - Duplicate {item['type']} URL '{item['url']}': shared by {item['funder_ids']}")

        if show_details and (fuzzy_count > 0 or shared_domain_count > 0 or channel_overlap_count > 0):
            print("\n📋 POTENTIAL OVERLAPS BREAKDOWN:")

            if fuzzy_count > 0:
                print("\n[Fuzzy Name Matches]")
                for item in report["fuzzy_name_matches"]:
                    sim = int(item['similarity'] * 100)
                    f1 = item['funder1']
                    f2 = item['funder2']
                    print(f"  • ({sim}% match):")
                    print(f"      1. [{f1['id']}] {f1['name']} ({f1['category']})")
                    print(f"      2. [{f2['id']}] {f2['name']} ({f2['category']})")

            if shared_domain_count > 0:
                print("\n[Shared Root Domains (Multiple entities from same institution)]")
                for item in report["shared_domains"]:
                    f1 = item['funder1']
                    f2 = item['funder2']
                    print(f"  • Domain: {item['domain']}")
                    print(f"      - {f1['name']} ({f1['id']})")
                    print(f"      - {f2['name']} ({f2['id']})")

            if channel_overlap_count > 0:
                print("\n[Overlapping Discovery Channels]")
                for item in report["discovery_channel_overlaps"]:
                    print(f"  • URL: {item['channel_url']}")
                    print(f"      Shared by IDs: {item['shared_by_funders']}")

        print("\n" + "=" * 70)
        if critical_errors > 0:
            print("❌ STATUS: FAILED (Critical duplicates detected)")
            return 1
        elif fuzzy_count > 0 or shared_domain_count > 0:
            print("✅ STATUS: CLEAN (No critical duplicates, warnings noted above)")
            return 0
        else:
            print("✅ STATUS: PERFECT (100% unique IDs, names, domains, and URLs)")
            return 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Check for duplicates across regional funders.json files")
    parser.add_argument("file", nargs="?", default=None,
                        help="Path to funder JSON or omit to scan all grants/*/funders.json")
    parser.add_argument("--fuzzy-threshold", type=float, default=0.82,
                        help="Similarity threshold for fuzzy name matching (0.0 to 1.0, default: 0.82)")
    parser.add_argument("--quiet", action="store_true", help="Only show summary, omit detailed list")

    args = parser.parse_args()

    try:
        checker = FunderDuplicateChecker(args.file)
        report = checker.check_all(fuzzy_threshold=args.fuzzy_threshold)
        code = checker.print_report(report, show_details=not args.quiet)
        sys.exit(code)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
