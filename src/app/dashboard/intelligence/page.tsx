'use client';

import { ExternalLink, Waves, ShieldAlert, BarChart2, MessageSquare, Clock } from 'lucide-react';

function PanelHeader({ icon: Icon, title, subtitle, badge }: {
    icon: React.ElementType;
    title: string;
    subtitle: string;
    badge?: { label: string; color: 'green' | 'yellow' | 'slate' };
}) {
    const badgeColors = {
        green: 'bg-green-500/10 text-green-400 border-green-500/30',
        yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
        slate: 'bg-slate-700/50 text-slate-400 border-slate-600/30',
    };
    return (
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/5">
            <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/10">
                    <Icon className="w-4 h-4 text-blue-400" />
                </div>
                <div>
                    <h3 className="font-semibold text-white text-sm">{title}</h3>
                    <p className="text-[11px] text-slate-400">{subtitle}</p>
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

function ComingSoonPanel({ message }: { message: string }) {
    return (
        <div className="flex flex-col items-center justify-center h-48 gap-3 text-center">
            <Clock className="w-8 h-8 text-slate-600" />
            <p className="text-sm text-slate-500 max-w-xs">{message}</p>
            <span className="text-[10px] text-slate-600 border border-slate-700 rounded px-2 py-0.5">Day 2 Integration</span>
        </div>
    );
}

export default function FloodIntelligencePage() {
    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-white">Flood Intelligence</h1>
                <p className="text-slate-400 mt-1">
                    Live data from NYC FloodNet, FEMA flood zones, vulnerability index, and community reports.
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
                    <p className="text-xs text-slate-400 mb-4">
                        Sensor data is displayed on the Command Center map. For the full interactive
                        FloodNet visualization with historical trends and borough breakdowns, use the
                        official dashboard.
                    </p>
                    <a
                        href="https://dataviz.floodnet.nyc"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg text-sm font-medium transition-all"
                    >
                        <ExternalLink className="w-4 h-4" />
                        Open Full FloodNet Dashboard →
                    </a>
                    {/* Day 2: Wire live sensor summary cards from /api/floodnet/sensors */}
                </div>

                {/* Panel 2 — FEMA Flood Zones */}
                <div className="glass-panel rounded-xl p-5 border border-white/5">
                    <PanelHeader
                        icon={ShieldAlert}
                        title="FEMA Flood Zone Map"
                        subtitle="NYC National Flood Hazard Layer (NFHL)"
                        badge={{ label: 'Day 2', color: 'yellow' }}
                    />
                    <ComingSoonPanel message="FEMA NFHL GeoJSON overlay will display flood zone classifications (AE, VE, X) on the map. Wiring /api/fema/zones on Day 2." />
                </div>
            </div>

            {/* Bottom Row: FVI + Community Voice */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Panel 3 — FVI */}
                <div className="glass-panel rounded-xl p-5 border border-white/5">
                    <PanelHeader
                        icon={BarChart2}
                        title="NYC Flood Vulnerability Index"
                        subtitle="Community-level risk scores by neighborhood"
                        badge={{ label: 'Day 2', color: 'yellow' }}
                    />
                    <ComingSoonPanel message="FVI scores from NYC Open Data will display neighborhood vulnerability rankings and risk tier breakdowns. Wiring /api/fvi/data on Day 2." />
                </div>

                {/* Panel 4 — Community Voice */}
                <div className="glass-panel rounded-xl p-5 border border-white/5">
                    <PanelHeader
                        icon={MessageSquare}
                        title="Community Voice Reports"
                        subtitle="Resident-submitted flood reports from the field"
                        badge={{ label: 'Day 2', color: 'yellow' }}
                    />
                    <ComingSoonPanel message="Community reports from Twitter, Facebook, Nextdoor, and manual submissions will appear here. community_reports table wired on Day 2." />
                </div>
            </div>
        </div>
    );
}

