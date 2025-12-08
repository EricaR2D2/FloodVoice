import { NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/supabase-admin';
import { sendDistressAlert } from '@/lib/telegram';
import { analyzeTranscript } from '@/lib/gemini';

export async function POST(request: Request) {
    try {
        const payload = await request.json();
        const { message } = payload;

        console.log('VAPI Webhook received:', message.type);

        // 1. Handle Function/Tool Calls (Immediate Distress Reporting)
        // VAPI uses 'function-call' (legacy) or 'tool-calls' (new format)
        if (message.type === 'function-call' || message.type === 'tool-calls') {
            let functionName: string = '';
            let functionArgs: any = {};
            let toolCallId: string = '';

            if (message.type === 'function-call') {
                // Legacy format
                functionName = message.functionCall?.name || '';
                toolCallId = message.functionCall?.id || 'default';
                functionArgs = message.functionCall?.parameters
                    ? (typeof message.functionCall.parameters === 'string'
                        ? JSON.parse(message.functionCall.parameters)
                        : message.functionCall.parameters)
                    : {};
            } else {
                // New tool-calls format (VAPI actual structure based on logs)
                // Data is nested: toolCallList[0].function.name and .function.arguments
                const toolCallList = message.toolCallList || [];
                const firstCall = toolCallList[0];

                if (firstCall) {
                    // Extract from the nested 'function' object
                    functionName = firstCall.function?.name || firstCall.name || '';
                    toolCallId = firstCall.id || '';
                    functionArgs = firstCall.function?.arguments || firstCall.parameters || {};

                    console.log('[TOOL-CALLS] Parsed:', {
                        name: functionName,
                        id: toolCallId,
                        parameters: functionArgs
                    });
                }

                if (!functionName) {
                    console.error('[TOOL-CALLS] Could not extract function name from payload');
                    return NextResponse.json({
                        results: [{
                            toolCallId: firstCall?.id || 'unknown',
                            error: 'Could not parse function name from tool-calls payload'
                        }]
                    });
                }
            }

            console.log(`Function called: ${functionName}`, functionArgs);

            // Handle reportStatus (case-insensitive)
            if (functionName?.toLowerCase() === 'reportstatus') {
                const { status, summary } = functionArgs;

                const callMetadata = message.call?.metadata || {};
                const residentId = callMetadata.residentId;

                console.log(`[TOOL-CALLS] reportStatus called with:`, { status, summary, residentId, metadata: callMetadata });

                if (residentId) {
                    console.log(`[TOOL-CALLS] Updating resident ${residentId} to status: ${status}`);

                    // Update Resident Status
                    const { error: updateError } = await supabaseAdmin
                        .from('residents')
                        .update({ status: status })
                        .eq('id', residentId);

                    if (updateError) {
                        console.error(`[TOOL-CALLS] Failed to update resident:`, updateError);
                        return NextResponse.json({
                            results: [{
                                name: functionName,
                                toolCallId: toolCallId,
                                error: `Database update failed: ${updateError.message}`
                            }]
                        });
                    }

                    console.log(`[TOOL-CALLS] Resident updated, now logging call...`);

                    // Log the Call
                    const { error: insertError } = await supabaseAdmin.from('call_logs').insert({
                        resident_id: residentId,
                        vapi_call_id: message.call?.id,
                        summary: summary,
                        risk_label: status
                    });

                    if (insertError) {
                        console.error(`[TOOL-CALLS] Failed to insert call log:`, insertError);
                    } else {
                        console.log(`[TOOL-CALLS] Call logged successfully`);
                    }

                    // Trigger Alert if Distress
                    if (status === 'distress') {
                        console.log(`[TOOL-CALLS] Distress detected! Looking up resident...`);

                        const { data: resident, error: residentError } = await supabaseAdmin
                            .from('residents')
                            .select('name, liaison_id')
                            .eq('id', residentId)
                            .single();

                        console.log(`[TOOL-CALLS] Resident lookup:`, { resident, error: residentError });

                        // MVP Fallback: Use this chat ID if no liaison is configured
                        const FALLBACK_TELEGRAM_CHAT_ID = '8414933635';
                        let telegramChatId: string | null = null;

                        if (resident) {
                            if (!resident.liaison_id || resident.liaison_id === '00000000-0000-0000-0000-000000000000') {
                                console.warn(`[TOOL-CALLS] Resident has no real liaison_id - using fallback`);
                                telegramChatId = FALLBACK_TELEGRAM_CHAT_ID;
                            } else {
                                // Get liaison's Telegram chat ID
                                const { data: profile, error: profileError } = await supabaseAdmin
                                    .from('profiles')
                                    .select('telegram_chat_id')
                                    .eq('id', resident.liaison_id)
                                    .single();

                                console.log(`[TOOL-CALLS] Profile lookup for liaison ${resident.liaison_id}:`, { profile, error: profileError });

                                if (profile?.telegram_chat_id) {
                                    telegramChatId = profile.telegram_chat_id;
                                } else {
                                    console.warn(`[TOOL-CALLS] Liaison has no telegram_chat_id - using fallback`);
                                    telegramChatId = FALLBACK_TELEGRAM_CHAT_ID;
                                }
                            }

                            if (telegramChatId) {
                                console.log(`[TOOL-CALLS] Sending Telegram alert to ${telegramChatId}...`);
                                await sendDistressAlert(telegramChatId, resident.name, residentId);
                                console.log(`[TOOL-CALLS] Telegram alert sent!`);
                            }
                        } else {
                            console.error(`[TOOL-CALLS] Could not find resident ${residentId}`);
                        }
                    }

                    // Return tool result for VAPI (required format with name, toolCallId, result)
                    return NextResponse.json({
                        results: [{
                            name: functionName,
                            toolCallId: toolCallId,
                            result: JSON.stringify({ success: true, status: status })
                        }]
                    });
                } else {
                    // No residentId - return error result (still HTTP 200)
                    return NextResponse.json({
                        results: [{
                            name: functionName,
                            toolCallId: toolCallId,
                            error: 'No residentId found in call metadata'
                        }]
                    });
                }
            } else {
                // Unknown function - return error
                return NextResponse.json({
                    results: [{
                        name: functionName,
                        toolCallId: toolCallId,
                        error: `Unknown function: ${functionName}`
                    }]
                });
            }
        }
        // 2. Handle End of Call Report (Final Summary & Artifacts)
        else if (message.type === 'end-of-call-report') {
            const vapiAnalysis = message.analysis;
            const summary = vapiAnalysis?.summary || "Call completed.";

            // Extract Artifacts
            const artifact = message.artifact || {};
            const recordingUrl = artifact.recordingUrl || null;
            const transcript = artifact.transcript || null;

            const callMetadata = payload.message.call?.metadata || {};
            const residentId = callMetadata.residentId;

            if (residentId) {
                console.log(`End of Call Report for ${residentId}: ${summary}`);

                // Insert Log with Artifacts (initial insert)
                const { data: insertedLog, error: insertError } = await supabaseAdmin
                    .from('call_logs')
                    .insert({
                        resident_id: residentId,
                        vapi_call_id: payload.message.call?.id,
                        summary: summary,
                        risk_label: 'safe', // Default to safe, will update if distress detected
                        recording_url: recordingUrl,
                        transcript: transcript
                    })
                    .select('id')
                    .single();

                if (insertError) {
                    console.error('Failed to insert call log:', insertError);
                    throw insertError;
                }

                // 3. Run AI Analysis if we have transcript or summary
                const textToAnalyze = transcript || summary;
                if (textToAnalyze && insertedLog) {
                    try {
                        console.log(`Running AI analysis for call ${insertedLog.id}...`);
                        const aiAnalysis = await analyzeTranscript(textToAnalyze);

                        if (aiAnalysis) {
                            console.log(`AI Analysis complete: Score=${aiAnalysis.sentiment_score}, Tags=${aiAnalysis.tags.join(', ')}`);

                            // Update call log with AI analysis results
                            await supabaseAdmin
                                .from('call_logs')
                                .update({
                                    tags: aiAnalysis.tags,
                                    sentiment_score: aiAnalysis.sentiment_score,
                                    key_topics: aiAnalysis.key_topics,
                                    processed_at: new Date().toISOString()
                                })
                                .eq('id', insertedLog.id);

                            // 4. Check for Distress (sentiment_score >= 7)
                            if (aiAnalysis.sentiment_score >= 7) {
                                console.log(`DISTRESS DETECTED for resident ${residentId}! Score: ${aiAnalysis.sentiment_score}`);

                                // Update resident status to distress
                                await supabaseAdmin
                                    .from('residents')
                                    .update({ status: 'distress' })
                                    .eq('id', residentId);

                                // Update call log risk label
                                await supabaseAdmin
                                    .from('call_logs')
                                    .update({ risk_label: 'distress' })
                                    .eq('id', insertedLog.id);

                                // Send Telegram Alert
                                console.log(`[END-OF-CALL] Looking up resident for Telegram alert...`);
                                const { data: resident, error: residentError } = await supabaseAdmin
                                    .from('residents')
                                    .select('name, liaison_id')
                                    .eq('id', residentId)
                                    .single();

                                console.log(`[END-OF-CALL] Resident lookup:`, { resident, error: residentError });

                                // MVP Fallback: Use this chat ID if no liaison is configured
                                const FALLBACK_TELEGRAM_CHAT_ID = '8414933635';
                                let telegramChatId: string | null = null;

                                if (resident) {
                                    if (!resident.liaison_id || resident.liaison_id === '00000000-0000-0000-0000-000000000000') {
                                        console.warn(`[END-OF-CALL] Resident has no real liaison_id - using fallback`);
                                        telegramChatId = FALLBACK_TELEGRAM_CHAT_ID;
                                    } else {
                                        const { data: profile, error: profileError } = await supabaseAdmin
                                            .from('profiles')
                                            .select('telegram_chat_id')
                                            .eq('id', resident.liaison_id)
                                            .single();

                                        console.log(`[END-OF-CALL] Profile lookup for liaison ${resident.liaison_id}:`, { profile, error: profileError });

                                        if (profile?.telegram_chat_id) {
                                            telegramChatId = profile.telegram_chat_id;
                                        } else {
                                            console.warn(`[END-OF-CALL] Liaison has no telegram_chat_id - using fallback`);
                                            telegramChatId = FALLBACK_TELEGRAM_CHAT_ID;
                                        }
                                    }

                                    if (telegramChatId) {
                                        console.log(`[END-OF-CALL] Sending Telegram alert to ${telegramChatId}...`);
                                        await sendDistressAlert(telegramChatId, resident.name, residentId);
                                        console.log(`[END-OF-CALL] Telegram alert sent!`);
                                    }
                                } else {
                                    console.error(`[END-OF-CALL] Could not find resident ${residentId}`);
                                }
                            }
                        }
                    } catch (analysisError: any) {
                        // Log but don't fail - the call log was still created
                        console.error('AI Analysis failed:', analysisError.message);
                    }
                }
            }
        }

        return NextResponse.json({ success: true });
    } catch (err: any) {
        console.error("Webhook Error:", err);
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
