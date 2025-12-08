'use client';

import { useEffect, useState, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

type WeekData = {
    week: string;
    weekStart: string;
    avgScore: number;
    callCount: number;
    criticalCount: number;
};

type TrendData = {
    weeklyTrend: WeekData[];
    insight: string;
    summary: {
        totalWeeks: number;
        totalCalls: number;
    };
};

export function TrendSparkline({ weeks = 4 }: { weeks?: number }) {
    const [data, setData] = useState<TrendData | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const fetchData = useCallback(async () => {
        try {
            const res = await fetch('/api/analytics/trends');
            if (!res.ok) throw new Error('Failed to fetch');
            const json = await res.json();
            setData(json);
        } catch (err) {
            console.error('TrendSparkline fetch error:', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        // Refresh every 5 minutes (trends don't change as frequently)
        const interval = setInterval(fetchData, 300000);
        return () => clearInterval(interval);
    }, [fetchData]);

    if (isLoading) {
        return (
            <Card className="bg-slate-900/80 border-slate-800 p-4">
                <div className="animate-pulse">
                    <div className="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                    <div className="h-16 bg-slate-800 rounded"></div>
                </div>
            </Card>
        );
    }

    const trend = data?.weeklyTrend.slice(-weeks) || [];
    const insight = data?.insight || 'No trend data available';

    // Determine trend direction
    let TrendIcon = Minus;
    let trendColor = 'text-slate-400';
    if (insight.includes('up') || insight.includes('⚠️')) {
        TrendIcon = TrendingUp;
        trendColor = 'text-red-400';
    } else if (insight.includes('down') || insight.includes('✅')) {
        TrendIcon = TrendingDown;
        trendColor = 'text-green-400';
    }

    // Calculate sparkline points
    const maxScore = Math.max(...trend.map(w => w.avgScore), 10);
    const minScore = Math.min(...trend.map(w => w.avgScore), 0);
    const range = maxScore - minScore || 1;

    return (
        <Card className="bg-slate-900/80 border-slate-800 p-4">
            <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-white">4-Week Trend</h4>
                <TrendIcon className={cn("w-4 h-4", trendColor)} />
            </div>

            {trend.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-4">
                    Insufficient data for trend analysis
                </p>
            ) : (
                <>
                    {/* Simple Sparkline */}
                    <div className="h-12 flex items-end gap-1 mb-3">
                        {trend.map((week, i) => {
                            const heightPct = ((week.avgScore - minScore) / range) * 100;
                            const isLatest = i === trend.length - 1;

                            return (
                                <div key={week.weekStart} className="flex-1 flex flex-col items-center gap-1">
                                    <div
                                        className={cn(
                                            "w-full rounded-t transition-all duration-300",
                                            week.avgScore >= 7 ? "bg-red-500" :
                                                week.avgScore >= 5 ? "bg-orange-500" :
                                                    week.avgScore >= 3 ? "bg-yellow-500" : "bg-green-500",
                                            isLatest && "ring-2 ring-white/20"
                                        )}
                                        style={{ height: `${Math.max(heightPct, 10)}%` }}
                                        title={`${week.week}: ${week.avgScore}/10`}
                                    />
                                    <span className="text-[10px] text-slate-500">
                                        {week.week.replace('Week ', 'W')}
                                    </span>
                                </div>
                            );
                        })}
                    </div>

                    {/* Insight */}
                    <div className={cn(
                        "text-xs p-2 rounded-lg",
                        insight.includes('⚠️') ? "bg-red-950/50 text-red-300" :
                            insight.includes('✅') ? "bg-green-950/50 text-green-300" :
                                "bg-slate-800 text-slate-400"
                    )}>
                        {insight}
                    </div>

                    {/* Stats */}
                    <div className="flex justify-between mt-3 pt-2 border-t border-slate-800">
                        <span className="text-[10px] text-slate-500">
                            {data?.summary.totalCalls || 0} calls analyzed
                        </span>
                        <span className="text-[10px] text-slate-500">
                            {trend.length} weeks of data
                        </span>
                    </div>
                </>
            )}
        </Card>
    );
}
