const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const APP_URL = process.env.NEXT_PUBLIC_APP_URL || 'https://floodvoice.vercel.app';

export async function sendTelegramMessage(chatId: number | string, text: string, parseMode: 'HTML' | 'Markdown' = 'HTML') {
    if (!TELEGRAM_BOT_TOKEN) {
        console.error('TELEGRAM_BOT_TOKEN not configured');
        return null;
    }

    try {
        const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: chatId,
                text: text,
                parse_mode: parseMode
            })
        });

        if (!response.ok) {
            const error = await response.json();
            console.error('Telegram API error:', error);
            return null;
        }

        return response.json();
    } catch (error) {
        console.error('Failed to send Telegram message:', error);
        return null;
    }
}

export async function sendDistressAlert(chatId: number | string, residentName: string, residentId: string) {
    const message = `🚨 <b>DISTRESS ALERT</b>\n\n` +
        `Resident: <b>${residentName}</b>\n` +
        `Status: <b>IN DISTRESS</b>\n\n` +
        `⚠️ Immediate action required.\n\n` +
        `View dashboard: ${APP_URL}/dashboard/residents`;

    return sendTelegramMessage(chatId, message);
}

export async function sendFloodAlert(chatId: number | string, sensorName: string, depth: number) {
    const message = `⚠️ <b>FLOOD RISK DETECTED</b>\n\n` +
        `Sensor: <b>${sensorName}</b>\n` +
        `Depth: <b>${depth.toFixed(2)} inches</b>\n\n` +
        `Review your pod and consider triggering emergency check-ins.\n\n` +
        `Dashboard: ${APP_URL}/dashboard`;

    return sendTelegramMessage(chatId, message);
}
