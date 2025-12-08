import { NextResponse } from 'next/server';

const BASE_URL = 'https://api.floodnet.nyc/api/rest';

// Flooding threshold in mm (converted from ~4 inches = 101.6mm)
const FLOOD_THRESHOLD_MM = 50; // ~2 inches - more sensitive threshold for alerts

interface SensorDeployment {
    deployment_id: string;
    name: string;
    sensor_status: string;
    location: {
        coordinates: [number, number];
    };
}

interface FloodingResult {
    floodingCount: number;
    activeSensors: number;
    floodingSensors: Array<{
        id: string;
        name: string;
        depth_mm: number;
        depth_in: number;
        location: [number, number];
    }>;
    lastUpdated: string;
}

export async function GET(): Promise<NextResponse<FloodingResult | { error: string }>> {
    try {
        // Step 1: Get all sensor deployments
        const deploymentsRes = await fetch(`${BASE_URL}/deployments/flood`);
        if (!deploymentsRes.ok) {
            throw new Error('Failed to fetch sensor deployments');
        }

        const deploymentsData = await deploymentsRes.json();
        const deployments: SensorDeployment[] = deploymentsData.deployments || [];

        // Filter to only active sensors (status = 'good' or similar working states)
        const activeSensors = deployments.filter(d =>
            ['good', 'low_charge', 'noisy'].includes(d.sensor_status)
        );

        // Step 2: Check recent readings for sensors
        const now = new Date();
        const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);

        const floodingSensors: FloodingResult['floodingSensors'] = [];

        // Check ALL active sensors - processed in parallel batches for speed
        const sensorsToCheck = activeSensors;

        const checkPromises = sensorsToCheck.map(async (sensor) => {
            try {
                const depthUrl = `${BASE_URL}/deployments/flood/${sensor.deployment_id}/depth?start_time=${oneHourAgo.toISOString()}&end_time=${now.toISOString()}`;
                const depthRes = await fetch(depthUrl);

                if (depthRes.ok) {
                    const depthData = await depthRes.json();
                    const readings = depthData.depth_data || [];

                    if (readings.length > 0) {
                        // Get the most recent reading
                        const latestReading = readings[readings.length - 1];
                        const depthMm = latestReading.depth_proc_mm || 0;

                        if (depthMm >= FLOOD_THRESHOLD_MM) {
                            return {
                                id: sensor.deployment_id,
                                name: sensor.name,
                                depth_mm: depthMm,
                                depth_in: parseFloat((depthMm * 0.0393701).toFixed(2)),
                                location: sensor.location?.coordinates || [0, 0]
                            };
                        }
                    }
                }
            } catch (e) {
                // Silent fail for individual sensor errors
                console.error(`Error checking sensor ${sensor.deployment_id}:`, e);
            }
            return null;
        });

        const results = await Promise.all(checkPromises);
        results.forEach(r => {
            if (r) floodingSensors.push(r);
        });

        const result: FloodingResult = {
            floodingCount: floodingSensors.length,
            activeSensors: activeSensors.length,
            floodingSensors,
            lastUpdated: now.toISOString()
        };

        return NextResponse.json(result);

    } catch (error: unknown) {
        console.error('Flooding Count API Error:', error);
        const message = error instanceof Error ? error.message : 'Unknown error';
        return NextResponse.json({ error: message }, { status: 500 });
    }
}
