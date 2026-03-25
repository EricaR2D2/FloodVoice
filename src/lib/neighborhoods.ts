/**
 * src/lib/neighborhoods.ts
 *
 * Single source of truth for the 7 Hurricane Ida priority neighborhoods
 * identified in the NYC Community Flood Triage Pilot report.
 *
 * Powers:
 *   - Mapbox neighborhood zone overlay (flood-map.tsx)
 *   - Community Segment Dashboard (intelligence/page.tsx)
 *   - Resident Alert List priority sort (residents/page.tsx)
 *
 * Scoring: true_risk_score (0–100) is a weighted composite of Ida damage data,
 * FEMA model gaps, language access barriers, FloodNet sensor gaps, basement
 * apartment density, and social vulnerability. It differs intentionally from
 * FEMA zone classification — 80.4 % of Ida damage occurred in FEMA Zone X.
 */

// ─── Types ───────────────────────────────────────────────────────────────────

export type FloodnetCoverage = 'none' | 'minimal' | 'moderate' | 'good' | 'high';
export type PilotStatus     = 'immediate' | 'near_term' | 'capacity_building';
export type PriorityTier    = 1 | 2 | 3;

export interface CboPartner {
    name:      string;
    type:      string;
    languages: string[];
}

export interface RiskInputs {
    /** 1–10  Normalized from Ida building damage rate %. Weight: 30 % */
    damage_rate_score:          number;
    /** 1–10  Degree to which FEMA underestimates this neighborhood. Weight: 25 % */
    fema_gap_score:             number;
    /** 1–10  Limited-English-Proficiency population share. Weight: 20 % */
    lep_score:                  number;
    /** 1–10  INVERSE of FloodNet coverage — 10 = no sensors, 1 = full. Weight: 10 % */
    sensor_gap_score:           number;
    /** 1–10  Estimated basement apartment density. Weight: 10 % */
    basement_density_score:     number;
    /** 1–10  Poverty rate + foreign-born % + socioeconomic fragility. Weight: 5 % */
    social_vulnerability_score: number;
}

export interface IdaNeighborhood {
    id:                   string;
    name:                 string;
    community_district:   string;
    borough:              'Queens' | 'Brooklyn' | 'Bronx' | 'Manhattan' | 'Staten Island';
    /** 1 = Immediate pilot · 2 = Near-term · 3 = Capacity-building */
    priority_tier:        PriorityTier;
    pilot_status:         PilotStatus;
    /** Composite 0–100. Calculated via calculateTrueRiskScore(). */
    true_risk_score:      number;
    /** FEMA zone as officially designated (commonly Zone X for Ida-hit areas) */
    fema_designated_zone: string;
    /** true when significant Ida damage occurred despite Zone X or low-hazard designation */
    fema_gap_flag:        boolean;
    /** Mapbox center as [lng, lat] */
    coordinates:          [number, number];
    map_zoom:             number;
    /** ZIP codes — used to map residents → neighborhoods */
    zip_codes:            string[];
    ida_impact: {
        damaged_buildings:     number;
        local_damage_rate_pct: number;
        /** null when no direct fatalities were recorded in this neighborhood */
        fatalities:            number | null;
        /** % of Ida damage inside FEMA Special Flood Hazard Areas */
        in_fema_sfha_pct:      number;
    };
    demographics: {
        total_population:  number;
        foreign_born_pct:  number;
        /** % speaking a language other than English at home */
        lep_pct:           number;
        primary_languages: string[];
        key_communities:   string[];
    };
    infrastructure: {
        /** null when no systematic estimate exists */
        basement_units_at_risk:   number | null;
        sewer_capacity_gap:       boolean;
        floodnet_coverage:        FloodnetCoverage;
        floodnet_sensor_count_est: number;
    };
    cbo_partners:            CboPartner[];
    risk_inputs:             RiskInputs;
    policy_notes:            string;
    /** FloodNet reading in inches at which neighborhood-wide alerts should fire */
    alert_threshold_depth_in: number;
}

// ─── Scoring Engine ───────────────────────────────────────────────────────────

export const SCORING_WEIGHTS = {
    damage_rate:          0.30,
    fema_gap:             0.25,
    lep:                  0.20,
    sensor_gap:           0.10,
    basement_density:     0.10,
    social_vulnerability: 0.05,
} as const;

/**
 * Returns a True Risk Score (0–100) from raw risk inputs.
 * An optional live FloodNet depth reading adds a real-time surge bonus (≤ +5).
 */
