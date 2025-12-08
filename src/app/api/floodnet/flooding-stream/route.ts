import { NextResponse } from 'next/server';

const BASE_URL = 'https://api.floodnet.nyc/api/rest';
const FLOOD_THRESHOLD_MM = 50;

interface SensorDeployment {
    deployment_id: string;
    name: string;
    sensor_status: string;
    location: {
        coordinates: [number, number];
    };
}

// This endpoint streams flooding updates as sensors are checked
export async function GET(): Promise<Response> {
    const encoder = new TextEncoder();

    const stream = new ReadableStream({
        async start(controller) {
            try {
                // Step 1: Get all sensor deployments
                const deploymentsRes = await fetch(`${BASE_URL}/deployments/flood`);
                if (!deploymentsRes.ok) {
                    controller.enqueue(encoder.encode(`data: ${JSON.stringify({ error: 'Failed to fetch sensors' })}\n\n`));
                    controller.close();
                    return;
                }

                const deploymentsData = await deploymentsRes.json();
                const deployments: SensorDeployment[] = deploymentsData.deployments || [];

                // Filter to only active sensors
                const activeSensors = deployments.filter(d =>
                    ['good', 'low_charge', 'noisy'].includes(d.sensor_status)
                );

                // Send initial state
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                    type: 'init',
                    floodingCount: 0,
                    totalToCheck: activeSensors.length,
                    checked: 0,
                    floodingSensors: []
                })}\n\n`));

                const now = new Date();
                const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);

                let floodingCount = 0;
                let checked = 0;
                const floodingSensors: Array<{
                    id: string;
                    name: string;
                    depth_mm: number;
                    depth_in: number;
                }> = [];

                // Check sensors in batches of 5 for better parallelism
                const batchSize = 5;
                for (let i = 0; i < activeSensors.length; i += batchSize) {
                    const batch = activeSensors.slice(i, i + batchSize);

                    const batchResults = await Promise.all(
                        batch.map(async (sensor) => {
                            try {
                                const depthUrl = `${BASE_URL}/deployments/flood/${sensor.deployment_id}/depth?start_time=${oneHourAgo.toISOString()}&end_time=${now.toISOString()}`;
                                const depthRes = await fetch(depthUrl);

                                if (depthRes.ok) {
                                    const depthData = await depthRes.json();
                                    const readings = depthData.depth_data || [];

                                    if (readings.length > 0) {
                                        const latestReading = readings[readings.length - 1];
                                        const depthMm = latestReading.depth_proc_mm || 0;

                                        if (depthMm >= FLOOD_THRESHOLD_MM) {
                                            return {
                                                id: sensor.deployment_id,
                                                name: sensor.name,
                                                depth_mm: depthMm,
                                                depth_in: parseFloat((depthMm * 0.0393701).toFixed(2))
                                            };
                                        }
                                    }
                                }
                            } catch (e) {
                                // Silent fail for individual sensors
                            }
                            return null;
                        })
                    );

                    // Process batch results
                    batchResults.forEach(result => {
                        checked++;
                        if (result) {
                            floodingCount++;
                            floodingSensors.push(result);
                        }
                    });

                    // Send progress update
                    controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                        type: 'update',
                        floodingCount,
                        checked,
                        totalToCheck: activeSensors.length,
                        floodingSensors
                    })}\n\n`));
                }

                // Send final result
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                    type: 'complete',
                    floodingCount,
                    activeSensors: activeSensors.length,
                    floodingSensors,
                    lastUpdated: new Date().toISOString()
                })}\n\n`));

            } catch (error) {
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                    type: 'error',
                    error: error instanceof Error ? error.message : 'Unknown error'
                })}\n\n`));
            }

            controller.close();
        }
    });

    return new Response(stream, {
        headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        },
    });
}
