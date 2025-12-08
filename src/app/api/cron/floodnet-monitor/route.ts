import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { sendFloodAlert } from '@/lib/telegram';

const FLOODNET_THRESHOLD = 4; // inches
const DEPLOYMENT_ID = 'dev_id_nyc_floodnet_deployment_1'; // Default sensor

export async function GET(request: Request) {
    try {
        // Verify cron secret to prevent unauthorized access
        const authHeader = request.headers.get('authorization');
        if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }

        // Fetch latest FloodNet data
        const floodnetResponse = await fetch(
            `https://api.floodnet.nyc/api/v1/deployments/${DEPLOYMENT_ID}/history?start_date=${new Date(Date.now() - 3600000).toISOString()}&end_date=${new Date().toISOString()}`
        );

        if (!floodnetResponse.ok) {
            console.error('FloodNet API error');
            return NextResponse.json({ error: 'FloodNet API unavailable' }, { status: 500 });
        }

        const floodData = await floodnetResponse.json();

        if (!floodData || floodData.length === 0) {
            return NextResponse.json({ message: 'No recent flood data' });
        }

        // Get latest reading
        const latestReading = floodData[floodData.length - 1];
        const currentDepth = latestReading.value || 0;

        console.log(`FloodNet Monitor: Current depth = ${currentDepth} inches`);

        // Check if threshold exceeded
        if (currentDepth >= FLOODNET_THRESHOLD) {
            console.log(`⚠️ FLOOD ALERT: Depth ${currentDepth}in exceeds threshold ${FLOODNET_THRESHOLD}in`);

            // Get all liaisons with Telegram enabled
            const { data: profiles } = await supabase
                .from('profiles')
                .select('telegram_chat_id')
                .not('telegram_chat_id', 'is', null);

            if (profiles && profiles.length > 0) {
                // Send alerts to all liaisons
                const alertPromises = profiles.map(profile =>
                    sendFloodAlert(
                        profile.telegram_chat_id!,
                        DEPLOYMENT_ID,
                        currentDepth
                    )
                );

                await Promise.all(alertPromises);

                return NextResponse.json({
                    alert_sent: true,
                    depth: currentDepth,
                    recipients: profiles.length,
                    message: `Sent flood alerts to ${profiles.length} liaison(s)`
                });
            }

            return NextResponse.json({
                alert_sent: false,
                depth: currentDepth,
                message: 'No liaisons with Telegram configured'
            });
        }

        return NextResponse.json({
            alert_sent: false,
            depth: currentDepth,
            message: `Depth ${currentDepth}in below threshold ${FLOODNET_THRESHOLD}in`
        });

    } catch (error: any) {
        console.error('FloodNet monitor error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
