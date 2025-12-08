'use client';

import { useEffect, useState, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Activity, Utensils, Zap, Home, Brain, Droplets, FileText, ShieldCheck } from 'lucide-react';
import { cn } from '@/lib/utils';

type TagData = {
    tag: string;
    count: number;
    percentage: number;
};

type ApiResponse = {
    tagDistribution: TagData[];
};

// Match colors from call-log-feed.tsx
const tagConfig: Record<string, { color: string; bgColor: string; icon: React.ElementType }> = {
    'Medical': { color: 'text-red-400', bgColor: 'bg-red-500', icon: Activity },
    'Food/Water': { color: 'text-orange-400', bgColor: 'bg-orange-500', icon: Utensils },
    'Power': { color: 'text-yellow-400', bgColor: 'bg-yellow-500', icon: Zap },
    'Evacuation': { color: 'text-purple-400', bgColor: 'bg-purple-500', icon: Home },
    'Mental Health': { color: 'text-pink-400', bgColor: 'bg-pink-500', icon: Brain },
    'Property Damage': { color: 'text-blue-400', bgColor: 'bg-blue-500', icon: Droplets },
    'Safe': { color: 'text-green-400', bgColor: 'bg-green-500', icon: ShieldCheck },
};

const defaultConfig = { color: 'text-slate-400', bgColor: 'bg-slate-500', icon: FileText };

export function TagBreakdown() {
    const [tags, setTags] = useState<TagData[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchData = useCallback(async () => {
        try {
            const res = await fetch('/api/analytics/priority');
            if (!res.ok) throw new Error('Failed to fetch');
            const json: ApiResponse = await res.json();
            setTags(json.tagDistribution || []);
        } catch (err) {
            console.error('TagBreakdown fetch error:', err);
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
                    <div className="space-y-2">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-6 bg-slate-800 rounded"></div>
                        ))}
                    </div>
                </div>
            </Card>
        );
    }

    const maxCount = Math.max(...tags.map(t => t.count), 1);

    return (
        <Card className="bg-slate-900/80 border-slate-800 p-4">
            <h4 className="text-sm font-semibold text-white mb-4">Top Concerns</h4>

            {tags.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-4">No tags recorded yet</p>
            ) : (
                <div className="space-y-3">
                    {tags.slice(0, 6).map((tag) => {
                        const config = tagConfig[tag.tag] || defaultConfig;
                        const Icon = config.icon;
                        const widthPct = (tag.count / maxCount) * 100;

                        return (
                            <div key={tag.tag} className="space-y-1">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <Icon className={cn("w-3.5 h-3.5", config.color)} />
                                        <span className="text-xs text-slate-300">{tag.tag}</span>
                                    </div>
                                    <span className={cn("text-xs font-bold", config.color)}>
                                        {tag.count}
                                    </span>
                                </div>
                                <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
                                    <div
                                        className={cn("h-full rounded-full transition-all duration-500", config.bgColor)}
                                        style={{ width: `${widthPct}%`, opacity: 0.7 }}
                                    />
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </Card>
    );
}
