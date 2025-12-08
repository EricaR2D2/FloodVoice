import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET() {
    try {
        // 1. Check Bot Token
        const botToken = process.env.TELEGRAM_BOT_TOKEN;

        // 2. Simulate Fallback Lookup (Same logic as send-alert)
        console.log('Testing fallback lookup...');
        const { data: profiles, error } = await supabase
            .from('profiles')
            .select('id, email, telegram_chat_id')
            .not('telegram_chat_id', 'is', null)
            .limit(1);

        // 3. Check what we found
        const foundProfile = profiles && profiles.length > 0 ? profiles[0] : null;

        return NextResponse.json({
            status: 'Debug Report',
            bot_token_configured: !!botToken, // Should be true
            fallback_search_result: {
                found: !!foundProfile,
                chat_id: foundProfile?.telegram_chat_id || 'NONE FOUND',
                email: foundProfile?.email,
                error: error?.message
            },
            diagnosis: foundProfile
                ? '✅ SUCCESS: Database has a chat ID. Alerts SHOULD work.'
                : '❌ FAILURE: No profiles found with telegram_chat_id. You need to run the SQL update.'
        });

    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
