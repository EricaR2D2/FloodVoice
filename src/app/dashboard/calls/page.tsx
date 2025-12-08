'use client';

import { useState } from 'react';
import { CallLogFeed } from '@/components/call-log-feed';
import { PriorityQueue } from '@/components/analytics';
import { PhoneCall, AlertTriangle } from 'lucide-react';

export default function CallsPage() {
    const [isCalling, setIsCalling] = useState(false);

    const handleTrigger = async () => {
        setIsCalling(true);
        try {
            const res = await fetch('/api/vapi/trigger', { method: 'POST' });
            const data = await res.json();

            if (res.ok) {
                const failures = data.results?.filter((r: { success: boolean }) => !r.success) || [];
                if (failures.length > 0) {
                    alert(`Failed to call ${failures.length} resident(s). Error: ${failures[0].error}`);
                } else {
                    alert(`Emergency Check-in initiated for ${data.results?.length || 0} residents.`);
                }
            } else {
                alert(`Failed to trigger calls: ${data.error || 'Unknown error'}`);
            }
        } catch (e: unknown) {
            const message = e instanceof Error ? e.message : 'Unknown error';
            console.error(e);
            alert(`Network error: ${message}`);
        }
        setIsCalling(false);
    };

    return (
        <div className="space-y-8">
            {/* Header with Emergency Button */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Live Call Feed</h1>
                    <p className="text-slate-400">Real-time monitoring of all check-in calls and AI analysis.</p>
                </div>

                <button
                    onClick={handleTrigger}
                    disabled={isCalling}
                    className="flex items-center gap-2 px-6 py-3 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/50 rounded-lg font-semibold transition-all shadow-[0_0_20px_rgba(239,68,68,0.2)] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <AlertTriangle className="w-5 h-5" />
                    {isCalling ? 'Initiating...' : 'Trigger Emergency Check-in'}
                </button>
            </div>

            {/* Main Content: Priority Queue + Call Feed */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Priority Queue Sidebar */}
                <div className="lg:col-span-1">
                    <div className="sticky top-6">
                        <div className="flex items-center gap-2 mb-4">
                            <AlertTriangle className="w-4 h-4 text-red-400" />
                            <h2 className="text-sm font-semibold text-white uppercase tracking-wide">Priority Queue</h2>
                        </div>
                        <PriorityQueue limit={15} />
                    </div>
                </div>

                {/* Main Feed */}
                <div className="lg:col-span-2 glass-panel p-6 rounded-xl border border-white/5 min-h-[600px]">
                    <div className="flex items-center gap-2 mb-6 pb-4 border-b border-white/5">
                        <PhoneCall className="w-5 h-5 text-blue-400" />
                        <h2 className="text-lg font-semibold text-white">Incoming Transcripts & Analysis</h2>
                    </div>

                    <CallLogFeed limit={50} />
                </div>
            </div>
        </div>
    );
}
