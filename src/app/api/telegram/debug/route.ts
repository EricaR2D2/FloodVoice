import { NextResponse } from 'next/server';

export async function GET() {
    const token = process.env.TELEGRAM_BOT_TOKEN;

    if (!token) {
        return NextResponse.json({
            error: 'TELEGRAM_BOT_TOKEN is not set',
            hint: 'Make sure you added it to .env.local and restarted the dev server'
        });
    }

    // Show first/last 4 chars only for security
    const masked = `${token.slice(0, 4)}...${token.slice(-4)}`;

    return NextResponse.json({
        status: 'Token found',
        masked_token: masked,
        token_length: token.length,
        instructions: 'If this looks wrong, check .env.local and restart npm run dev'
    });
}
