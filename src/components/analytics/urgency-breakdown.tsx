'use client';

import { useEffect, useState, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { AlertTriangle, AlertCircle, Minus, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

type UrgencyData = {
    urgencyBreakdown: {
        critical: number;
        elevated: number;
        moderate: number;
        stable: number;
    };
    summary: {
        totalCalls: number;
        analyzedCalls: number;
        avgScore: number;
    };
};

const urgencyConfig = [
    { key: 'critical', label: 'Critical', color: 'bg-red-500', icon: AlertTriangle, textColor: 'text-red-400' },
    { key: 'elevated', label: 'Elevated', color: 'bg-orange-500', icon: AlertCircle, textColor: 'text-orange-400' },
    { key: 'moderate', label: 'Moderate', color: 'bg-yellow-500', icon: Minus, textColor: 'text-yellow-400' },
    { key: 'stable', label: 'Stable', color: 'bg-green-500', icon: CheckCircle, textColor: 'text-green-400' },
] as const;

export function UrgencyBreakdown() {
    const [data, setData] = useState<UrgencyData | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const fetchData = useCallback(async () => {
        try {
            const res = await fetch('/api/analytics/priority');
            if (!res.ok) throw new Error('Failed to fetch');
            const json = await res.json();
            setData(json);
        } catch (err) {
            console.error('UrgencyBreakdown fetch error:', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [fetchData]);

    if (isLoading) {
        return (
            <Card className="bg-slate-900/80 border-slate-800 p-4">
                <div className="animate-pulse">
                    <div className="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                    <div className="h-6 bg-slate-800 rounded-full"></div>
                </div>
            </Card>
        );
    }

    const breakdown = data?.urgencyBreakdown || { critical: 0, elevated: 0, moderate: 0, stable: 0 };
    const total = Object.values(breakdown).reduce((a, b) => a + b, 0);

    return (
        <Card className="bg-slate-900/80 border-slate-800 p-4">
            <h4 className="text-sm font-semibold text-white mb-4">Urgency Distribution</h4>

            {/* Stacked Bar */}
            {total > 0 ? (
                <div className="h-8 rounded-full overflow-hidden flex bg-slate-800">
                    {urgencyConfig.map(({ key, color }) => {
                        const value = breakdown[key as keyof typeof breakdown];
                        const pct = total > 0 ? (value / total) * 100 : 0;
                        if (pct === 0) return null;
                        return (
                            <div
                                key={key}
                                className={cn("h-full transition-all duration-500", color)}
                                style={{ width: `${pct}%` }}
                                title={`${key}: ${value}`}
                            />
                        );
                    })}
                </div>
            ) : (
                <div className="h-8 rounded-full bg-slate-800 flex items-center justify-center">
                    <span className="text-xs text-slate-500">No data yet</span>
                </div>
            )}

            {/* Legend */}
            <div className="grid grid-cols-2 gap-2 mt-4">
                {urgencyConfig.map(({ key, label, color, icon: Icon, textColor }) => {
                    const value = breakdown[key as keyof typeof breakdown];
                    return (
                        <div key={key} className="flex items-center gap-2">
                            <div className={cn("w-3 h-3 rounded-sm", color)} />
                            <span className="text-xs text-slate-400">{label}</span>
                            <span className={cn("text-xs font-bold ml-auto", textColor)}>
                                {value}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Average Score */}
            {data?.summary && (
                <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-center">
                    <span className="text-xs text-slate-500">Avg Distress Score</span>
                    <span className={cn(
                        "text-lg font-bold",
                        data.summary.avgScore >= 7 ? "text-red-400" :
                            data.summary.avgScore >= 5 ? "text-orange-400" :
                                data.summary.avgScore >= 3 ? "text-yellow-400" : "text-green-400"
                    )}>
                        {data.summary.avgScore}/10
                    </span>
                </div>
            )}
        </Card>
    );
}
