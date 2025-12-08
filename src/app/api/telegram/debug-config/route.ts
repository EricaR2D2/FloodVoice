import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET() {
    try {
        const botToken = process.env.TELEGRAM_BOT_TOKEN;

        if (!botToken) {
            return NextResponse.json({ error: 'TELEGRAM_BOT_TOKEN not set' });
        }

        // Get current user (you'll need to be logged in)
        const { data: { user } } = await supabase.auth.getUser();

        if (!user) {
            return NextResponse.json({ error: 'Not authenticated' });
        }

        // Check if profile has telegram_chat_id
        const { data: profile } = await supabase
            .from('profiles')
            .select('telegram_chat_id, email')
            .eq('id', user.id)
            .single();

        // Get a sample resident to test with
        const { data: sampleResident } = await supabase
            .from('residents')
            .select('id, name, liaison_id')
            .limit(1)
            .single();

        return NextResponse.json({
            bot_token_set: !!botToken,
            bot_token_masked: botToken ? `${botToken.slice(0, 4)}...${botToken.slice(-4)}` : null,
            current_user_id: user.id,
            current_user_email: user.email,
            profile_telegram_chat_id: profile?.telegram_chat_id || 'NOT SET',
            profile_email: profile?.email,
            sample_resident: sampleResident,
            liaison_match: sampleResident?.liaison_id === user.id ? 'YES' : 'NO - This resident belongs to a different liaison',
            instructions: profile?.telegram_chat_id
                ? 'Telegram is configured. Try marking a resident as distress.'
                : 'Run: UPDATE profiles SET telegram_chat_id = 8414933635 WHERE id = \'' + user.id + '\';'
        });

    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
