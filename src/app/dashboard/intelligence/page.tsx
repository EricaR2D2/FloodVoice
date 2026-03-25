'use client';

import { ExternalLink, Waves, ShieldAlert, BarChart2, MessageSquare, MapPin, AlertTriangle, Users, Building2 } from 'lucide-react';
import { getNeighborhoodsSorted, TIER_CONFIG, COVERAGE_LABEL, type IdaNeighborhood } from '@/lib/neighborhoods';

// Pre-sort once at module level — Tier 1 first, then by true_risk_score desc
const SORTED_NEIGHBORHOODS = getNeighborhoodsSorted();

function NeighborhoodCard({ n }: { n: IdaNeighborhood }) {
    const tier = TIER_CONFIG[n.priority_tier];
    return (
        <div className={`rounded-xl p-5 border ${tier.bg} flex flex-col gap-3`}>
            {/* Header: tier pill + name + score */}
            <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                    <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${tier.bg} ${tier.color}`}>
                        {tier.shortLabel}
                    </span>
                    <h4 className="text-base font-bold text-white mt-2 flex items-center gap-1.5 truncate">
                        <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
                        <span className="truncate">{n.name}</span>
                    </h4>
                    <p className="text-xs text-slate-400 ml-[22px]">{n.borough}</p>
                </div>
                <div className="text-right shrink-0">
                    <div className={`text-3xl font-bold leading-none ${tier.color}`}>{n.true_risk_score}</div>
                    <div className="text-xs text-slate-500">/ 100</div>
                </div>
            </div>

            {/* FEMA gap warning */}
            {n.fema_gap_flag && (
                <div className="flex items-center gap-1.5 text-xs bg-yellow-500/10 border border-yellow-500/20 rounded-md px-2.5 py-1.5 text-yellow-400">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                    Ida damage in FEMA Zone {n.fema_designated_zone} — model gap confirmed
                </div>
            )}

            {/* Score bar */}
            <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${tier.dot}`} style={{ width: `${n.true_risk_score}%` }} />
            </div>

            {/* Key stats */}
            <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-xs">
                <div className="flex items-center gap-1.5 text-slate-300">
                    <AlertTriangle className="w-3.5 h-3.5 text-orange-400 shrink-0" />
                    {n.ida_impact.local_damage_rate_pct}% dmg rate
                </div>
                <div className="flex items-center gap-1.5 text-slate-300">
                    <Users className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    {n.demographics.lep_pct}% LEP
                </div>
                <div className="flex items-center gap-1.5 text-slate-400 col-span-2">
                    <Building2 className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                    {n.infrastructure.basement_units_at_risk !== null
                        ? `${n.infrastructure.basement_units_at_risk.toLocaleString()} basement units`
                        : 'Basement data pending'}
                    <span className="text-slate-600">·</span>
                    <span className="text-slate-500">{COVERAGE_LABEL[n.infrastructure.floodnet_coverage]}</span>
                </div>
            </div>

            {/* Language tags */}
            <div className="flex flex-wrap gap-1.5">
                {n.demographics.primary_languages.slice(0, 3).map(lang => (
                    <span key={lang} className="text-xs px-2 py-0.5 bg-slate-700/50 border border-slate-600/30 rounded text-slate-300">
                        {lang}
                    </span>
                ))}
                {n.demographics.primary_languages.length > 3 && (
                    <span className="text-xs px-2 py-0.5 bg-slate-700/50 border border-slate-600/30 rounded text-slate-500">
                        +{n.demographics.primary_languages.length - 3}
                    </span>
                )}
            </div>

            {/* CBO partners */}
            <div className="text-xs text-slate-400 pt-1.5 border-t border-white/5">
                {n.cbo_partners.length} CBO partner{n.cbo_partners.length !== 1 ? 's' : ''} ·{' '}
                <span className="text-slate-500">
                    {n.cbo_partners.slice(0, 2).map(c => c.name).join(', ')}
                    {n.cbo_partners.length > 2 ? ' +more' : ''}
                </span>
            </div>
        </div>
    );
}

