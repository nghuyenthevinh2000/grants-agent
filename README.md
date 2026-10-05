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
├── grants/                        # 🔍 Core searchable databases
│   ├── funder_websites.json       # 139 funders across 10 categories, 120 sample programs + search hints
│   ├── newest_grants.json         # Granular, validated grant listings with deadlines & award amounts
│   └── README.md                  # Summary overview of latest discovered grants
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

| File | What It Contains | When An Agent Should Query It |
| :--- | :--- | :--- |
| [`grants/funder_websites.json`](grants/funder_websites.json) | 139 funding organizations, 120 specific program samples, discovery channels, applicant eligibility types, and specific `agent_search_hints`. | Broad discovery across tech, Web3, academia, and non-traditional funders (e.g. non-degree, travel, micro-grants). |
| [`grants/newest_grants.json`](grants/newest_grants.json) | Granular grant records with deadlines, exact award bounds ($ min/max), currency, application effort, and focus tags. | Pinpointing active application rounds, hard deadlines, and exact cash/compute awards. |

---

### 2. Fast Python Query Snippets for AI Agents

Agents can run these targeted scripts directly via terminal/command execution:

#### A. Search by Keywords & Focus Areas

```bash
python3 -c "
import json
from pathlib import Path

kw = 'quantum'  # Target keyword (e.g. quantum, travel, ai-safety, privacy)
path = Path('grants/funder_websites.json')

with open(path) as f:
    data = json.load(f)

matches = []
for funder in data.get('funders', []):
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
with open('grants/funder_websites.json') as f:
    data = json.load(f)

for f in data.get('funders', []):
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

Checks if a new funder already exists in `grants/funder_websites.json` using exact URL and fuzzy string matching:

```bash
python3 .agents/skills/grant-search/tools/check_funder_duplication.py grants/funder_websites.json
```

---

## 📋 Recommended Prompt for External AI Agents

When instructing another AI agent to look up funding opportunities in this repository, paste the following prompt:

```text
You have access to the grants intelligence database in `grants/`.
1. Inspect `grants/funder_websites.json` to find relevant funding organizations across categories (Government, Corporate, Philanthropy, Non-Traditional, Web3/Open Source).
2. Check `grants/newest_grants.json` for active calls with deadlines and award amounts.
3. Pay close attention to `applicant_types` and `agent_search_hints` in each funder entry to respect degree requirements, geographic restrictions, and application cycles.
4. Filter out opportunities that don't match the applicant's profile (e.g., distinguish between university-enrolled students and independent/non-degree autodidacts).
5. Produce a prioritized matching report with award ranges, direct application portals, and actionable next steps.
```

---

## 📜 License & Maintenance

Maintained as part of the `app-factory` multi-agent ecosystem. Open for community contributions of verified funding opportunities.
