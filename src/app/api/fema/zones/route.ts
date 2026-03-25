import { NextResponse } from 'next/server';

// FEMA NFHL (National Flood Hazard Layer) — Flood Hazard Zones layer (ID 28)
// Bounding box: NYC (lon_min, lat_min, lon_max, lat_max)
const NYC_BBOX = '-74.26,40.47,-73.69,40.93';
const FEMA_URL =
    'https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query' +
    `?geometry=${NYC_BBOX}` +
    '&geometryType=esriGeometryEnvelope' +
    '&spatialRel=esriSpatialRelIntersects' +
    '&outFields=FLD_ZONE,SFHA_TF,ZONE_SUBTY' +
    '&returnGeometry=true' +
    '&f=geojson' +
    '&resultRecordCount=2000';

export async function GET() {
    try {
        const response = await fetch(FEMA_URL, {
            // Cache for 24 hours — FEMA flood zone data changes very rarely
            next: { revalidate: 86400 },
        });

        if (!response.ok) {
            throw new Error(`FEMA API Error: ${response.status} ${response.statusText}`);
        }

        const geojson = await response.json();

        // Simplify: only keep features we care about (SFHA zones: AE, VE, AO, AH, A)
        // and minimal zone X for context. Drop features without geometry.
        const filtered = {
            type: 'FeatureCollection',
            features: (geojson.features || []).filter(
                (f: { geometry: unknown; properties: { FLD_ZONE?: string } }) =>
                    f.geometry && f.properties?.FLD_ZONE
            ),
        };

        return NextResponse.json(filtered, {
            headers: {
                'Cache-Control': 'public, s-maxage=86400, stale-while-revalidate=3600',
            },
        });
    } catch (error: unknown) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        console.error('FEMA Zones Proxy Error:', message);
        return NextResponse.json({ error: message }, { status: 500 });
    }
}

