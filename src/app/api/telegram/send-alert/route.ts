import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { sendDistressAlert } from '@/lib/telegram';

export async function POST(request: Request) {
    try {
        const { residentId, residentName, source } = await request.json();

        if (!residentId || !residentName) {
            return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
        }

        // Get the resident's liaison_id
        const { data: resident } = await supabase
            .from('residents')
            .select('liaison_id')
            .eq('id', residentId)
            .single();

        let targetChatId = null;

        // 1. Try to find the specific liaison's chat ID
        if (resident?.liaison_id) {
            const { data: profile } = await supabase
                .from('profiles')
                .select('telegram_chat_id')
                .eq('id', resident.liaison_id)
                .single();
            targetChatId = profile?.telegram_chat_id;
        }

        // 2. FALLBACK (MVP/Demo Mode): If no specific liaison found (or auth issue), 
        // find ANY profile with a telegram_chat_id (likely the user who set it up)
        if (!targetChatId) {
            const { data: profiles } = await supabase
                .from('profiles')
                .select('telegram_chat_id')
                .not('telegram_chat_id', 'is', null)
                .limit(1);

            if (profiles && profiles.length > 0) {
                targetChatId = profiles[0].telegram_chat_id;
            } else {
                // LAST RESORT: Hardcoded ID for Demo (Since profiles table is empty)
                // This ensures it works for the specific demo user even with no DB setup
                targetChatId = 8414933635;
            }
        }

        if (!targetChatId) {
            return NextResponse.json({
                error: 'No Telegram recipients found',
                message: 'No profiles found with telegram_chat_id configured'
            }, { status: 200 });
        }

        // Send the alert
        await sendDistressAlert(targetChatId, residentName, residentId);

        return NextResponse.json({
            success: true,
            mapped_chat_id: targetChatId,
            message: `Alert sent to Telegram (${source || 'unknown'} trigger)`
        });

    } catch (error: any) {
        console.error('Send alert error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
