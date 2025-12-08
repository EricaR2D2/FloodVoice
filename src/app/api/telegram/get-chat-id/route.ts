import { NextResponse } from 'next/server';

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

export async function GET() {
    if (!TELEGRAM_BOT_TOKEN) {
        return NextResponse.json({ error: 'TELEGRAM_BOT_TOKEN not set in .env.local' }, { status: 500 });
    }

    try {
        // Fetch recent updates from Telegram
        const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates`);
        const data = await response.json();

        if (!data.ok) {
            return NextResponse.json({ error: 'Failed to fetch updates from Telegram', details: data }, { status: 500 });
        }

        // Extract chat IDs from recent messages
        const chatIds = data.result
            .filter((update: any) => update.message?.chat?.id)
            .map((update: any) => ({
                chat_id: update.message.chat.id,
                username: update.message.chat.username || 'N/A',
                first_name: update.message.chat.first_name || 'N/A',
                message_text: update.message.text
            }));

        return NextResponse.json({
            message: 'Recent chat IDs from bot interactions',
            chats: chatIds,
            instructions: 'If you don\'t see your chat ID, send /start to @FloodVoice_bot in Telegram and refresh this page.'
        });

    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