// ─── Community Voice Static Reports ───
const COMMUNITY_REPORTS = [
    {
        id: 1,
        timestamp: '2 hours ago',
        location: 'Van Dyke St & Ferris St, Red Hook',
        message: 'Water is coming under the front door. At least 4 inches on the street. Power is still on but I can hear the sump pump struggling.',
        severity: 'critical',
        reporter: 'Anonymous resident',
        verified: true,
    },
    {
        id: 2,
        timestamp: '3 hours ago',
        location: 'Hunts Point Ave & Lafayette Ave, Bronx',
        message: 'Flooding at the corner. Cars can\'t get through. A few families on the ground floor need help — one older man with oxygen.',
        severity: 'critical',
        reporter: 'Community liaison',
        verified: true,
    },
    {
        id: 3,
        timestamp: '4 hours ago',
        location: 'E 86th St, Canarsie',
        message: 'Street flooding on my block. Drains are backed up. Basement apartments getting water. Some people need to get to higher ground.',
        severity: 'moderate',
        reporter: 'Nextdoor report',
        verified: false,
    },
    {
        id: 4,
        timestamp: '5 hours ago',
        location: 'Willis Ave, South Bronx',
        message: 'Utility pole on Willis sparking. Water below it. Someone called 911 already. Stay away from that corner.',
        severity: 'critical',
        reporter: 'Resident — translated from Spanish',
        verified: true,
    },
    {
        id: 5,
        timestamp: '6 hours ago',
        location: 'Tiffany St, Hunts Point',
        message: 'Flooding on Tiffany. Not too deep yet. Most people I see are staying inside. Bodega on the corner is still open and helping people.',
        severity: 'low',
        reporter: 'WhatsApp community group',
        verified: false,
    },
];

function PanelHeader({ icon: Icon, title, subtitle, badge }: {
    icon: React.ElementType;
    title: string;
    subtitle: string;
    badge?: { label: string; color: 'green' | 'yellow' | 'slate' | 'blue' };
}) {
    const badgeColors = {
        green: 'bg-green-500/10 text-green-400 border-green-500/30',
        yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
        slate: 'bg-slate-700/50 text-slate-400 border-slate-600/30',
        blue: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    };
    return (
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/5">
            <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/10">
                    <Icon className="w-4 h-4 text-blue-400" />
                </div>
                <div>
                    <h3 className="font-semibold text-white text-base">{title}</h3>
                    <p className="text-xs text-slate-400">{subtitle}</p>
                </div>
            </div>
            {badge && (
                <span className={`text-[10px] px-2 py-0.5 rounded-full border font-medium ${badgeColors[badge.color]}`}>
                    {badge.label}
                </span>
            )}
        </div>
    );
}

