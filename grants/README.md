# Grants & Funders Directory

This directory stores outputs and resources from the `grant-search` pipeline, organized by **Geographic Region**.

- **Regional Funder Databases**: 173 curated AI/tech grant funders partitioned into 10 regional folders (`<region>/funders.json`).
- **Latest Discovery Feed**: [`newest_grants.json`](newest_grants.json) – Feed of newly discovered grants across all regions.
- **Regional Summary Report**: [`regional_summary.json`](regional_summary.json) – Automated count and breakdown of grants and funders per region.

---

## Regional Directories

Each regional directory contains two synchronized resources:
1. `grants.json`: Verified active/rolling grant opportunities matching the region.
2. `funders.json`: Curated funding organizations, government agencies, corporate labs, and direct application portals based in or funding that region.

| Folder | Region Code | Scope & Tech Hubs | Grants Tracked | Funders & Portals |
| :--- | :--- | :--- | :--- | :--- |
| [`global/`](global/README.md) | `GLOBAL` | No geographic barrier; remote-friendly; Web3, AI safety, open-source | [8 grants](global/grants.json) | [46 funders](global/funders.json) |
| [`sea/`](sea/README.md) | `SEA` | Southeast Asia (Vietnam, Singapore, Indonesia, Thailand, Malaysia...) | [2 grants](sea/grants.json) | [5 funders](sea/funders.json) |
| [`north-america/`](north-america/README.md) | `NORTH_AMERICA` | United States and Canada (US Federal, NSF, DARPA, NSERC) | [1 grant](north-america/grants.json) | [100 funders](north-america/funders.json) |
| [`europe/`](europe/README.md) | `EUROPE` | EU member states, United Kingdom, Switzerland, Norway (Horizon, UKRI) | [0 grants](europe/grants.json) | [5 funders](europe/funders.json) |
| [`east-asia/`](east-asia/README.md) | `EAST_ASIA` | Japan, South Korea, China, Taiwan, Hong Kong (JSPS, NRF Korea, NSFC) | [0 grants](east-asia/grants.json) | [3 funders](east-asia/funders.json) |
| [`south-asia/`](south-asia/README.md) | `SOUTH_ASIA` | India, Pakistan, Bangladesh, Sri Lanka (SERB, BIRAC, MeitY) | [0 grants](south-asia/grants.json) | [2 funders](south-asia/funders.json) |
| [`mena/`](mena/README.md) | `MENA` | Middle East & North Africa (UAE, Saudi Arabia, Qatar, Israel, Egypt) | [0 grants](mena/grants.json) | [3 funders](mena/funders.json) |
| [`latam/`](latam/README.md) | `LATAM` | Latin America & Caribbean (Brazil, Mexico, Colombia, Chile, Argentina) | [0 grants](latam/grants.json) | [3 funders](latam/funders.json) |
| [`sub-saharan-africa/`](sub-saharan-africa/README.md) | `SUB_SAHARAN_AFRICA` | Sub-Saharan Africa (Nigeria, Kenya, South Africa, Rwanda, Ghana) | [0 grants](sub-saharan-africa/grants.json) | [3 funders](sub-saharan-africa/funders.json) |
| [`oceania/`](oceania/README.md) | `OCEANIA` | Australia, New Zealand, Pacific Islands (ARC, CSIRO, Callaghan) | [0 grants](oceania/grants.json) | [3 funders](oceania/funders.json) |

---

## Directory Layout

```
grants/
├── README.md                      # Central hub and regional index
├── newest_grants.json             # Global chronological discovery feed
├── global/
│   ├── README.md
│   ├── grants.json                # Grants open globally
│   └── funders.json               # Global funders (Web3, AI Safety, OSS)
├── sea/
│   ├── README.md
│   ├── grants.json                # Grants for Southeast Asia / Vietnam
│   └── funders.json               # Regional funders (VinIF, NAFOSTED, SG NRF)
├── north-america/
│   ├── README.md
│   ├── grants.json
│   └── funders.json               # US Federal, State, corporate labs
├── europe/
│   ├── README.md
│   ├── grants.json
│   └── funders.json               # Horizon Europe, UKRI, Wellcome Trust, ERC
├── east-asia/
│   ├── README.md
│   ├── grants.json
│   └── funders.json               # JSPS, NRF Korea, NSFC
├── south-asia/
│   ├── README.md
│   ├── grants.json
│   └── funders.json               # SERB, BIRAC
├── mena/
│   ├── README.md
│   ├── grants.json
│   └── funders.json               # KAUST, Dubai Future, IIA
├── latam/
│   ├── README.md
│   ├── grants.json
│   └── funders.json               # FAPESP, IDB Lab, Start-Up Chile
├── sub-saharan-africa/
│   ├── README.md
│   ├── grants.json
│   └── funders.json               # Lacuna Fund, AIMS, Google Africa
└── oceania/
    ├── README.md
    ├── grants.json
    └── funders.json               # ARC, CSIRO, Callaghan Innovation
```
