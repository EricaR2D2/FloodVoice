import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET() {
    try {
        // Get date 4 weeks ago
        const fourWeeksAgo = new Date();
        fourWeeksAgo.setDate(fourWeeksAgo.getDate() - 28);

        // Fetch call logs from last 4 weeks
        const { data: callLogs, error } = await supabase
            .from('call_logs')
            .select('id, created_at, sentiment_score')
            .gte('created_at', fourWeeksAgo.toISOString())
            .not('sentiment_score', 'is', null)
            .order('created_at', { ascending: true });

        if (error) {
            console.error('Error fetching trends:', error);
            return NextResponse.json({ error: 'Failed to fetch trends' }, { status: 500 });
        }

        // Group by week
        const weeklyData: Record<string, { scores: number[], criticalCount: number }> = {};

        callLogs?.forEach(log => {
            const date = new Date(log.created_at);
            const weekStart = getWeekStart(date);
            const weekKey = weekStart.toISOString().split('T')[0];

            if (!weeklyData[weekKey]) {
                weeklyData[weekKey] = { scores: [], criticalCount: 0 };
            }

            const score = log.sentiment_score || 0;
            weeklyData[weekKey].scores.push(score);
            if (score >= 8) {
                weeklyData[weekKey].criticalCount++;
            }
        });

        // Convert to array and calculate averages
        const sortedWeeks = Object.keys(weeklyData).sort();
        const weeklyTrend = sortedWeeks.map((weekKey, index) => {
            const data = weeklyData[weekKey];
            const avgScore = data.scores.length > 0
                ? Math.round((data.scores.reduce((a, b) => a + b, 0) / data.scores.length) * 10) / 10
                : 0;

            return {
                week: `Week ${index + 1}`,
                weekStart: weekKey,
                avgScore,
                callCount: data.scores.length,
                criticalCount: data.criticalCount
            };
        });

        // Generate insight based on trend
        let insight = 'No significant trend detected';
        if (weeklyTrend.length >= 2) {
            const latest = weeklyTrend[weeklyTrend.length - 1];
            const previous = weeklyTrend[weeklyTrend.length - 2];

            if (latest.avgScore > previous.avgScore + 0.5) {
                const pctChange = Math.round(((latest.avgScore - previous.avgScore) / previous.avgScore) * 100);
                insight = `⚠️ Distress levels up ${pctChange}% this week`;
            } else if (latest.avgScore < previous.avgScore - 0.5) {
                const pctChange = Math.round(((previous.avgScore - latest.avgScore) / previous.avgScore) * 100);
                insight = `✅ Distress levels down ${pctChange}% this week`;
            } else {
                insight = '➡️ Distress levels stable week-over-week';
            }
        }

        return NextResponse.json({
            weeklyTrend,
            insight,
            summary: {
                totalWeeks: weeklyTrend.length,
                totalCalls: callLogs?.length || 0
            }
        });

    } catch (err) {
        console.error('Analytics trends error:', err);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}

function getWeekStart(date: Date): Date {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Monday start
    d.setDate(diff);
    d.setHours(0, 0, 0, 0);
    return d;
}
