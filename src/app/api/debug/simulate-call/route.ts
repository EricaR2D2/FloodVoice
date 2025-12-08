import { NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/supabase-admin';
import { analyzeTranscript } from '@/lib/gemini';
import { sendDistressAlert } from '@/lib/telegram';

/**
 * Debug endpoint to simulate a VAPI call end and test AI analysis.
 * 
 * POST /api/debug/simulate-call
 * Body: {
 *   residentId: string,           // Required: existing resident UUID
 *   transcript: string,           // Required: the call transcript to analyze
 *   summary?: string              // Optional: call summary
 * }
 */
export async function POST(request: Request) {
    try {
        const { residentId, transcript, summary } = await request.json();

        if (!residentId) {
            return NextResponse.json({ error: 'residentId is required' }, { status: 400 });
        }
        if (!transcript) {
            return NextResponse.json({ error: 'transcript is required' }, { status: 400 });
        }

        // Verify resident exists
        const { data: resident, error: residentError } = await supabaseAdmin
            .from('residents')
            .select('id, name, liaison_id')
            .eq('id', residentId)
            .single();

        if (residentError || !resident) {
            return NextResponse.json({ error: 'Resident not found' }, { status: 404 });
        }

        console.log(`[DEBUG] Simulating call for resident: ${resident.name} (${residentId})`);

        // 1. Insert call log
        const { data: insertedLog, error: insertError } = await supabaseAdmin
            .from('call_logs')
            .insert({
                resident_id: residentId,
                vapi_call_id: `debug-${Date.now()}`,
                summary: summary || 'Debug call simulation',
                risk_label: 'safe',
                transcript: transcript
            })
            .select('id')
            .single();

        if (insertError) {
            console.error('Failed to insert call log:', insertError);
            return NextResponse.json({ error: 'Failed to insert call log', details: insertError }, { status: 500 });
        }

        console.log(`[DEBUG] Call log created: ${insertedLog.id}`);

        // 2. Run AI Analysis
        console.log(`[DEBUG] Running AI analysis...`);
        const aiAnalysis = await analyzeTranscript(transcript);

        if (!aiAnalysis) {
            return NextResponse.json({
                error: 'AI Analysis failed',
                callLogId: insertedLog.id
            }, { status: 500 });
        }

        console.log(`[DEBUG] AI Analysis complete: Score=${aiAnalysis.sentiment_score}, Tags=[${aiAnalysis.tags.join(', ')}]`);

        // 3. Update call log with analysis
        await supabaseAdmin
            .from('call_logs')
            .update({
                tags: aiAnalysis.tags,
                sentiment_score: aiAnalysis.sentiment_score,
                key_topics: aiAnalysis.key_topics,
                processed_at: new Date().toISOString()
            })
            .eq('id', insertedLog.id);

        // 4. Check for Distress
        let distressTriggered = false;
        let alertSent = false;

        if (aiAnalysis.sentiment_score >= 7) {
            console.log(`[DEBUG] DISTRESS DETECTED! Score: ${aiAnalysis.sentiment_score}`);
            distressTriggered = true;

            // Update resident status
            await supabaseAdmin
                .from('residents')
                .update({ status: 'distress' })
                .eq('id', residentId);

            // Update call log risk label
            await supabaseAdmin
                .from('call_logs')
                .update({ risk_label: 'distress' })
                .eq('id', insertedLog.id);

            // Try to send Telegram alert
            if (resident.liaison_id) {
                const { data: profile } = await supabaseAdmin
                    .from('profiles')
                    .select('telegram_chat_id')
                    .eq('id', resident.liaison_id)
                    .single();

                if (profile?.telegram_chat_id) {
                    try {
                        await sendDistressAlert(profile.telegram_chat_id, resident.name, residentId);
                        alertSent = true;
                        console.log(`[DEBUG] Telegram alert sent!`);
                    } catch (alertError: any) {
                        console.error('[DEBUG] Failed to send Telegram alert:', alertError.message);
                    }
                } else {
                    console.log('[DEBUG] No Telegram chat ID configured for liaison');
                }
            }
        }

        return NextResponse.json({
            success: true,
            callLogId: insertedLog.id,
            analysis: aiAnalysis,
            distressTriggered,
            alertSent,
            message: distressTriggered
                ? `⚠️ DISTRESS DETECTED - Resident status updated, ${alertSent ? 'alert sent' : 'no alert sent (check Telegram config)'}`
                : `✅ Call analyzed - No distress detected`
        });

    } catch (err: any) {
        console.error('[DEBUG] Simulate call error:', err);
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
