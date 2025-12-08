'use client';

import { useEffect, useState, useCallback } from 'react';
import { supabase } from '@/lib/supabase';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Play, FileText, Activity, Zap, Droplets, Utensils, Home, Brain, ChevronDown } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

type CallLog = {
    id: string;
    created_at: string;
    recording_url: string;
    transcript: string;
    summary: string;
    resident_id: string;
    resident: { name: string };
    // New Fields
    tags: string[];
    sentiment_score: number;
    key_topics: string;
};

// Map Tags to Colors & Icons - Compact version
const getTagConfig = (tag: string) => {
    switch (tag) {
        case 'Medical': return { color: 'bg-red-500/30 text-red-400', icon: Activity, short: 'Med' };
        case 'Food/Water': return { color: 'bg-orange-500/30 text-orange-400', icon: Utensils, short: 'Food' };
        case 'Power': return { color: 'bg-yellow-500/30 text-yellow-400', icon: Zap, short: 'Pwr' };
        case 'Evacuation': return { color: 'bg-purple-500/30 text-purple-400', icon: Home, short: 'Evac' };
        case 'Mental Health': return { color: 'bg-pink-500/30 text-pink-400', icon: Brain, short: 'MH' };
        case 'Property Damage': return { color: 'bg-blue-500/30 text-blue-400', icon: Droplets, short: 'Prop' };
        case 'Safe': return { color: 'bg-green-500/30 text-green-400', icon: FileText, short: 'Safe' };
        default: return { color: 'bg-slate-700/50 text-slate-400', icon: FileText, short: tag.slice(0, 4) };
    }
};

// Get border and badge colors based on score
const getPriorityColors = (score: number) => {
    if (score >= 8) return { border: 'border-l-red-500', badge: 'bg-red-500 text-white', pulse: true };
    if (score >= 6) return { border: 'border-l-orange-500', badge: 'bg-orange-500 text-white', pulse: false };
    if (score >= 4) return { border: 'border-l-yellow-500', badge: 'bg-yellow-500 text-black', pulse: false };
    return { border: 'border-l-green-500', badge: 'bg-green-600 text-white', pulse: false };
};

