# Grants Agent (`grants-agent`)

> 💡 **Quick Guide for Humans**: Copy and paste this to your AI agent:
> ```text
> install https://github.com/nghuyenthevinh2000/grants-agent.git
> ```

> **Curated Grant Intelligence & Search Toolkit for Autonomous AI Agents**  
> Comprehensive database of 139+ technology, AI safety, scientific research, and Web3/open-source grant programs optimized for programmatic agent retrieval, applicant matching, and verification.

---

## 📌 Overview

`grants-agent` provides machine-readable datasets, structured schemas, deduplication utilities, and domain-matching workflows designed to help AI agents (and human researchers) quickly discover, filter, and match funding opportunities for:

- **Academic & Independent Researchers** (including non-degree autodidacts & student founders).
- **Core Technology & Open-Source Projects** (Web3, cryptographic infrastructure, digital privacy).
- **Scientific Computing & Hardware** (AI compute credits, GPU allocations, cloud infrastructure).
- **Mission-Driven & Frontier Tech** (AI safety, biosecurity, existential risk, climate tech).

---

## 📂 Repository Structure

```text
grants-agent/
├── README.md                      # This guide for developers and AI agents
├── grants/                        # 🔍 Regional databases (grants.json & funders.json)
│   ├── README.md                  # Central index matrix for all 10 regions
│   ├── newest_grants.json         # Global chronological discovery feed
│   ├── global/                    # Worldwide / remote opportunities (Web3, AI safety)
│   ├── sea/                       # Southeast Asia (Vietnam, Singapore, ASEAN)
│   ├── north-america/             # US & Canada (Federal, NSF, DARPA, DOE)
│   └── europe/, east-asia/, etc.  # Other regional directories
├── reports/                       # 📄 Deep-dive applicant matching case studies & reports
│   └── grant-recommendations-tran-the-son.md # Case study: Travel & research grants for non-degree researcher
└── .agents/
    └── skills/
        └── grant-search/          # Automated grant discovery & verification skill
            ├── SKILL.md           # 10-category search taxonomy and query playbook
            ├── process_grant.md   # Schema rules, eligibility classification & validation workflow
            └── tools/             # Python tools for validation and duplicate prevention
                ├── check_funder_duplication.py
                ├── validate_grant_schema.py
                ├── is_existing.py
                └── append_verified_grants.py
```

---

## ⚡ Quickstart & Installation

### Option 1: Standalone Clone

```bash
git clone https://github.com/nghuyenthevinh2000/grants-agent.git
cd grants-agent
```

### Option 2: As a Submodule in an Existing Project

```bash
git submodule add https://github.com/nghuyenthevinh2000/grants-agent.git projects/grants-agent
git submodule update --init --recursive
```

### Prerequisites

- **Python**: 3.10 or higher.

- **Dependencies**: Standard library only (`json`, `pathlib`, `difflib`, `argparse`, `re`). No heavy external packages required for search and verification tools.

---

## 🤖 AI Agent Search Guide: How Agents Search in `grants/`

Autonomous AI agents can search and extract matching grants using either **Python scripts**, **CLI one-liners**, or **structured JSON querying**.

### 1. Data Files at a Glance

| File / Directory | What It Contains | When An Agent Should Query It |
| :--- | :--- | :--- |
| [`grants/<region>/funders.json`](grants/README.md) | 163 total funding organizations partitioned across 10 regions (`global/`, `sea/`, `north-america/`, etc.), including portals, discovery channels, and hints. | Regional or global discovery respecting applicant geographic eligibility. |
| [`grants/<region>/grants.json`](grants/README.md) | Granular, region-specific grant opportunities with deadlines, award bounds ($ min/max), currency, and application requirements. | Finding matching programs targeted to the applicant's geographical base. |
| [`grants/newest_grants.json`](grants/newest_grants.json) | Global discovery feed of newest verified grants across all regions. | Quick tracking of recent additions, deadlines, and awards. |

---

### 2. Fast Python Query Snippets for AI Agents

Agents can run these targeted scripts directly via terminal/command execution:

#### A. Search by Keywords & Focus Areas

