# Process New Grant (Stage 2)

Stage 2 of the grant pipeline. Input: entries staged in `potential_new_grants.json` by the discovery skill ([SKILLS.md](SKILLS.md)). Output: verified entries appended to `found_grants.json`. Staged entries may carry a discovery-only `source_category` field — strip it before appending.

This file is the **single source of truth for the grant schema**. Add each grant to `found_grants.json` following this structure:

## Grant Entry Schema

```json
{
  "id": "unique-identifier",
  "name": "Grant Name",
  "applicant_need": "personal_stipend|student_support|research_project|lab_operations|org_operations|startup_capital|infrastructure|competition_prize|community_support|conference_travel|compute_access|mixed",
  "source": {
    "name": "Organization/Website",
    "url": "https://link-to-grant",
    "discovered_date": "2026-04-19",
    "source_type": "website|email|recommendation|partnership"
  },
  "award": {
    "type": "cash|gpu|equity-waiver|other",
    "min_amount": 0,
    "max_amount": 0,
    "currency": "USD",
    "gpu_type": "H100|A100|L40S|T4|other",
    "gpu_count": 0
  },
  "deadline": "YYYY-MM-DD | Rolling | TBD",
  "eligibility": {
    "stage": ["early-stage", "growth", "all"],
    "team_size_min": 0,
    "team_size_max": null,
    "geography": ["GLOBAL", "SEA", "NORTH_AMERICA"],
    "restrictions": "501(c)(3) required, founders only, etc.",
    "eligibility_checks": ["first-time", "women-led", "underrepresented", "none", "other - short sentence explanation"]
  },
  "requirements": {
    "key_requirements": ["Live demo", "Financial statements", "Product roadmap"],
    "focus_areas": ["AI safety", "Open source", "Foundation model development"]
  },
  "recurring": "yearly|quarterly|one-time|anytime|no|other",
  "notes": "Any additional context, red flags, or opportunities",
  "tags": ["gpu-focused", "fast-process", "philanthropy"]
}
```

## Field Descriptions

### Core Fields

- **id**: Unique identifier (use format: `grant-org-date`, e.g., `grant-openai-202604`)
- **name**: Official grant program name as published by the funder
- **source**: Metadata about where and when the grant was discovered
- **award**: Type and amount of funding or resources offered
- **deadline**: Application deadline as `YYYY-MM-DD`, or `Rolling` / `TBD`
- **eligibility**: Constraints on who can apply based on company stage, size, location, or other criteria
- **requirements**: Application documents, submission steps, specific deliverables, and focus areas required after eligibility is confirmed
- **applicant_need**: What problem/need does this grant solve? When in a career/org lifecycle would someone apply?
  - **Classification heuristic**: Answer "WHEN would I apply to this grant?"
    - `personal_stipend`: Fellowship, personal career funding (e.g., Microsoft Research Fellowship $17K) (possibly also with compute access)
    - `student_support`: PhD/postdoc support, grad student awards (e.g., NSF GRFP)
    - `research_project`: Specific research with deliverables (e.g., Amazon Research Awards)
    - `lab_operations`: Running existing lab (e.g., NSF CAREER, sustained research)
    - `org_operations`: Running organization/nonprofit (e.g., Google.org Impact grants)
    - `startup_capital`: Seed funding for new company (e.g., Y Combinator, accelerators)
    - `infrastructure`: Building centers, facilities (e.g., NSF Engineering Centers $10M+)
    - `competition_prize`: Winning competitions (e.g., XPRIZE, ARC Prize)
    - `community_support`: Open source, community projects (e.g., GitHub Sponsors)
    - `conference_travel`: Conference attendance support (e.g., travel grants)
    - `compute_access`: GPU/cloud resources (e.g., OpenAI Researcher Access)
    - `mixed`: Covers multiple needs (e.g., fellowship with project funding + travel)
  - **Key distinction**: This is NOT about eligibility, but about APPLICANT STAGE/NEED
    - Same person might apply as: student_support → personal_stipend → research_project → lab_operations
    - Clarifies: "I'm in situation X, which grants should I look at?"

