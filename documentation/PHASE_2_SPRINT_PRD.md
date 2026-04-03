# FloodVoice — Phase 2 Dashboard Sprint PRD

**Project:** FloodVoice AI — Emergency Response Dashboard  
**Owner:** Jessenia, Ethan, Erica, Josue, Kelvin, Shanell  
**Sprint Period:** April 2026  
**Last Updated:** April 3, 2026  
**Repository:** https://github.com/EricaR2D2/FloodVoice (branch: `production-nextjs`)  
**Builds On:** [Flood Voice Final PRD.md](./Flood%20Voice%20Final%20PRD.md) · [PRODUCTION_BUILD_STATUS.md](./PRODUCTION_BUILD_STATUS.md)

---

## Executive Summary

This document covers the features designed, built, and deployed to the FloodVoice dashboard during the Phase 2 sprint — the period of active development following the December 2025 demo. The sprint focused on three strategic goals:

1. **Deepen intelligence** — Move beyond raw sensor data to give liaisons and coordinators actionable, neighborhood-level flood risk context rooted in post-Ida damage data.
2. **Close the registration gap** — Build a formal, multilingual community intake form to replace the lightweight modal and capture the full data profile needed for emergency response.
3. **Improve operational usability** — Refine the dashboard with prioritized resident sorting, API health visibility, and a light/dark theme so it works in any field environment.

All features are live on the `production-nextjs` branch and require only the Supabase migration SQL to be run before the intake form can write to the database.

---

## Background

The December 2025 demo validated the core FloodVoice concept: AI-powered voice check-ins, real-time sentiment analysis, and Telegram distress alerts. Post-demo feedback and ongoing development identified several gaps:

| Gap Identified | Phase 2 Response |
|---|---|
| No neighborhood-level risk context | Built Flood Intelligence dashboard with True Risk Scores for 7 Ida pilot neighborhoods |
| Registration form was a basic modal with 6 fields | Built full standalone intake form with 6 sections, 4 languages, and 27 data fields |
| Residents sorted alphabetically, ignoring real-world risk | Added priority sort: Ida neighborhood tier → status urgency → alphabetical |
| FEMA zones not visible in dashboard | FEMA zone overlay added to Command Center map with zone classification legend |
| No visibility into API connection health | Built Settings page showing connection status of all integrated data sources |
| Dashboard had no accessibility theme | Added system-wide light/dark mode toggle |
| No consent mechanism for resident registration | Added consent section with typed signature and date to intake form |

---

## Phase 2 Features Built

### Feature 1 — Flood Intelligence Dashboard
**Route:** `/dashboard/intelligence`  
**Nav Label:** Flood Intelligence (Brain icon)

#### Problem
Liaisons and coordinators had sensor readings and call logs but no structured way to understand *which neighborhoods* were highest risk, *why*, and *what community resources* existed there. The FEMA flood zone map existed in isolation from the platform.

#### What Was Built
A four-panel intelligence hub that consolidates all flood risk data sources into one view:

