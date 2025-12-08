import { NextResponse } from 'next/server';

export async function GET() {
    try {
        const response = await fetch('https://api.floodnet.nyc/api/rest/deployments/flood');

        if (!response.ok) {
            throw new Error(`External API Error: ${response.statusText}`);
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error: any) {
        console.error('FloodNet Sensors Proxy Error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
