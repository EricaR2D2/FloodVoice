import { NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/supabase-admin';

/**
 * GET /api/debug/check-analysis
 * Check if analysis data is persisted in call_logs
 */
export async function GET() {
    try {
        const { data: logs, error } = await supabaseAdmin
            .from('call_logs')
            .select('id, created_at, summary, tags, sentiment_score, key_topics, processed_at')
            .order('created_at', { ascending: false })
            .limit(5);

        if (error) {
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json({
            count: logs?.length || 0,
            logs: logs?.map(log => ({
                id: log.id,
                created_at: log.created_at,
                summary: log.summary?.substring(0, 50) + '...',
                tags: log.tags,
                sentiment_score: log.sentiment_score,
                key_topics: log.key_topics,
                processed_at: log.processed_at,
                hasAnalysis: !!(log.tags?.length || log.sentiment_score)
            }))
        });
    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
