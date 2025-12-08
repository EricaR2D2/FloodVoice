'use client';

import { useEffect, useState, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Phone, AlertTriangle, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

type PriorityResident = {
    callId: string;
    residentId: string;
    residentName: string;
    residentPhone: string;
    residentStatus: string;
    sentimentScore: number;
    tags: string[];
    keyTopics: string;
    callTime: string;
};

type PriorityData = {
    topPriority: PriorityResident[];
    summary: {
        totalCalls: number;
        analyzedCalls: number;
        avgScore: number;
    };
};

const getScoreStyle = (score: number) => {
    if (score >= 8) return { bg: 'bg-red-500', text: 'text-white', border: 'border-red-500', pulse: true };
    if (score >= 6) return { bg: 'bg-orange-500', text: 'text-white', border: 'border-orange-500', pulse: false };
    return { bg: 'bg-yellow-500', text: 'text-black', border: 'border-yellow-500', pulse: false };
};

export function PriorityQueue({ limit = 10 }: { limit?: number }) {
    const [data, setData] = useState<PriorityData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        try {
            const res = await fetch('/api/analytics/priority');
            if (!res.ok) throw new Error('Failed to fetch priority data');
            const json = await res.json();
            setData(json);
            setError(null);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        // Refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [fetchData]);

    if (isLoading) {
        return (
            <Card className="bg-slate-900/80 border-slate-800 p-6">
                <div className="animate-pulse space-y-4">
                    <div className="h-6 bg-slate-700 rounded w-1/3"></div>
                    <div className="space-y-3">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-16 bg-slate-800 rounded"></div>
                        ))}
                    </div>
                </div>
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="bg-slate-900/80 border-slate-800 p-6">
                <p className="text-red-400 text-sm">Error: {error}</p>
            </Card>
        );
    }

    const residents = data?.topPriority.slice(0, limit) || [];

    return (
        <Card className="bg-slate-900/80 border-slate-800 overflow-hidden">
            {/* Header */}
            <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                    <h3 className="font-semibold text-white">Priority Queue</h3>
                </div>
                <span className="text-xs text-slate-500">
                    {residents.length} need attention
                </span>
            </div>

            {/* Resident List */}
            <div className="divide-y divide-slate-800/50 max-h-[500px] overflow-y-auto">
                {residents.length === 0 ? (
                    <div className="p-8 text-center">
                        <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-3">
                            <AlertTriangle className="w-6 h-6 text-green-500" />
                        </div>
                        <p className="text-slate-400 text-sm">All residents stable</p>
                        <p className="text-slate-600 text-xs mt-1">No critical cases requiring attention</p>
                    </div>
                ) : (
                    residents.map((resident, index) => {
                        const style = getScoreStyle(resident.sentimentScore);
                        return (
                            <div
                                key={resident.callId}
                                className={cn(
                                    "px-4 py-3 hover:bg-slate-800/50 transition-colors",
                                    index === 0 && resident.sentimentScore >= 8 && "bg-red-950/30"
                                )}
                            >
                                <div className="flex items-start gap-3">
                                    {/* Score Badge */}
                                    <div className={cn(
                                        "flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg",
                                        style.bg, style.text,
                                        style.pulse && "animate-pulse"
                                    )}>
                                        {resident.sentimentScore}
                                    </div>

                                    {/* Info */}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2">
                                            <span className="font-medium text-white truncate">
                                                {resident.residentName}
                                            </span>
                                            <span className="text-[10px] text-slate-500 flex items-center gap-1">
                                                <Clock className="w-3 h-3" />
                                                {formatDistanceToNow(new Date(resident.callTime), { addSuffix: true })}
                                            </span>
                                        </div>

                                        {/* Key Topics */}
                                        {resident.keyTopics && (
                                            <p className="text-xs text-slate-400 mt-1 line-clamp-1 italic">
                                                "{resident.keyTopics}"
                                            </p>
                                        )}

                                        {/* Tags */}
                                        {resident.tags.length > 0 && (
                                            <div className="flex flex-wrap gap-1 mt-2">
                                                {resident.tags.slice(0, 3).map(tag => (
                                                    <span
                                                        key={tag}
                                                        className="text-[10px] px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-300"
                                                    >
                                                        {tag}
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </div>

                                    {/* Quick Call */}
                                    {resident.residentPhone && (
                                        <a
                                            href={`tel:${resident.residentPhone}`}
                                            className="flex-shrink-0 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
                                            onClick={(e) => e.stopPropagation()}
                                            title={`Call ${resident.residentName}`}
                                        >
                                            <Phone className="w-4 h-4 text-slate-400" />
                                        </a>
                                    )}
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </Card>
    );
}