const severityConfig = {
    critical: { label: 'Critical', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/30', dot: 'bg-red-500' },
    moderate: { label: 'Moderate', color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/30', dot: 'bg-orange-500' },
    low: { label: 'Low', color: 'text-yellow-400', bg: 'bg-yellow-500/10 border-yellow-500/30', dot: 'bg-yellow-500' },
};

export default function FloodIntelligencePage() {
    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-[var(--text-primary)]">Flood Intelligence</h1>
                <p className="text-[var(--text-secondary)] mt-1">
                    Live data from NYC FloodNet, FEMA flood zones, Ida priority neighborhood risk scores, and community reports.
                </p>
            </div>

            {/* Top Row: FloodNet + FEMA */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Panel 1 — FloodNet Live */}
                <div className="glass-panel rounded-xl p-5 border border-white/5">
                    <PanelHeader
                        icon={Waves}
                        title="NYC FloodNet — Live Sensors"
                        subtitle="Real-time street-level flood depth data"
                        badge={{ label: 'Live', color: 'green' }}
                    />
                    <p className="text-xs text-[var(--text-secondary)] mb-4">
                        Sensor data and the <strong className="text-[var(--text-primary)]">FEMA zone overlay</strong> are
                        displayed on the Command Center map — click the{' '}
                        <span className="text-blue-400 font-medium">FEMA Zones</span> toggle on the map to show
                        AE, VE, and shallow flood areas. For historical trends and borough breakdowns, use
                        the official FloodNet dashboard below.
                    </p>
                    <div className="flex flex-wrap gap-3">
                        <a
                            href="https://dataviz.floodnet.nyc"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg text-sm font-medium transition-all"
                        >
                            <ExternalLink className="w-4 h-4" />
                            Open Full FloodNet Dashboard →
                        </a>
                    </div>
                </div>

                {/* Panel 2 — FEMA Flood Zones */}
                <div className="glass-panel rounded-xl p-5 border border-white/5">
                    <PanelHeader
                        icon={ShieldAlert}
                        title="FEMA Flood Zone Map"
                        subtitle="NYC National Flood Hazard Layer (NFHL)"
                        badge={{ label: 'Live', color: 'blue' }}
                    />
                    <div className="space-y-3">
                        <p className="text-xs text-[var(--text-secondary)]">
                            FEMA flood zone polygons are now overlaid on the Command Center map.
                            Toggle them on with the <span className="text-blue-400 font-medium">FEMA Zones</span> button.
                        </p>
                        {/* Zone classification key */}
                        <div className="grid grid-cols-1 gap-2">
                            {[
                                { zone: 'VE', label: 'Coastal High Hazard', color: 'bg-red-500/20 border-red-500/40', text: 'text-red-300', desc: 'Wave action + 1% annual flood risk. Highest risk.' },
                                { zone: 'AE', label: '100-Year Flood Zone', color: 'bg-blue-500/20 border-blue-500/40', text: 'text-blue-300', desc: '1% annual chance of flooding. FEMA flood insurance required.' },
                                { zone: 'AO/AH', label: 'Shallow Flooding', color: 'bg-purple-500/20 border-purple-500/40', text: 'text-purple-300', desc: 'Sheet flow or ponding. Depth 1–3 ft.' },
                                { zone: 'X', label: 'Minimal Hazard', color: 'bg-slate-700/30 border-slate-600/40', text: 'text-slate-400', desc: 'Outside 500-year floodplain. Lowest risk.' },
                            ].map(({ zone, label, color, text, desc }) => (
                                <div key={zone} className={`flex items-start gap-3 p-2.5 rounded-lg border ${color}`}>
                                    <span className={`text-xs font-bold font-mono shrink-0 mt-0.5 ${text}`}>{zone}</span>
                                    <div>
                                        <div className={`text-xs font-medium ${text}`}>{label}</div>
                                        <div className="text-[11px] text-[var(--text-secondary)]">{desc}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Ida Priority Neighborhoods — full width */}
            <div className="glass-panel rounded-xl p-5 border border-white/5">
                <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/5">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-500/10">
                            <BarChart2 className="w-4 h-4 text-blue-400" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-white text-base">Ida Priority Neighborhoods — True Risk Score</h3>
                            <p className="text-xs text-slate-400">7 pilot areas · Scored by Ida damage, FEMA gap, LEP, and basement density</p>
                        </div>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full border font-medium bg-yellow-500/10 text-yellow-400 border-yellow-500/30 shrink-0">
                        ⚠ 80.4% of Ida damage was in FEMA Zone X
                    </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {SORTED_NEIGHBORHOODS.map(n => (
                        <NeighborhoodCard key={n.id} n={n} />
                    ))}
                </div>
                <p className="text-xs text-slate-500 mt-4">
                    True Risk Score = weighted composite: Ida damage rate (30%) · FEMA model gap (25%) · LEP population (20%) · sensor gap (10%) · basement density (10%) · social vulnerability (5%). Source: NYC Community Flood Triage Pilot Report.
                </p>
            </div>

            {/* Community Voice — full width */}
            <div className="glass-panel rounded-xl p-5 border border-white/5">
                <PanelHeader
                    icon={MessageSquare}
                    title="Community Voice Reports"
                    subtitle="Field reports from residents and liaisons"
                    badge={{ label: 'Demo', color: 'yellow' }}
                />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {COMMUNITY_REPORTS.map((report) => {
                        const sev = severityConfig[report.severity as keyof typeof severityConfig];
                        return (
                            <div key={report.id} className="p-4 rounded-lg bg-slate-800/40 border border-white/5 space-y-2">
                                <div className="flex items-center justify-between gap-2">
                                    <div className="flex items-center gap-2">
                                        <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${sev.dot}`} />
                                        <span className="text-xs font-medium text-slate-300">{report.location}</span>
                                    </div>
                                    <div className="flex items-center gap-2 shrink-0">
                                        {report.verified && (
                                            <span className="text-[10px] px-2 py-0.5 bg-green-500/10 text-green-400 border border-green-500/30 rounded-full">✓ verified</span>
                                        )}
                                        <span className={`text-[10px] px-2 py-0.5 border rounded-full font-medium ${sev.bg} ${sev.color}`}>
                                            {sev.label}
                                        </span>
                                    </div>
                                </div>
                                <p className="text-sm text-[var(--text-primary)] leading-relaxed">&ldquo;{report.message}&rdquo;</p>
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-slate-500">{report.reporter}</span>
                                    <span className="text-xs text-slate-600">{report.timestamp}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
                <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-xs text-slate-500">
                        Demo data — live community_reports table connects here when Supabase is configured.
                    </p>
                </div>
            </div>
        </div>
    );
}

