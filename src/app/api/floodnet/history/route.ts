import { NextResponse } from 'next/server';

const BASE_URL = 'https://api.floodnet.nyc/api/rest';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const deploymentId = searchParams.get('id') || 'simply-solid-cub';

    // Calculate window (Default: 24h)
    const paramStart = searchParams.get('start');
    const paramEnd = searchParams.get('end');

    const endDate = paramEnd ? new Date(paramEnd) : new Date();
    const startDate = paramStart ? new Date(paramStart) : new Date();

    // If no start provided, default to 24h ago
    if (!paramStart) {
        startDate.setHours(startDate.getHours() - 24);
    }

    // Format dates as ISO strings
    const startStr = startDate.toISOString();
    const endStr = endDate.toISOString();

    // Correct Endpoint: /deployments/flood/{id}/depth?start_time=...&end_time=...
    const apiUrl = `${BASE_URL}/deployments/flood/${deploymentId}/depth?start_time=${startStr}&end_time=${endStr}`;

    try {
        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error(`External API Error: ${response.statusText}`);
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error: any) {
        console.error('FloodNet Proxy Error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
