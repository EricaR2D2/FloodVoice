import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

export async function POST(request: Request) {
    try {
        const payload = await request.json();

        // Handle /start command
        if (payload.message && payload.message.text === '/start') {
            const chatId = payload.message.chat.id;
            const responseText = `Welcome to FloodVoice! 🌊\n\nYour Chat ID is: \`${chatId}\`\n\nPlease enter this ID in your Dashboard Settings to receive alerts.`;

            await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: chatId,
                    text: responseText,
                    parse_mode: 'Markdown'
                })
            });
        }

        return NextResponse.json({ success: true });
    } catch (err: any) {
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