export function CallLogFeed({ limit = 10 }: { limit?: number }) {
    const [logs, setLogs] = useState<CallLog[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [expandedId, setExpandedId] = useState<string | null>(null);

    const fetchLogs = useCallback(async () => {
        const { data } = await supabase
            .from('call_logs')
            .select(`
                    id, created_at, recording_url, transcript, summary, resident_id, tags, sentiment_score, key_topics,
                    resident:residents(name)
                `)
            .order('created_at', { ascending: false })
            .limit(limit);

        if (data) setLogs(data as any[]);
        setIsLoading(false);
    }, [limit]);

    useEffect(() => {
        fetchLogs();

        // Subscribe to real-time changes
        const subscription = supabase
            .channel('call_logs_realtime')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'call_logs' },
                (payload) => {
                    console.log('Call Log Updated:', payload);
                    fetchLogs(); // Refresh on Insert OR Update
                }
            )
            .subscribe();

        return () => { subscription.unsubscribe(); };
    }, [fetchLogs]);

    const toggleExpand = (id: string) => {
        setExpandedId(expandedId === id ? null : id);
    };

    if (isLoading) return <div className="text-slate-500 text-sm animate-pulse">Scanning feed...</div>;

    if (logs.length === 0) return <div className="text-slate-500 text-sm">No recent calls recorded.</div>;

    return (
        <div className="space-y-2">
            {logs.map((log) => {
                const score = log.sentiment_score ?? 0;
                const priority = getPriorityColors(score);
                const isExpanded = expandedId === log.id;

                return (
                    <Card
                        key={log.id}
                        className={cn(
                            "bg-slate-900/80 border-slate-800 overflow-hidden transition-all duration-200 cursor-pointer hover:bg-slate-800/60",
                            score > 0 && `border-l-4 ${priority.border}`
                        )}
                        onClick={() => toggleExpand(log.id)}
                    >
                        {/* Compact Card View */}
                        <div className="px-3 py-2.5">
                            {/* Row 1: Name + Time | Score */}
                            <div className="flex items-center justify-between gap-2">
                                {/* Left: Name + Time */}
                                <div className="flex items-center gap-2 min-w-0">
                                    <span className="font-semibold text-white text-sm truncate">
                                        {log.resident?.name || 'Unknown'}
                                    </span>
                                    <span className="text-[10px] text-slate-500 whitespace-nowrap">
                                        {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                                    </span>
                                </div>

                                {/* Right: Score Badge + Expand */}
                                <div className="flex items-center gap-2 flex-shrink-0">
                                    {score > 0 && (
                                        <span className={cn(
                                            "text-xs font-bold px-2.5 py-0.5 rounded-full min-w-[32px] text-center",
                                            priority.badge,
                                            priority.pulse && "animate-pulse"
                                        )}>
                                            {score}
                                        </span>
                                    )}
                                    <ChevronDown className={cn(
                                        "w-4 h-4 text-slate-500 transition-transform",
                                        isExpanded && "rotate-180"
                                    )} />
                                </div>
                            </div>

                            {/* Row 2: Summary + Tags */}
                            {(log.key_topics || (log.tags && log.tags.length > 0)) && (
                                <div className="mt-2 space-y-1.5">
                                    {/* Summary */}
                                    {log.key_topics && (
                                        <p className="text-xs text-slate-400 line-clamp-1 italic">
                                            "{log.key_topics}"
                                        </p>
                                    )}

                                    {/* Tags Row */}
                                    {log.tags && log.tags.length > 0 && (
                                        <div className="flex flex-wrap gap-1.5">
                                            {log.tags.map(tag => {
                                                const config = getTagConfig(tag);
                                                const Icon = config.icon;
                                                return (
                                                    <span
                                                        key={tag}
                                                        className={cn(
                                                            "text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1",
                                                            config.color
                                                        )}
                                                        title={tag}
                                                    >
                                                        <Icon className="w-3 h-3" />
                                                        {config.short}
                                                    </span>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Expanded Detail View: Audio & Full Transcript */}
                        {expandedId === log.id && (
                            <div className="border-t border-slate-800 bg-slate-950 p-4 animate-in slide-in-from-top-2 duration-200">
                                {/* Audio Player */}
                                {log.recording_url && (
                                    <div className="mb-4">
                                        <h4 className="text-xs font-bold text-slate-500 uppercase mb-2 flex items-center gap-2">
                                            <Play className="w-3 h-3" /> Call Recording
                                        </h4>
                                        <audio controls className="w-full h-8 rounded bg-slate-900" src={log.recording_url} />
                                    </div>
                                )}

                                {/* Full Transcript */}
                                <div>
                                    <h4 className="text-xs font-bold text-slate-500 uppercase mb-2 flex items-center gap-2">
                                        <FileText className="w-3 h-3" /> Full Transcript
                                    </h4>
                                    <div className="text-sm text-slate-300 leading-relaxed p-3 bg-slate-900 rounded-md max-h-60 overflow-y-auto font-mono">
                                        {log.transcript || "Transcript not available."}
                                    </div>
                                </div>

                                {/* Manual Re-Analyze Button (Debug) */}
                                {(!log.sentiment_score || log.sentiment_score === 0) && (
                                    <div className="mt-4 pt-4 border-t border-slate-900 flex justify-end">
                                        <Button size="sm" variant="secondary"
                                            className="text-xs h-7"
                                            onClick={async (e) => {
                                                e.stopPropagation();
                                                const btn = e.currentTarget;
                                                btn.disabled = true;
                                                const originalText = btn.textContent;
                                                btn.textContent = "Analyzing...";

                                                try {
                                                    console.log(`Starting analysis for call: ${log.id}`);
                                                    const response = await fetch('/api/analyze-call', {
                                                        method: 'POST',
                                                        headers: {
                                                            'Content-Type': 'application/json',
                                                        },
                                                        body: JSON.stringify({ callId: log.id })
                                                    });

                                                    const result = await response.json();
                                                    console.log('Analysis API Response:', result);

                                                    if (!response.ok) {
                                                        throw new Error(result.error || 'Analysis failed');
                                                    }

                                                    // Directly update local state with the analysis results
                                                    if (result.success && result.analysis) {
                                                        setLogs(prevLogs => prevLogs.map(l =>
                                                            l.id === log.id
                                                                ? {
                                                                    ...l,
                                                                    tags: result.analysis.tags,
                                                                    sentiment_score: result.analysis.sentiment_score,
                                                                    key_topics: result.analysis.key_topics
                                                                }
                                                                : l
                                                        ));
                                                        console.log('Local state updated with analysis:', result.analysis);
                                                    }
                                                } catch (err: any) {
                                                    console.error('Analysis Error:', err);
                                                    alert(`Analysis Failed: ${err.message}`);
                                                } finally {
                                                    btn.disabled = false;
                                                    btn.textContent = originalText;
                                                }
                                            }}
                                        >
                                            <Brain className="w-3 h-3 mr-2" />
                                            Analyze with Gemini
                                        </Button>
                                    </div>
                                )}
                            </div>
                        )}
                    </Card>
                );
            })}
        </div>
    );
}
