import { NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/supabase-admin';
import { analyzeTranscript } from '@/lib/gemini';

export async function POST(request: Request) {
    try {
        const { callId } = await request.json();

        if (!callId) {
            return NextResponse.json({ error: 'Missing callId' }, { status: 400 });
        }

        // 1. Fetch Transcript
        const { data: log, error } = await supabaseAdmin
            .from('call_logs')
            .select('transcript, summary')
            .eq('id', callId)
            .single();

        if (error || !log) {
            return NextResponse.json({ error: 'Call log not found' }, { status: 404 });
        }

        const transcript = log.transcript || log.summary; // Fallback to summary if no raw transcript
        if (!transcript) {
            return NextResponse.json({ error: 'No text to analyze' }, { status: 400 });
        }

        // 2. Perform AI Analysis
        console.log(`Analyzing call ${callId}...`);
        const analysis = await analyzeTranscript(transcript);

        if (!analysis) {
            return NextResponse.json({ error: 'AI Analysis Failed' }, { status: 500 });
        }

        // 3. Save Results
        console.log(`Saving analysis for call ${callId}:`, analysis);
        const { data: updateData, error: updateError } = await supabaseAdmin
            .from('call_logs')
            .update({
                tags: analysis.tags,
                sentiment_score: analysis.sentiment_score,
                key_topics: analysis.key_topics,
                processed_at: new Date().toISOString()
            })
            .eq('id', callId)
            .select();

        console.log('Update result:', { updateData, updateError });

        if (updateError) {
            console.error('Supabase update failed:', updateError);
            throw updateError;
        }

        if (!updateData || updateData.length === 0) {
            console.error('Update returned no data - RLS may be blocking updates');
            return NextResponse.json({
                error: 'Update failed - possibly due to RLS policies',
                analysis
            }, { status: 500 });
        }

        return NextResponse.json({ success: true, analysis, savedData: updateData[0] });

    } catch (error: any) {
        console.error('Analysis API Error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
