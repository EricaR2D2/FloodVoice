import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET() {
    // Get ANY profile so we can give the user a valid ID to update
    const { data: profiles } = await supabase
        .from('profiles')
        .select('id, email')
        .limit(1);

    const profile = profiles?.[0];

    return NextResponse.json({
        can_fix: !!profile,
        profile_found: profile,
        fix_command: profile
            ? `UPDATE profiles SET telegram_chat_id = 8414933635 WHERE id = '${profile.id}';`
            : 'No profiles exist in table!'
    });
}
