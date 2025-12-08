import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

type UrgencyTier = 'critical' | 'elevated' | 'moderate' | 'stable';

function getUrgencyTier(score: number): UrgencyTier {
    if (score >= 8) return 'critical';
    if (score >= 6) return 'elevated';
    if (score >= 4) return 'moderate';
    return 'stable';
}

export async function GET() {
    try {
        // Fetch all call logs with sentiment scores and resident info
        const { data: callLogs, error } = await supabase
            .from('call_logs')
            .select(`
                id,
                created_at,
                sentiment_score,
                tags,
                key_topics,
                summary,
                resident_id,
                resident:residents(id, name, phone_number, status)
            `)
            .not('sentiment_score', 'is', null)
            .order('sentiment_score', { ascending: false })
            .order('created_at', { ascending: false });

        if (error) {
            console.error('Error fetching call logs:', error);
            return NextResponse.json({ error: 'Failed to fetch analytics' }, { status: 500 });
        }

        // Calculate urgency breakdown
        const urgencyBreakdown = {
            critical: 0,  // 8-10
            elevated: 0,  // 6-7
            moderate: 0,  // 4-5
            stable: 0     // 1-3
        };

        // Track tag counts
        const tagCounts: Record<string, number> = {};

        // Process each call log
        let totalScore = 0;
        let analyzedCount = 0;

        callLogs?.forEach((log) => {
            const score = log.sentiment_score || 0;
            if (score > 0) {
                urgencyBreakdown[getUrgencyTier(score)]++;
                totalScore += score;
                analyzedCount++;
            }

            // Count tags
            if (log.tags && Array.isArray(log.tags)) {
                log.tags.forEach((tag: string) => {
                    tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                });
            }
        });

        // Get top 10 priority residents (highest scores)
        const topPriority = callLogs
            ?.filter(log => log.sentiment_score && log.sentiment_score >= 6)
            .slice(0, 10)
            .map(log => ({
                callId: log.id,
                residentId: log.resident_id,
                residentName: (log.resident as any)?.name || 'Unknown',
                residentPhone: (log.resident as any)?.phone_number || '',
                residentStatus: (log.resident as any)?.status || 'pending',
                sentimentScore: log.sentiment_score,
                tags: log.tags || [],
                keyTopics: log.key_topics || log.summary || '',
                callTime: log.created_at
            })) || [];

        // Build tag distribution (sorted by count)
        const totalTags = Object.values(tagCounts).reduce((a, b) => a + b, 0);
        const tagDistribution = Object.entries(tagCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8)
            .map(([tag, count]) => ({
                tag,
                count,
                percentage: totalTags > 0 ? Math.round((count / totalTags) * 100) : 0
            }));

        return NextResponse.json({
            urgencyBreakdown,
            topPriority,
            tagDistribution,
            summary: {
                totalCalls: callLogs?.length || 0,
                analyzedCalls: analyzedCount,
                avgScore: analyzedCount > 0 ? Math.round((totalScore / analyzedCount) * 10) / 10 : 0
            }
        });

    } catch (err) {
        console.error('Analytics priority error:', err);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