export function calculateTrueRiskScore(inputs: RiskInputs, liveDepthIn = 0): number {
    const base =
        inputs.damage_rate_score          * SCORING_WEIGHTS.damage_rate +
        inputs.fema_gap_score             * SCORING_WEIGHTS.fema_gap +
        inputs.lep_score                  * SCORING_WEIGHTS.lep +
        inputs.sensor_gap_score           * SCORING_WEIGHTS.sensor_gap +
        inputs.basement_density_score     * SCORING_WEIGHTS.basement_density +
        inputs.social_vulnerability_score * SCORING_WEIGHTS.social_vulnerability;

    // Live surge: sensor reading > 2 in adds up to +5 points
    const surge = liveDepthIn > 2 ? Math.min((liveDepthIn - 2) * 1.25, 5) : 0;
    return Math.min(Math.round((base + surge) * 10), 100);
}

// ─── Neighborhood Data ────────────────────────────────────────────────────────

export const IDA_NEIGHBORHOODS: IdaNeighborhood[] = [

    // ── 1. Woodside / Sunnyside — TIER 1 · IMMEDIATE ─────────────────────────
    // Highest priority: most direct Ida fatalities; 6.66 % damage rate in FEMA Zone X.
    {
        id:                   'woodside-sunnyside',
        name:                 'Woodside / Sunnyside',
        community_district:   'Queens CD2',
        borough:              'Queens',
        priority_tier:        1,
        pilot_status:         'immediate',
        true_risk_score:      86,
        fema_designated_zone: 'X',
        fema_gap_flag:        true,
        coordinates:          [-73.9021, 40.7452],
        map_zoom:             13,
        zip_codes:            ['11104', '11377'],
        ida_impact: {
            damaged_buildings:     789,
            local_damage_rate_pct: 6.66,
            fatalities:            3,
            in_fema_sfha_pct:      0,
        },
        demographics: {
            total_population:  165_000,
            foreign_born_pct:  60.2,
            lep_pct:           55.0,
            primary_languages: ['Chinese', 'Tagalog', 'Bengali', 'Korean', 'Spanish', 'English'],
            key_communities:   ['Chinese', 'Bangladeshi', 'Filipino', 'Korean'],
        },
        infrastructure: {
            basement_units_at_risk:    null,
            sewer_capacity_gap:        true,
            floodnet_coverage:         'moderate',
            floodnet_sensor_count_est: 8,
        },
        cbo_partners: [
            { name: 'Queens Community House', type: 'Social services',    languages: ['English', 'Spanish', 'Chinese'] },
            { name: 'Philippine Forum',        type: 'Immigrant services', languages: ['Tagalog', 'English'] },
            { name: 'Korean Community Services', type: 'Immigrant services', languages: ['Korean', 'English'] },
        ],
        risk_inputs: {
            damage_rate_score:          9,
            fema_gap_score:             10,
            lep_score:                  8,
            sensor_gap_score:           6,
            basement_density_score:     8,
            social_vulnerability_score: 8,
        },
        policy_notes:             'Highest pilot priority. Most direct Ida fatalities. Council Member Julie Won engaged DEP on sewer upgrades. FloodNet sensors actively being deployed.',
        alert_threshold_depth_in: 2,
    },

    // ── 2. Flushing / Murray Hill — TIER 1 · IMMEDIATE ───────────────────────
    // Highest absolute damage count in NYC (2,357 buildings). 70.9 % non-English at home.
    {
        id:                   'flushing-murray-hill',
        name:                 'Flushing / Murray Hill',
        community_district:   'Queens CD7',
        borough:              'Queens',
        priority_tier:        1,
        pilot_status:         'immediate',
        true_risk_score:      75,
        fema_designated_zone: 'X',
        fema_gap_flag:        true,
        coordinates:          [-73.8330, 40.7678],
        map_zoom:             13,
        zip_codes:            ['11354', '11355', '11358', '11365', '11366'],
        ida_impact: {
            damaged_buildings:     2_357,
            local_damage_rate_pct: 4.83,
            fatalities:            null,
            in_fema_sfha_pct:      5,
        },
        demographics: {
            total_population:  247_000,
            foreign_born_pct:  57.4,
            lep_pct:           70.9,
            primary_languages: ['Korean', 'Chinese (Mandarin)', 'Chinese (Cantonese)', 'Spanish', 'English'],
            key_communities:   ['Korean', 'Chinese'],
        },
        infrastructure: {
            basement_units_at_risk:    null,
            sewer_capacity_gap:        true,
            floodnet_coverage:         'high',
            floodnet_sensor_count_est: 14,
        },
        cbo_partners: [
            { name: 'MinKwon Center for Community Action', type: 'Immigrant services', languages: ['Korean', 'English'] },
            { name: 'Chinese Community Center',            type: 'Social services',    languages: ['Chinese (Mandarin)', 'Chinese (Cantonese)', 'English'] },
            { name: 'NY Sea Grant',                        type: 'Resilience research', languages: ['English'] },
        ],
        risk_inputs: {
            damage_rate_score:          7,
            fema_gap_score:             9,
            lep_score:                  9,
            sensor_gap_score:           3,
            basement_density_score:     7,
            social_vulnerability_score: 7,
        },
        policy_notes:             'Highest absolute damage count in all of NYC. High LEP rate among Korean Americans raises communication barriers. Strong CBO presence enables rapid outreach.',
        alert_threshold_depth_in: 2,
    },

    // ── 3. Elmhurst / Corona — TIER 1 · IMMEDIATE ────────────────────────────
    // ~1,885 damaged buildings; 11,000 basement units explicitly at risk.
    {
        id:                   'elmhurst-corona',
        name:                 'Elmhurst / Corona',
        community_district:   'Queens CD3–4',
        borough:              'Queens',
        priority_tier:        1,
        pilot_status:         'immediate',
        true_risk_score:      83,
        fema_designated_zone: 'X',
        fema_gap_flag:        true,
        coordinates:          [-73.8696, 40.7406],
        map_zoom:             13,
        zip_codes:            ['11368', '11369', '11373'],
        ida_impact: {
            damaged_buildings:     1_885,
            local_damage_rate_pct: 6.31,
            fatalities:            null,
            in_fema_sfha_pct:      3,
        },
        demographics: {
            total_population:  180_000,
            foreign_born_pct:  62.0,
            lep_pct:           65.0,
            primary_languages: ['Spanish', 'Chinese', 'Punjabi', 'Urdu', 'English'],
            key_communities:   ['Latino', 'South Asian', 'Sikh'],
        },
        infrastructure: {
            basement_units_at_risk:    11_000,
            sewer_capacity_gap:        true,
            floodnet_coverage:         'good',
            floodnet_sensor_count_est: 12,
        },
        cbo_partners: [
            { name: 'Make the Road New York', type: 'Immigrant & legal services', languages: ['Spanish', 'English'] },
            { name: 'United Sikhs',            type: 'Disaster relief',           languages: ['Punjabi', 'English'] },
        ],
        risk_inputs: {
            damage_rate_score:          8,
            fema_gap_score:             9,
            lep_score:                  9,
            sensor_gap_score:           5,
            basement_density_score:     9,
            social_vulnerability_score: 9,
        },
        policy_notes:             '11,000 basement units explicitly documented at risk. Make the Road NY has 24,000+ members here. New community center under construction as resilience hub.',
        alert_threshold_depth_in: 2,
    },

    // ── 4. Canarsie / Flatlands — TIER 2 · NEAR-TERM ─────────────────────────
    // Faces both coastal AE-zone risk and inland stormwater. Limited FloodNet coverage.
    {
        id:                   'canarsie-flatlands',
        name:                 'Canarsie / Flatlands',
        community_district:   'Brooklyn CD18',
        borough:              'Brooklyn',
        priority_tier:        2,
        pilot_status:         'near_term',
        true_risk_score:      58,
        fema_designated_zone: 'AE / X',
        fema_gap_flag:        true,
        coordinates:          [-73.9270, 40.6379],
        map_zoom:             13,
        zip_codes:            ['11234', '11236'],
        ida_impact: {
            damaged_buildings:     1_280,
            local_damage_rate_pct: 3.80,
            fatalities:            null,
            in_fema_sfha_pct:      35,
        },
        demographics: {
            total_population:  95_000,
            foreign_born_pct:  42.0,
            lep_pct:           32.0,
            primary_languages: ['English', 'Haitian Creole', 'Spanish', 'French'],
            key_communities:   ['Black', 'Caribbean-American'],
        },
        infrastructure: {
            basement_units_at_risk:    null,
            sewer_capacity_gap:        true,
            floodnet_coverage:         'minimal',
            floodnet_sensor_count_est: 3,
        },
        cbo_partners: [
            { name: 'CCDI (Caribbean Cultural Center Dance Institute)', type: 'Cultural & community org', languages: ['English', 'Haitian Creole'] },
            { name: 'SRIJB (Southeast Brooklyn)',                       type: 'Resilience coalition',    languages: ['English', 'Spanish'] },
        ],
        risk_inputs: {
            damage_rate_score:          6,
            fema_gap_score:             5,
            lep_score:                  5,
            sensor_gap_score:           8,
            basement_density_score:     6,
            social_vulnerability_score: 7,
        },
        policy_notes:             'Historically impacted by Sandy; now faces combined stormwater and coastal risks. Land subsidence and outdated FEMA maps compound risk. FloodNet coverage expanding.',
        alert_threshold_depth_in: 2,
    },

    // ── 5. East New York / Jewel Streets — TIER 2 · NEAR-TERM ────────────────
    // Structural exclusion: no sewer access. Endemic groundwater flooding. Minimal sensors.
    {
        id:                   'east-new-york',
        name:                 'East New York / Jewel Streets',
        community_district:   'Brooklyn CD5',
        borough:              'Brooklyn',
        priority_tier:        2,
        pilot_status:         'near_term',
        true_risk_score:      72,
        fema_designated_zone: 'X',
        fema_gap_flag:        true,
        coordinates:          [-73.8827, 40.6680],
        map_zoom:             13,
        zip_codes:            ['11207', '11208'],
        ida_impact: {
            damaged_buildings:     698,
            local_damage_rate_pct: 3.50,
            fatalities:            null,
            in_fema_sfha_pct:      0,
        },
        demographics: {
            total_population:  110_000,
            foreign_born_pct:  38.0,
            lep_pct:           48.0,
            primary_languages: ['Spanish', 'Haitian Creole', 'English'],
            key_communities:   ['Latino', 'Haitian'],
        },
        infrastructure: {
            basement_units_at_risk:    null,
            sewer_capacity_gap:        true,
            floodnet_coverage:         'minimal',
            floodnet_sensor_count_est: 2,
        },
        cbo_partners: [
            { name: 'East New York Community Land Trust', type: 'Housing & legal',   languages: ['Spanish', 'English'] },
            { name: 'Legal Aid Society ENY',              type: 'Legal services',    languages: ['Spanish', 'Haitian Creole', 'English'] },
        ],
        risk_inputs: {
            damage_rate_score:          6,
            fema_gap_score:             8,
            lep_score:                  7,
            sensor_gap_score:           9,
            basement_density_score:     7,
            social_vulnerability_score: 8,
        },
        policy_notes:             'Jewel Streets have no sewer connection — endemic flooding from groundwater. FEMA maps capture none of this structural exclusion. Capacity-building needed before full pilot deployment.',
        alert_threshold_depth_in: 2,
    },

    // ── 6. Soundview / Parkchester — TIER 2 · NEAR-TERM ──────────────────────
    // 6.62 % damage rate; Bronx River genuinely in FEMA 100-yr floodplain.
    {
        id:                   'soundview-parkchester',
        name:                 'Soundview / Parkchester',
        community_district:   'Bronx CD9',
        borough:              'Bronx',
        priority_tier:        2,
        pilot_status:         'near_term',
        true_risk_score:      73,
        fema_designated_zone: 'AE / X',
        fema_gap_flag:        false,
        coordinates:          [-73.8634, 40.8275],
        map_zoom:             13,
        zip_codes:            ['10462', '10473'],
        ida_impact: {
            damaged_buildings:     870,
            local_damage_rate_pct: 6.62,
            fatalities:            null,
            in_fema_sfha_pct:      45,
        },
        demographics: {
            total_population:  130_000,
            foreign_born_pct:  48.0,
            lep_pct:           55.0,
            primary_languages: ['Spanish', 'English', 'Haitian Creole', 'French'],
            key_communities:   ['Latino', 'Black', 'Caribbean immigrant'],
        },
        infrastructure: {
            basement_units_at_risk:    null,
            sewer_capacity_gap:        false,
            floodnet_coverage:         'moderate',
            floodnet_sensor_count_est: 9,
        },
        cbo_partners: [
            { name: 'Bronx River Alliance', type: 'Environmental resilience', languages: ['Spanish', 'English'] },
        ],
        risk_inputs: {
            damage_rate_score:          9,
            fema_gap_score:             6,
            lep_score:                  8,
            sensor_gap_score:           5,
            basement_density_score:     6,
            social_vulnerability_score: 7,
        },
        policy_notes:             'Bronx River Alliance is an established partner with strong community trust. FloodNet deployed early here. Stormwater damage still exceeds FEMA predictions despite genuine floodplain designation.',
        alert_threshold_depth_in: 2,
    },

    // ── 7. Southeast Queens / Jamaica — TIER 3 · CAPACITY-BUILDING ───────────
    // Groundwater table risen 40 ft since 1970s. 80,000+ homes at risk within 15 yrs.
    {
        id:                   'southeast-queens-jamaica',
        name:                 'Southeast Queens / Jamaica',
        community_district:   'Queens CD12',
        borough:              'Queens',
        priority_tier:        3,
        pilot_status:         'capacity_building',
        true_risk_score:      71,
        fema_designated_zone: 'X',
        fema_gap_flag:        true,
        coordinates:          [-73.8067, 40.6980],
        map_zoom:             13,
        zip_codes:            ['11432', '11433', '11434', '11435', '11436'],
        ida_impact: {
            damaged_buildings:     838,
            local_damage_rate_pct: 3.20,
            fatalities:            null,
            in_fema_sfha_pct:      2,
        },
        demographics: {
            total_population:  200_000,
            foreign_born_pct:  45.0,
            lep_pct:           38.0,
            primary_languages: ['English', 'Spanish', 'Haitian Creole', 'Punjabi'],
            key_communities:   ['Black', 'Caribbean-American', 'South Asian'],
        },
        infrastructure: {
            basement_units_at_risk:    80_000,
            sewer_capacity_gap:        true,
            floodnet_coverage:         'moderate',
            floodnet_sensor_count_est: 7,
        },
        cbo_partners: [
            { name: 'SQREJC (SE Queens Resiliency & Justice Coalition)', type: 'Environmental justice', languages: ['English', 'Haitian Creole'] },
        ],
        risk_inputs: {
            damage_rate_score:          6,
            fema_gap_score:             9,
            lep_score:                  6,
            sensor_gap_score:           6,
            basement_density_score:     9,
            social_vulnerability_score: 7,
        },
        policy_notes:             'Groundwater table risen 40 ft since 1970s. Incomplete sewer infrastructure. FEMA maps miss rising groundwater entirely. 80,000+ homes at risk within 15 years. Invest in capacity-building before full pilot.',
        alert_threshold_depth_in: 2,
    },
];