**Panel A — NYC FloodNet Live Sensors**
- Links directly to the official [dataviz.floodnet.nyc](https://dataviz.floodnet.nyc) dashboard
- Explains the FEMA Zones toggle on the Command Center map
- Directs users to the correct tool for sensor deep-dives vs. operational response

**Panel B — FEMA Flood Zone Classification**
- Interactive legend for all four FEMA flood zone types:
  - `VE` — Coastal High Hazard (wave action + 1% annual flood risk)
  - `AE` — 100-Year Flood Zone (FEMA insurance required)
  - `AO/AH` — Shallow Flooding (1–3 ft sheet flow or ponding)
  - `X` — Minimal Hazard (outside 500-year floodplain)
- Contextualizes a critical insight: **80.4% of Hurricane Ida damage in NYC occurred in FEMA Zone X** — the zone classified as lowest risk — exposing a systemic gap in the federal flood model

**Panel C — Ida Priority Neighborhoods (True Risk Score)**
- 7 NYC pilot neighborhoods scored 0–100 via a weighted composite model
- Each neighborhood card displays:
  - True Risk Score with color-coded tier badge
  - FEMA gap warning flag (where Ida damage contradicted the zone designation)
  - Visual risk bar
  - Key stats: Ida damage rate, LEP population %, basement units at risk, FloodNet coverage
  - Primary language tags
  - CBO partner count and names
- Neighborhoods are pre-sorted: Tier 1 (Immediate) → Tier 2 (Near-term) → Tier 3 (Capacity-building)

**Panel D — Community Voice Reports**
- Feed of field reports from residents, liaisons, and community groups
- Each report shows: location, verbatim message, severity badge (Critical/Moderate/Low), reporter source, verification status, and timestamp
- Connects to the `community_reports` Supabase table when live data is available

#### True Risk Score Model
The composite score replaces FEMA zone classification as the primary risk signal:

| Factor | Weight | Data Source |
|---|---|---|
| Ida building damage rate | 30% | NYC post-Ida damage surveys |
| FEMA model gap (Zone X damage) | 25% | FEMA NFHL vs. actual damage records |
| Limited English Proficiency (LEP) population | 20% | ACS Census data |
| FloodNet sensor gap (inverse coverage) | 10% | NYC FloodNet API |
| Basement apartment density | 10% | NYC DOB + ACS estimates |
| Social vulnerability index | 5% | Poverty rate + foreign-born % |

#### 7 Pilot Neighborhoods (Phase 2 Scope)

| Neighborhood | Borough | Tier | True Risk Score |
|---|---|---|---|
| Flushing / Willets Point | Queens | 1 | 88 |
| Red Hook | Brooklyn | 1 | 85 |
| Hunts Point / Longwood | Bronx | 1 | 82 |
| Canarsie | Brooklyn | 2 | 74 |
| Jackson Heights / Corona | Queens | 2 | 71 |
| South Jamaica | Queens | 2 | 68 |
| East New York | Brooklyn | 3 | 61 |

---

### Feature 2 — Residents Pod Priority Sort
**Route:** `/dashboard/residents`

#### Problem
The resident roster sorted alphabetically, meaning a distressed resident in a Tier 1 Ida neighborhood could appear below a safe resident in a low-risk area. During an active flood event, visual scan time is critical.

#### What Was Built
A three-key sort applied automatically on every load and after every status update:

1. **Primary:** Ida neighborhood priority tier (Tier 1 residents appear first regardless of status)
2. **Secondary:** Status urgency — `distress` → `unresponsive` → `pending` → `safe`
3. **Tertiary:** Alphabetical by name (tiebreaker)

Each resident card now displays a **neighborhood tier badge** (pulled live from the `neighborhoods.ts` data layer by matching the resident's `zip_code`) showing the tier label and neighborhood name. Residents in unmapped zip codes display no badge and sort to the bottom.

---

### Feature 3 — Community Resident Intake / Registration Form
**Route:** `/dashboard/intake`  
**Nav Label:** Intake Form (ClipboardList icon)

#### Problem
The existing "Add Resident" UI was a small modal with 6 fields (name, phone, age, address, zip, health conditions). It did not capture: date of birth, next of kin, disability status, household size, contact preferences, consent, or liaison metadata. There was no consent mechanism and no multilingual support for field data collection.

#### What Was Built
A standalone full-page intake form that acts as a digital version of a community registration document. A liaison fills it out with the resident present — on a tablet, laptop, or desktop.

**Language Switcher**
Four tabs at the top of the form switch every label, placeholder, section header, privacy notice, consent text, and button instantly between:
- 🇺🇸 English
- 🇪🇸 Español
- 🇧🇩 বাংলা (Bengali)
- 🇨🇳 中文 (Mandarin)

No page reload. No external i18n library. All translations live in a single TypeScript constant object ported from the original HTML prototype.

**Form Sections**

| Section | Fields |
|---|---|
| **Section 1 — Personal Information** | Full name *, Date of birth *, Phone number *, Alternate phone, Email (optional) |
| **Section 2 — Household & Housing** | Home address *, Borough/ZIP *, Floor/apt #, Basement apartment (Y/N), # people in household * |
| **Section 3 — Emergency Contact** | Next of kin name *, Next of kin phone *, Relationship, Next of kin address (if different) |
| **Section 4 — Health & Access Needs** | Disability affecting evacuation (Y/N → reveals description field), Medical conditions (optional free text) |
| **Section 5 — Contact Preferences** | Preferred language (checkboxes: EN/ES/Bengali/Mandarin/Korean/Haitian Creole/Other), Contact method (Voice/SMS/Both), Best time to reach (Morning/Afternoon/Evening/Anytime) |
| **Section 6 — Consent** | Consent statement (translated per language tab), Typed signature *, Date * |
| **Liaison Use Only** | Liaison name, Organization, Registration date (auto-fills today), Neighborhood/pilot site, Form ID (auto-generated: `FV-YYYYMMDD-XXXX`) |

**Privacy Notice**
A prominent amber-bordered notice at the top of the form (translated in all 4 languages) stating explicitly that data is not shared with immigration authorities and the program serves all residents regardless of immigration status.

**Supabase Integration**
On submission, all fields save to the `residents` table. New fields require the `docs/migration_intake_form.sql` migration to be run first (one-time, non-destructive `ALTER TABLE`).

**Success State**
After a successful save, the submit button is replaced by a branded confirmation card with the translated success message.

---

### Feature 4 — FEMA Flood Zone Map Overlay
**Location:** Command Center (`/dashboard`) — interactive Mapbox map

#### What Was Built
- FEMA National Flood Hazard Layer (NFHL) polygons overlaid on the existing Mapbox flood sensor map
- Toggle button labeled **FEMA Zones** allows liaisons to show/hide the overlay without leaving the Command Center
- Zone fill colors match the legend in the Flood Intelligence panel (VE = red, AE = blue, AO/AH = purple, X = gray)
- Graceful fallback if the Mapbox token is missing or the FEMA GeoJSON fails to load

---

### Feature 5 — Settings Page — API Health Dashboard
**Route:** `/dashboard/settings`

#### What Was Built
A connection status panel displaying the live health of every integrated data source:

| Source | Status |
|---|---|
| Supabase | ✅ Connected |
| NYC FloodNet | ✅ Connected (public API, no key required) |
| Vapi (Voice AI) | Configured via env |
| Google Gemini | Configured via env |
| Telegram Bot | Configured via env |
| FEMA Flood Zones | ✅ Connected |
| NYC FVI (Flood Vulnerability Index) | Coming Soon |
| Social Media Sources (Twitter, Facebook) | Coming Soon |

Each card shows the service name, description, connection status badge, the relevant environment variable name, and any relevant notes.

---

### Feature 6 — Light / Dark Mode Theme
**Location:** Sidebar toggle (Sun/Moon icon), all dashboard pages

#### What Was Built
- System-wide CSS custom property theming (`--bg-primary`, `--text-primary`, `--text-secondary`, etc.)
- `ThemeProvider` context wrapping the entire app
- `useTheme()` hook available to any component
- Toggle persists across the session
- All dashboard pages, glass panels, cards, and charts respect the active theme

---

## Updated Database Schema

The `residents` table now supports 27 fields after the Phase 2 intake migration:

```sql
-- Core fields (existed pre-Phase 2)
residents (
  id, liaison_id, name, phone_number, age, address,
  health_conditions, zip_code, language, status,
  vapi_assistant_id, created_at
)

-- New fields added in Phase 2 (docs/migration_intake_form.sql)
  date_of_birth DATE,
  alternate_phone TEXT,
  email TEXT,
  floor_apt TEXT,
  basement_apartment BOOLEAN,
  household_size INTEGER,
  next_of_kin_name TEXT,
  next_of_kin_phone TEXT,
  next_of_kin_relationship TEXT,
  next_of_kin_address TEXT,
  has_disability BOOLEAN,
  disability_description TEXT,
  preferred_languages TEXT,       -- comma-separated e.g. "English, Bengali"
  contact_method TEXT,            -- 'call' | 'sms' | 'both'
  best_time_to_reach TEXT,        -- 'morning' | 'afternoon' | 'evening' | 'anytime'
  consent_signature TEXT,
  consent_date DATE,
  liaison_name TEXT,
  liaison_org TEXT,
  registration_date DATE,
  neighborhood TEXT,
  form_id TEXT                    -- auto-generated: FV-YYYYMMDD-XXXX
```

**Migration file:** `docs/migration_intake_form.sql`  
**Action required:** Run once in Supabase SQL Editor before using the intake form submit button.

---

## Updated Navigation Structure

```
/dashboard              Command Center       (LayoutDashboard)
/dashboard/calls        Live Calls           (Phone)
/dashboard/residents    Residents Pod        (Users)
/dashboard/intake       Intake Form  ← NEW  (ClipboardList)
/dashboard/intelligence Flood Intelligence   (Brain)
/dashboard/settings     Settings             (Settings)
```

---

## Updated Implementation Status

### Registration & Onboarding

| Feature | Status Before | Status After Phase 2 |
|---|---|---|
| Add Residents | ✅ Modal (6 fields) | ✅ Full intake form (27 fields) |
| Multilingual registration | ❌ Not implemented | ✅ EN / ES / BN / ZH |
| Date of birth capture | ❌ Not implemented | ✅ Implemented |
| Next of kin collection | ❌ Not implemented | ✅ Implemented |
| Disability & access needs | ❌ Not implemented | ✅ Implemented (Y/N + description) |
| Contact preferences | ❌ Not implemented | ✅ Implemented (method + best time) |
| Consent mechanism | ❌ Not implemented | ✅ Typed signature + date |
| Privacy notice | ❌ Not implemented | ✅ Translated in all 4 languages |
| Liaison attestation fields | ❌ Not implemented | ✅ Liaison name, org, Form ID |
| Household size | ❌ Not implemented | ✅ Implemented |

### Intelligence & Context

| Feature | Status Before | Status After Phase 2 |
|---|---|---|
| Neighborhood risk scoring | ❌ Not implemented | ✅ True Risk Score for 7 neighborhoods |
| FEMA gap analysis | ❌ Not implemented | ✅ Implemented (Zone X Ida data) |
| CBO partner data | ❌ Not implemented | ✅ Implemented per neighborhood |
| Community Voice reports | ❌ Not implemented | ✅ Implemented (demo + live table) |
| FEMA zone map overlay | ❌ Not implemented | ✅ Toggle on Command Center map |
| LEP population data | ❌ Not implemented | ✅ Per-neighborhood % and languages |
| Resident priority sorting | ❌ Alphabetical only | ✅ Tier → urgency → alphabetical |
| Neighborhood badge on resident cards | ❌ Not implemented | ✅ Tier badge with neighborhood name |

### Platform & Operations

| Feature | Status Before | Status After Phase 2 |
|---|---|---|
| Light / Dark mode | ❌ Dark only | ✅ Toggle via sidebar |
| Settings / API health page | ❌ Not implemented | ✅ Implemented |
| Graceful error handling | ⚠️ Partial | ✅ Mapbox + Supabase fallbacks |
| Demo seed data | ⚠️ Partial | ✅ Full schema + 4-neighborhood seed |

---

## Features Still Deferred (Phase 3 Roadmap)

| Feature | Notes |
|---|---|
| **One-Click 911 Escalation** | Manual escalation only. Requires carrier integration or Twilio |
| **Liaison Network / Pod Discovery** | No nearby liaison discovery. Requires geospatial search feature |
| **Multi-language Voice Calls** | `language` field stored and passed to Vapi; runtime language switching not confirmed |
| **FVI (Flood Vulnerability Index) Integration** | NYC Open Data FVI scores not yet wired to resident profiles |
| **Social Media Ingestion** | Twitter/Facebook/community group monitoring listed in Settings as "Coming Soon" |
| **Community Reports — Live Submission** | Community Voice panel shows demo data; live `community_reports` Supabase table needs a public intake endpoint |
| **Intake Form — Public URL** | Currently requires dashboard login. A public-facing, unauthenticated version for CBOs is a Phase 3 candidate |
| **Print / PDF Export of Intake Form** | Field liaisons may need a paper backup. Browser print CSS or PDF generation (e.g., React-PDF) not yet built |
| **Duplicate Resident Detection** | No check for existing phone number on intake form submit |

---

## Technical Notes

### Key Files Added / Modified

| File | Change |
|---|---|
| `src/app/dashboard/intake/page.tsx` | New — full intake form component (450 lines) |
| `src/app/dashboard/intelligence/page.tsx` | New — 4-panel Flood Intelligence dashboard |
| `src/app/dashboard/settings/page.tsx` | New — API health status cards |
| `src/app/dashboard/layout.tsx` | Modified — added Intake Form nav item + ClipboardList icon |
| `src/app/dashboard/residents/page.tsx` | Modified — priority sort + neighborhood tier badges |
| `src/lib/neighborhoods.ts` | New — 7-neighborhood data layer with True Risk Score model |
| `docs/migration_intake_form.sql` | New — 22-column `ALTER TABLE` for residents table |
| `docs/schema.sql` | Updated — complete schema with Phase 2 tables |
| `docs/seed_demo_data.sql` | Updated — realistic demo data for 4 NYC neighborhoods |

### Dependency Notes
- No new npm packages were added in Phase 2
- Bengali text rendering relies on the system font stack (no Noto Sans Bengali loaded — acceptable for labels, may need attention for body text)
- The `FloodVoice Intake Code.txt` HTML prototype is archived in the repo root for reference

---

## Action Required Before Next Demo

1. **Run the Supabase migration** — Open `docs/migration_intake_form.sql` in Supabase SQL Editor and execute. This is a one-time, non-destructive operation that enables the intake form to save all 27 fields.
2. **Verify Mapbox token** — Confirm `NEXT_PUBLIC_MAPBOX_TOKEN` is set in the Vercel environment for the FEMA zone overlay to render.
3. **Seed demo data** — Run `docs/seed_demo_data.sql` if starting fresh to populate the dashboard with realistic resident and call log data.

---

*For the original platform PRD, see `documentation/Flood Voice Final PRD.md`*  
*For the December 2025 demo build status, see `documentation/PRODUCTION_BUILD_STATUS.md`*