- **recurring**: Beyond the current deadline, will there be new deadlines in known frequencies?
  - **Classification heuristic**:
    - `yearly`: Fellowship programs, annual cycles, named "(20XX)" or "(cycle Y)", funder history shows annual rounds
    - `quarterly`: Explicitly stated rolling rounds, "every quarter", fund refresh cycles
    - `anytime`: "Rolling", no deadline stated, continuous applications, ongoing platforms
    - `one-time`: Challenge ends explicitly, sunset date stated, "first/inaugural", no history of repeats
    - When in doubt, check funder's past cycles or mark as `yearly` for named fellowships/awards
- **notes**: Any additional context, clarifications, or observations
- **tags**: Searchable keywords for filtering and categorization

### Source Object

- **name**: Organization name or program name offering the grant
- **url**: Direct URL to grant details or application portal
- **discovered_date**: ISO date when the grant was first identified (YYYY-MM-DD)
- **source_type**: Channel of discovery: `website`, `email`, `recommendation`, or `partnership`

### Award Object

- **type**: Primary award type: `cash`, `gpu`, `equity-waiver`, or `other`
- **min_amount/max_amount**: Numeric funding range in the specified currency (0 if not applicable)
- **currency**: Currency code (e.g., "USD")
- **gpu_type**: GPU model if applicable: `H100`, `A100`, `L40S`, `T4`, or `other`
- **gpu_count**: Number of GPUs offered (0 if N/A)

### Eligibility Object

- **stage**: Company stages eligible: `early-stage`, `growth`, or `all`
- **team_size_min**: Minimum team size required (integer)
- **team_size_max**: Maximum team size allowed (null for no limit)
- **geography**: List of eligible region codes from the standard taxonomy:
  - `GLOBAL`: Open worldwide / remote-friendly (Web3, AI safety, open source)
  - `SEA`: Southeast Asia (Vietnam, Singapore, Indonesia, Thailand, Malaysia, etc.)
  - `EAST_ASIA`: East Asia (Japan, South Korea, China, Taiwan, Hong Kong)
  - `SOUTH_ASIA`: South Asia (India, Pakistan, Bangladesh, Sri Lanka)
  - `MENA`: Middle East & North Africa (UAE, Saudi Arabia, Qatar, Israel, Egypt, Morocco)
  - `NORTH_AMERICA`: United States & Canada (US Federal, NSF, DARPA, NSERC)
  - `EUROPE`: European Union, UK, Switzerland, Norway (Horizon Europe, UKRI)
  - `LATAM`: Latin America & Caribbean (Brazil, Mexico, Colombia, Chile, Argentina)
  - `SUB_SAHARAN_AFRICA`: Sub-Saharan Africa (Nigeria, Kenya, South Africa, Rwanda, Ghana)
  - `OCEANIA`: Australia, New Zealand, Pacific Islands
  - *Modifiers*: `CROSS_BORDER`, `BILATERAL`
- Regional folders are stored under `grants/<region-slug>/` (`global/`, `sea/`, `north-america/`, etc.).
- **restrictions**: Specific disqualifying factors or requirements (e.g., "501(c)(3) required")
- **eligibility_checks**: List of special criteria such as `first-time`, `women-led`, `underrepresented`, `none`, or descriptive text

### Requirements Object

- **key_requirements**: Specific deliverables or documents needed (e.g., "Live demo", "Financial statements")
- **focus_areas**: Stated funding priorities or research areas (e.g., "AI safety", "Open source")

## Duplicate Detection Rules

Before adding a new grant, check:

1. **Exact duplicates**: Same grant, same source (skip - already recorded)
2. **Related grants**: Same program, different year/round (add as separate entry, link in notes)
3. **Similar from different sources**: Different organizations offering same type of funding (add - multiple sources allowed)
4. **Rebranded programs**: Grant renamed or restructured (add new entry, note in `notes` field)
5. **Expired one-time grants**: If `recurring` is `"one-time"` and deadline is in the past, **DO NOT ADD** (grant is expired and no longer actionable)

## Example Entry