// ─── Utility Functions ────────────────────────────────────────────────────────

/**
 * Returns the neighborhood for a given ZIP code, or null if not mapped.
 * Used by the Residents page to tag each resident with their neighborhood
 * and sort by neighborhood priority tier.
 */
export function getNeighborhoodByZip(zip: string): IdaNeighborhood | null {
    return IDA_NEIGHBORHOODS.find(n => n.zip_codes.includes(zip)) ?? null;
}

/**
 * Returns all neighborhoods sorted by priority tier (1 first), then by
 * true_risk_score descending within each tier.
 */
export function getNeighborhoodsSorted(): IdaNeighborhood[] {
    return [...IDA_NEIGHBORHOODS].sort((a, b) => {
        if (a.priority_tier !== b.priority_tier) return a.priority_tier - b.priority_tier;
        return b.true_risk_score - a.true_risk_score;
    });
}

/**
 * Returns the priority sort order for a given ZIP code (lower = higher priority).
 * Returns 999 for ZIP codes not mapped to any pilot neighborhood.
 * Used when sorting the full resident list.
 */
export function getZipPriorityOrder(zip: string | undefined): number {
    if (!zip) return 999;
    const neighborhood = getNeighborhoodByZip(zip);
    if (!neighborhood) return 999;
    // Within a tier, higher true_risk_score sorts earlier
    return (neighborhood.priority_tier * 100) - neighborhood.true_risk_score;
}

/** Tier labels and colors for UI rendering */
export const TIER_CONFIG = {
    1: {
        label:     'Tier 1 — Immediate Pilot',
        shortLabel: 'Tier 1',
        color:     'text-red-400',
        bg:        'bg-red-500/10 border-red-500/30',
        dot:       'bg-red-500',
    },
    2: {
        label:     'Tier 2 — Near-Term',
        shortLabel: 'Tier 2',
        color:     'text-orange-400',
        bg:        'bg-orange-500/10 border-orange-500/30',
        dot:       'bg-orange-500',
    },
    3: {
        label:     'Tier 3 — Capacity Building',
        shortLabel: 'Tier 3',
        color:     'text-yellow-400',
        bg:        'bg-yellow-500/10 border-yellow-500/30',
        dot:       'bg-yellow-500',
    },
} as const satisfies Record<PriorityTier, {
    label: string; shortLabel: string; color: string; bg: string; dot: string;
}>;

/** FloodNet coverage labels for display */
export const COVERAGE_LABEL: Record<FloodnetCoverage, string> = {
    none:     'No sensors',
    minimal:  'Minimal (1–3)',
    moderate: 'Moderate (4–9)',
    good:     'Good (10–13)',
    high:     'High (14+)',
};


