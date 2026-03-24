'use client';

import { CheckCircle, XCircle, AlertCircle, Database, Waves, ShieldAlert, BarChart2, Twitter, Facebook, MessageCircle } from 'lucide-react';

type ConnectionStatus = 'connected' | 'not_configured' | 'coming_soon';

interface ApiCard {
    name: string;
    description: string;
    status: ConnectionStatus;
    icon: React.ElementType;
    envVar?: string;
    note?: string;
}

function StatusBadge({ status }: { status: ConnectionStatus }) {
    if (status === 'connected') return (
        <span className="flex items-center gap-1 text-xs text-green-400 font-medium">
            <CheckCircle className="w-3.5 h-3.5" /> Connected
        </span>
    );
    if (status === 'not_configured') return (
        <span className="flex items-center gap-1 text-xs text-yellow-400 font-medium">
            <AlertCircle className="w-3.5 h-3.5" /> Not Configured
        </span>
    );
    return (
        <span className="flex items-center gap-1 text-xs text-slate-500 font-medium">
            <XCircle className="w-3.5 h-3.5" /> Coming Soon
        </span>
    );
}

const apiSources: ApiCard[] = [
    {
        name: 'Supabase',
        description: 'Resident records, call logs, and community reports database.',
        status: 'connected',
        icon: Database,
        envVar: 'NEXT_PUBLIC_SUPABASE_URL',
    },
    {
        name: 'NYC FloodNet',
        description: 'Real-time street-level flood sensor network across NYC.',
        status: 'connected',
        icon: Waves,
        note: 'Public API — no key required.',
    },
    {
        name: 'FEMA Flood Zones',
        description: 'National Flood Hazard Layer (NFHL) GeoJSON for NYC.',
        status: 'coming_soon',
        icon: ShieldAlert,
        note: 'Wiring on Day 2 via /api/fema/zones.',
    },
    {
        name: 'NYC Flood Vulnerability Index',
        description: 'Neighborhood-level flood risk scores from NYC Open Data.',
        status: 'coming_soon',
        icon: BarChart2,
        note: 'Wiring on Day 2 via /api/fvi/data.',
    },
    {
        name: 'Twitter / X',
        description: 'Social media posts geo-tagged to NYC flood areas.',
        status: 'not_configured',
        icon: Twitter,
        envVar: 'TWITTER_BEARER_TOKEN',
        note: 'Requires Twitter API v2 Basic or Pro access.',
    },
    {
        name: 'Facebook',
        description: 'Public group posts and community alerts.',
        status: 'not_configured',
        icon: Facebook,
        envVar: 'FACEBOOK_PAGE_ACCESS_TOKEN',
        note: 'Requires Meta Graph API page access token.',
    },
    {
        name: 'Nextdoor',
        description: 'Hyperlocal neighborhood emergency posts.',
        status: 'coming_soon',
        icon: MessageCircle,
        note: 'Nextdoor does not have a public API — manual input panel planned.',
    },
];

export default function SettingsPage() {
    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-white">Settings</h1>
                <p className="text-slate-400 mt-1">API connections, environment status, and configuration.</p>
            </div>

            {/* API Connection Status */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold text-white">Data Source Connections</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {apiSources.map((api) => {
                        const Icon = api.icon;
                        return (
                            <div key={api.name} className="glass-panel rounded-xl p-5 border border-white/5 flex items-start gap-4">
                                <div className="p-2 rounded-lg bg-blue-500/10 shrink-0 mt-0.5">
                                    <Icon className="w-4 h-4 text-blue-400" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between gap-2 mb-1">
                                        <span className="font-medium text-white text-sm">{api.name}</span>
                                        <StatusBadge status={api.status} />
                                    </div>
                                    <p className="text-xs text-slate-400 leading-relaxed">{api.description}</p>
                                    {api.envVar && (
                                        <code className="mt-1.5 inline-block text-[10px] text-slate-500 bg-slate-800/60 border border-slate-700/50 rounded px-1.5 py-0.5">
                                            {api.envVar}
                                        </code>
                                    )}
                                    {api.note && (
                                        <p className="mt-1 text-[10px] text-slate-500 italic">{api.note}</p>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}

