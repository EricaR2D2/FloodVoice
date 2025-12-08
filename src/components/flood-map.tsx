'use client';

import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { RefreshCw, MapPin, Waves, Search, Filter } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useFlooding } from '@/contexts/flooding-context';

// Set the Mapbox access token
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

interface Sensor {
    deployment_id: string;
    name: string;
    sensor_status: string;
    location: {
        coordinates: [number, number]; // [lng, lat]
    };
}

interface FloodingSensor {
    id: string;
    name: string;
    depth_mm: number;
    depth_in: number;
}

interface FloodingData {
    floodingCount: number;
    activeSensors: number;
    floodingSensors: FloodingSensor[];
}

export function FloodMap({ className }: { className?: string }) {
    const mapContainer = useRef<HTMLDivElement>(null);
    const map = useRef<mapboxgl.Map | null>(null);
    const markersRef = useRef<mapboxgl.Marker[]>([]);

    const [sensors, setSensors] = useState<Sensor[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [mapLoaded, setMapLoaded] = useState(false);

    // Use shared flooding context
    const flooding = useFlooding();
    const floodingData = {
        floodingCount: flooding.floodingCount,
        activeSensors: flooding.activeSensors,
        floodingSensors: flooding.floodingSensors
    };

    // Search and filter state
    const [searchQuery, setSearchQuery] = useState('');
    const [showFloodingOnly, setShowFloodingOnly] = useState(false);

    // NYC center coordinates
    const NYC_CENTER: [number, number] = [-73.935242, 40.730610];
    const NYC_ZOOM = 10;

    // Fetch sensor data (fast)
    const fetchSensors = async () => {
        try {
            const res = await fetch('/api/floodnet/sensors');
            if (res.ok) {
                const data = await res.json();
                setSensors(data.deployments || []);
            }
        } catch (e) {
            console.error('Failed to fetch sensors:', e);
        }
    };

    // Fetch data (sensors only - flooding comes from context)
    const fetchData = async () => {
        setIsLoading(true);
        await fetchSensors();
        setIsLoading(false);
    };

    // Get marker color based on sensor status and flooding
    const getMarkerColor = (sensor: Sensor): string => {
        // Check if sensor is offline
        const offlineStatuses = ['dead', 'retired', 'signal'];
        if (offlineStatuses.includes(sensor.sensor_status)) {
            return '#64748b'; // Gray - offline
        }

        // Check if this sensor is flooding
        const isFlooding = floodingData?.floodingSensors?.some(
            f => f.id === sensor.deployment_id
        );

        if (isFlooding) {
            return '#ef4444'; // Red - flooding
        }

        // Check if sensor has issues
        const warningStatuses = ['low_charge', 'noisy', 'non-ota'];
        if (warningStatuses.includes(sensor.sensor_status)) {
            return '#f59e0b'; // Amber - warning
        }

        return '#22c55e'; // Green - good
    };

    // Initialize map
    useEffect(() => {
        if (!mapContainer.current || map.current) return;

        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: 'mapbox://styles/mapbox/dark-v11',
            center: NYC_CENTER,
            zoom: NYC_ZOOM,
            attributionControl: false
        });

        map.current.addControl(
            new mapboxgl.NavigationControl({ showCompass: false }),
            'top-right'
        );

        map.current.on('load', () => {
            setMapLoaded(true);
        });

        return () => {
            map.current?.remove();
            map.current = null;
        };
    }, []);

    // Fetch data on mount
    useEffect(() => {
        fetchData();

        // Auto-refresh every 5 minutes
        const interval = setInterval(fetchData, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    // Update markers when data or filters change
    useEffect(() => {
        if (!map.current || !mapLoaded || sensors.length === 0) return;

        // Apply filters to sensors
        const sensorsToShow = sensors.filter(sensor => {
            const matchesSearch = searchQuery === '' ||
                sensor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                sensor.deployment_id.toLowerCase().includes(searchQuery.toLowerCase());

            const isFlooding = floodingData?.floodingSensors?.some(f => f.id === sensor.deployment_id);
            const matchesFloodingFilter = !showFloodingOnly || isFlooding;

            return matchesSearch && matchesFloodingFilter;
        });

        // Clear existing markers
        markersRef.current.forEach(m => m.remove());
        markersRef.current = [];

        // Add new markers for filtered sensors
        sensorsToShow.forEach(sensor => {
            if (!sensor.location?.coordinates) return;

            const [lng, lat] = sensor.location.coordinates;
            const color = getMarkerColor(sensor);

            // Check if flooding
            const floodingInfo = floodingData?.floodingSensors?.find(
                f => f.id === sensor.deployment_id
            );

            // Create custom marker element
            const el = document.createElement('div');
            el.className = 'flood-sensor-marker';
            const baseBoxShadow = floodingInfo ? `0 0 10px ${color}` : `0 0 4px ${color}`;
            el.style.cssText = `
                width: 12px;
                height: 12px;
                background-color: ${color};
                border: 2px solid rgba(255,255,255,0.8);
                border-radius: 50%;
                cursor: pointer;
                transition: box-shadow 0.2s, border-width 0.2s;
                box-shadow: ${baseBoxShadow};
            `;

            // Add pulse animation for flooding sensors
            if (floodingInfo) {
                el.style.animation = 'pulse 1.5s infinite';
            }

            // Hover effect using glow instead of scale (prevents position jump)
            el.addEventListener('mouseenter', () => {
                el.style.boxShadow = `0 0 15px ${color}, 0 0 25px ${color}`;
                el.style.borderWidth = '3px';
            });
            el.addEventListener('mouseleave', () => {
                el.style.boxShadow = baseBoxShadow;
                el.style.borderWidth = '2px';
            });

            // Create popup content
            const statusLabel = floodingInfo
                ? `🔴 FLOODING: ${floodingInfo.depth_in}" depth`
                : sensor.sensor_status === 'good'
                    ? '🟢 Active - No flooding'
                    : `⚪ ${sensor.sensor_status}`;

            const popup = new mapboxgl.Popup({
                offset: 15,
                closeButton: false,
                className: 'flood-map-popup'
            }).setHTML(`
                <div style="font-family: system-ui; padding: 4px;">
                    <div style="font-weight: 600; font-size: 13px; margin-bottom: 4px;">
                        ${sensor.name}
                    </div>
                    <div style="font-size: 11px; color: #94a3b8;">
                        ${statusLabel}
                    </div>
                </div>
            `);

            const marker = new mapboxgl.Marker({ element: el })
                .setLngLat([lng, lat])
                .setPopup(popup)
                .addTo(map.current!);

            markersRef.current.push(marker);
        });

        // If there are flooding sensors, fly to the first one
        if (floodingData?.floodingSensors && floodingData.floodingSensors.length > 0) {
            const floodingSensor = sensors.find(
                s => s.deployment_id === floodingData.floodingSensors[0].id
            );
            if (floodingSensor?.location?.coordinates) {
                map.current.flyTo({
                    center: floodingSensor.location.coordinates,
                    zoom: 13,
                    duration: 2000
                });
            }
        }
    }, [sensors, floodingData, mapLoaded, searchQuery, showFloodingOnly]);

    const activeCount = sensors.filter(s => s.sensor_status === 'good').length;
    const offlineCount = sensors.filter(s => ['dead', 'retired'].includes(s.sensor_status)).length;

    // Filter sensors based on search and flooding toggle
    const filteredSensors = sensors.filter(sensor => {
        // Search filter
        const matchesSearch = searchQuery === '' ||
            sensor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            sensor.deployment_id.toLowerCase().includes(searchQuery.toLowerCase());

        // Flooding filter
        const isFlooding = floodingData?.floodingSensors?.some(f => f.id === sensor.deployment_id);
        const matchesFloodingFilter = !showFloodingOnly || isFlooding;

        return matchesSearch && matchesFloodingFilter;
    });

    return (
        <div className={cn("glass-panel rounded-xl overflow-hidden flex flex-col", className)}>
            {/* Header with Search and Filter */}
            <div className="p-3 border-b border-white/5 flex flex-wrap items-center gap-3">
                {/* Title */}
                <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-blue-500/10">
                        <MapPin className="w-4 h-4 text-blue-400" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-white text-sm">Flood Sensor Network</h3>
                        <p className="text-[10px] text-slate-400">
                            {sensors.length} sensors • {activeCount} active
                        </p>
                    </div>
                </div>

                {/* Search Input */}
                <div className="relative flex-1 min-w-[120px] max-w-[180px]">
                    <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500" />
                    <input
                        type="text"
                        placeholder="Search..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-7 pr-2 py-1 text-xs bg-slate-800/50 border border-white/10 rounded text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500/50"
                    />
                </div>

                {/* Flooding Toggle with integrated count */}
                <button
                    onClick={() => setShowFloodingOnly(!showFloodingOnly)}
                    className={cn(
                        "flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium transition-all",
                        showFloodingOnly
                            ? "bg-red-500 border border-red-500 text-white"  // ON: solid red
                            : floodingData && floodingData.floodingCount > 0
                                ? "bg-red-500/20 border border-red-500/50 text-red-400"  // OFF but flooding
                                : "bg-slate-800/50 border border-white/10 text-slate-400 hover:border-white/20"  // OFF no flooding
                    )}
                >
                    <Filter className="w-3 h-3" />
                    Flooding
                    {floodingData && floodingData.floodingCount > 0 && (
                        <span className="ml-1 px-1.5 py-0.5 bg-red-500 text-white rounded-full text-[10px] leading-none">
                            {floodingData.floodingCount}
                        </span>
                    )}
                </button>

                {/* Refresh Button */}
                <button
                    onClick={fetchData}
                    disabled={isLoading}
                    className="p-1.5 hover:bg-white/5 rounded transition-colors ml-auto"
                    title="Refresh data"
                >
                    <RefreshCw className={cn(
                        "w-3.5 h-3.5 text-slate-400",
                        isLoading && "animate-spin"
                    )} />
                </button>
            </div>

            {/* Map Container */}
            <div className="relative flex-1 min-h-[350px]">
                <div
                    ref={mapContainer}
                    className="absolute inset-0"
                    style={{ width: '100%', height: '100%' }}
                />

                {/* Loading overlay */}
                {isLoading && !mapLoaded && (
                    <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center z-10">
                        <span className="text-sm text-blue-400">Loading map...</span>
                    </div>
                )}

                {/* Legend */}
                <div className="absolute bottom-4 left-4 glass-panel p-3 rounded-lg text-xs space-y-1.5 z-10">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-green-500 border border-white/50" />
                        <span className="text-slate-300">Active</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-amber-500 border border-white/50" />
                        <span className="text-slate-300">Warning</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-500 border border-white/50 shadow-[0_0_8px_#ef4444]" />
                        <span className="text-slate-300">Flooding</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-slate-500 border border-white/50" />
                        <span className="text-slate-300">Offline</span>
                    </div>
                </div>
            </div>

            {/* CSS for pulse animation and Mapbox */}
            <style jsx global>{`
                /* Essential Mapbox GL styles */
                .mapboxgl-map {
                    position: absolute;
                    top: 0;
                    bottom: 0;
                    left: 0;
                    right: 0;
                }
                .mapboxgl-canvas {
                    position: absolute;
                    left: 0;
                    top: 0;
                }
                .mapboxgl-canvas-container {
                    position: absolute;
                    top: 0;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    overflow: hidden;
                }
                .mapboxgl-ctrl-group {
                    background: #1e293b;
                    border-radius: 8px;
                }
                .mapboxgl-ctrl-group button {
                    background-color: #1e293b;
                    border: none;
                }
                .mapboxgl-ctrl-group button:hover {
                    background-color: #334155;
                }
                .mapboxgl-ctrl-group button span {
                    filter: invert(1);
                }
                
                @keyframes pulse {
                    0%, 100% { box-shadow: 0 0 10px #ef4444; }
                    50% { box-shadow: 0 0 20px #ef4444, 0 0 30px #ef4444; }
                }
                .flood-map-popup .mapboxgl-popup-content {
                    background: #1e293b;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: white;
                }
                .flood-map-popup .mapboxgl-popup-tip {
                    border-top-color: #1e293b;
                }
            `}</style>
        </div>
    );
}
