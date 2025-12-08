'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Phone, CheckCircle, Droplets, BarChart3 } from 'lucide-react';
import { FloodNetGraph } from '@/components/floodnet-graph';
import { FloodMap } from '@/components/flood-map';
import { FloodingDetected } from '@/components/flooding-detected';
import { UrgencyBreakdown, TagBreakdown, TrendSparkline } from '@/components/analytics';
import { supabase } from '@/lib/supabase';
import { useFlooding } from '@/contexts/flooding-context';

export default function DashboardHome() {

    // Use shared flooding context for city-wide flood data
    const flooding = useFlooding();

    // Calculate max depth and risk from all flooding sensors
    const maxFloodDepth = flooding.floodingSensors.length > 0
        ? Math.max(...flooding.floodingSensors.map(s => s.depth_in))
        : 0;

    const floodRisk: 'Low' | 'Moderate' | 'High' =
        maxFloodDepth > 8 ? 'High' :
            maxFloodDepth > 4 ? 'Moderate' : 'Low';

    // Real Data State
    const [stats, setStats] = useState({
        totalResidents: 0,
        safe: 0,
        distress: 0,
        pending: 0,
    });

    useEffect(() => {
        fetchResidentCounts();

        // Subscription for Resident Updates
        const channel = supabase
            .channel('dashboard-stats')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'residents' }, () => {
                fetchResidentCounts();
            })
            .subscribe();

        return () => { supabase.removeChannel(channel); };
    }, []);

    const fetchResidentCounts = async () => {
        const { data: residents } = await supabase.from('residents').select('status');

        if (residents) {
            const total = residents.length;
            const safe = residents.filter(r => r.status === 'safe' || r.status === 'unaffected').length;
            const distress = residents.filter(r => r.status === 'distress').length;
            const pending = total - safe - distress; // Catch-all for other statuses

            setStats({
                totalResidents: total,
                safe,
                distress,
                pending
            });
        }
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white">Command Center</h1>
                <p className="text-slate-400">Real-time resident monitoring & flood alerts</p>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                {/* Flood Risk Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                    className={
                        `glass-panel p-6 rounded-xl border-l-4 transition-colors duration-500 ` +
                        (floodRisk === 'High' ? 'border-red-500 bg-red-900/10' :
                            floodRisk === 'Moderate' ? 'border-yellow-500' : 'border-blue-500')
                    }
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm font-medium">Flood Risk</span>
                        <Droplets className={"w-5 h-5 " + (floodRisk === 'High' ? 'text-red-500' : floodRisk === 'Moderate' ? 'text-yellow-500' : 'text-blue-500')} />
                    </div>
                    <div className="text-3xl font-bold text-white mb-1">{floodRisk}</div>
                    <div className="text-xs text-slate-400 opacity-80">
                        {flooding.floodingSensors.length > 0
                            ? `Max depth: ${maxFloodDepth.toFixed(2)} in`
                            : `${flooding.activeSensors} sensors clear`
                        }
                    </div>
                </motion.div>

                {/* Flooding Detected Card - NEW */}
                <FloodingDetected />

                {/* Distress Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
                    className="glass-panel p-6 rounded-xl border-l-4 border-red-500 bg-red-500/5"
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-red-300 text-sm font-medium">In Distress</span>
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                    </div>
                    <div className="text-3xl font-bold text-white mb-1">{stats.distress}</div>
                    <div className="text-xs text-red-400">Requires immediate attention</div>
                </motion.div>

                {/* Pending Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
                    className="glass-panel p-6 rounded-xl border-l-4 border-slate-600"
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm font-medium">Pending Response</span>
                        <Phone className="w-5 h-5 text-slate-500" />
                    </div>
                    <div className="text-3xl font-bold text-white mb-1">{stats.pending}</div>
                    <div className="text-xs text-slate-500">Call active / Retrying</div>
                </motion.div>

                {/* Safe Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
                    className="glass-panel p-6 rounded-xl border-l-4 border-green-500"
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm font-medium">Confirmed Safe</span>
                        <CheckCircle className="w-5 h-5 text-green-500" />
                    </div>
                    <div className="text-3xl font-bold text-white mb-1">{stats.safe}</div>
                    <div className="text-xs text-green-500/80">
                        {stats.totalResidents > 0 ? Math.round((stats.safe / stats.totalResidents) * 100) : 0}% coverage
                    </div>
                </motion.div>
            </div>

            {/* Narrative to Numbers: Analytics Section */}
            <div className="space-y-4">
                <div className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-cyan-400" />
                    <h2 className="text-xl font-semibold text-white">Narrative to Numbers</h2>
                    <span className="text-xs text-slate-500 ml-2">AI-analyzed call insights</span>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left: Map + Sensor Network */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Flood Sensor Map */}
                        <FloodMap className="h-[400px]" />

                        {/* Sensor Network Graph */}
                        <div className="space-y-3">
                            <div className="flex items-center gap-2">
                                <Droplets className="w-4 h-4 text-blue-400" />
                                <h3 className="text-sm font-semibold text-white">Water Level History</h3>
                            </div>
                            <div className="h-[350px]">
                                <FloodNetGraph />
                            </div>
                        </div>
                    </div>

                    {/* Right: Analytics Sidebar */}
                    <div className="space-y-4">
                        <UrgencyBreakdown />
                        <TagBreakdown />
                        <TrendSparkline weeks={4} />
                    </div>
                </div>
            </div>
        </div>
    );
}