```bash
python3 -c "
import json
from pathlib import Path

kw = 'quantum'  # Target keyword (e.g. quantum, travel, ai-safety, privacy)
funders = []
for p in Path('grants').glob('*/funders.json'):
    with open(p) as f:
        funders.extend(json.load(f).get('funders', []))

matches = []
for funder in funders:
    funder_str = json.dumps(funder, ensure_ascii=False).lower()
    if kw.lower() in funder_str:
        matches.append({
            'name': funder.get('name'),
            'category': funder.get('category'),
            'portal': funder.get('funding_portal_url'),
            'programs': funder.get('active_programs_sample', []),
            'hints': funder.get('agent_search_hints', '')
        })

print(f'Found {len(matches)} matching funders for \"{kw}\":\n')
for m in matches[:10]:
    print(f\"• {m['name']} ({m['category']})\")
    print(f\"  Portal: {m['portal']}\")
    if m['programs']:
        print(f\"  Programs: {', '.join(m['programs'])}\")
    if m['hints']:
        print(f\"  Agent Hint: {m['hints']}\")
    print()
"
```

#### B. Filter by Applicant Eligibility (e.g., Non-Degree, Independent, Student)

```bash
python3 -c "
import json

target_type = 'independent_researcher'  # e.g. independent_researcher, student, developer
funders = []
for p in Path('grants').glob('*/funders.json'):
    with open(p) as f:
        funders.extend(json.load(f).get('funders', []))

for f in funders:
    types = f.get('applicant_types', [])
    if target_type in types:
        print(f\"• {f['name']} | Portal: {f['funding_portal_url']} | Programs: {f.get('active_programs_sample')}\")
"
```

#### C. Search Detailed Grants in `newest_grants.json`

```bash
python3 -c "
import json

with open('grants/newest_grants.json') as f:
    data = json.load(f)

for grant in data.get('grants', []):
    award = grant.get('award', {})
    amount = f\"\${award.get('min_amount'):,} - \${award.get('max_amount'):,} {award.get('currency')}\"
    print(f\"ID: {grant['id']} | Name: {grant['name']}\")
    print(f\"  Award: {amount} | Deadline: {grant.get('deadline')}\")
    print(f\"  Focus: {', '.join(grant.get('requirements', {}).get('focus_areas', []))}\")
    print(f\"  Link: {grant.get('source', {}).get('url')}\n\")
"
```

---

## 🛠️ Verification & Pipeline Tools

The `.agents/skills/grant-search/tools/` folder contains automated validation scripts for checking new grants and preventing duplicates:

### 1. Validate Schema

Ensures grant records strictly conform to the expected format before committing:

```bash
python3 .agents/skills/grant-search/tools/validate_grant_schema.py grants/newest_grants.json
```

### 2. Check Funder Duplication

Checks if a new funder already exists across all regional `grants/*/funders.json` using exact URL and fuzzy string matching:

```bash
python3 .agents/skills/grant-search/tools/check_funder_duplication.py
```

### 3. Generate Regional Summary Report

Aggregates the total number of grants and funders across all 10 regions and writes a consolidated JSON report:

```bash
python3 .agents/skills/grant-search/tools/report_regional_grants.py
```
*(Outputs to `grants/regional_summary.json`)*

---

## 📋 Recommended Prompt for External AI Agents

When instructing another AI agent to look up funding opportunities in this repository, paste the following prompt:

```text
You have access to the grants intelligence database organized by geographic region in `grants/`.
1. Inspect the relevant regional folders (e.g., `grants/sea/funders.json`, `grants/global/funders.json`, or `grants/north-america/funders.json`) based on the applicant's geographical base.
2. Check `grants/<region>/grants.json` and `grants/newest_grants.json` for active calls with deadlines and award amounts.
3. Pay close attention to `applicant_types`, `eligible_regions`, and `agent_search_hints` in each funder entry to respect degree requirements, geographic restrictions, and application cycles.
4. Filter out opportunities that don't match the applicant's profile (e.g., distinguish between university-enrolled students and independent/non-degree autodidacts).
5. Produce a prioritized matching report with award ranges, direct application portals, and actionable next steps.
```

---

## 📜 License & Maintenance

Maintained as part of the `app-factory` multi-agent ecosystem. Open for community contributions of verified funding opportunities.