```json
{
  "id": "grant-openai-202604",
  "name": "OpenAI Startup Fund",
  "applicant_need": "startup_capital",
  "source": {
    "name": "OpenAI",
    "url": "https://openai.com/grants",
    "discovered_date": "2026-04-19",
    "source_type": "website"
  },
  "award": {
    "type": "cash",
    "min_amount": 10000,
    "max_amount": 1000000,
    "currency": "USD",
    "gpu_type": null,
    "gpu_count": null
  },
  "deadline": "2026-06-30",
  "eligibility": {
    "stage": ["early-stage", "growth"],
    "team_size_min": 1,
    "team_size_max": null,
    "geography": ["US"],
    "restrictions": "Must be building with OpenAI models",
    "eligibility_checks": []
  },
  "requirements": {
    "key_requirements": ["Live product", "User traction", "Use of GPT API"],
    "focus_areas": ["AI applications", "Productivity", "Developer tools"]
  },
  "recurring": "yearly",
  "notes": "Non-dilutive funding. Relatively quick review process. May include GPU credits.",
  "tags": ["cash", "non-dilutive", "fast-track"]
}
```

## Applicant Need Classification Reference

When classifying grants by `applicant_need`, use these rules:

- **Impact Challenge/Prize** → `research_project` (NOT competition_prize)
- **XPRIZE/ARC Prize/Competitions** → `competition_prize`
- **GPU/compute/cloud credits** → `compute_access`
- **Travel/conference grants** → `conference_travel`
- **Fellowship + <$200K** → `personal_stipend`
- **Graduate/postdoc/PhD support** → `student_support`
- **Nonprofit + >$500K** → `org_operations`, else → `research_project`
- **Founder/startup** → `startup_capital`
- **University/academic + >$500K** → `lab_operations`, else → `research_project`
- **Open source/community/GitHub** → `community_support`
- **Center/institute + >$1M** → `infrastructure`
- **Unclear/multiple categories** → `mixed`

## Grant Addition Workflow

**Before adding new grants to `found_grants.json`, follow this multi-step verification process:**

1. **Check for duplicates** (see Duplicate Detection Rules above)
2. **Load staged entries** from `potential_new_grants.json` (produced by [SKILLS.md](SKILLS.md)); strip `source_category`
3. **Validate schema**: Verify JSON structure matches the Grant Entry Schema
4. **Verify content**: Use LLM to review:
   - applicant_need classification accuracy
   - deadline format and logic (YYYY-MM-DD or "Rolling")
   - eligibility constraints make sense
   - award amounts are realistic
   - required fields are present
5. **Fix any issues** in staging before appending
6. **Append to found_grants.json** only after verification passes

**Scripts (located in `tools/`; run from this skill directory or project root, `found_grants.json` is automatically resolved):**

- `python tools/is_existing.py --check <entries.json> [found_grants.json]` - Intelligent duplicate check against `found_grants.json` (ID, exact name/org, normalized URL, fuzzy name/org). Exits with code 1 if any duplicate is found.
- `python tools/validate_grant_schema.py <file.json>` - Schema validation. Verifies required fields and types, valid date formats (`YYYY-MM-DD`, `Rolling`, or `TBD`), and allows nullable optional fields.
- `python tools/append_verified_grants.py <staging.json> [target.json]` - Validates schema, checks duplicates via `GrantDuplicateChecker`, strips `source_category`, normalizes defaults, appends to `found_grants.json`, updates metadata, and cleans up the staging file.

`found_grants.json` has the shape `{"schema_version", "total_grants", "last_updated", "grants": [...]}`. Staging files may be a bare array or `{"grants": [...]}`.

## Questions to Ask When Processing

- ✓ Is this a duplicate of something already tracked?
- ✓ Is this a one-time grant with a deadline in the past? (If yes, skip — expired)
- ✓ Does the JSON schema match the Grant Entry Schema exactly?
- ✓ Are all required fields present and correctly typed?
- ✓ Is the applicant_need classification semantically correct?
- ✓ What's the effort-to-reward ratio?
- ✓ Are there any red flags or unusual requirements?
- ✓ When is the deadline relative to our current priorities?
- ✓ Could this source provide ongoing opportunities?
