'use client';

import { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Droplets, RefreshCw, MapPin, TrendingUp, Search, Filter, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useFlooding } from '@/contexts/flooding-context';

export function FloodNetGraph({ className }: { className?: string }) {
    const [data, setData] = useState<any[]>([]);
    const [sensors, setSensors] = useState<any[]>([]);
    const [selectedSensor, setSelectedSensor] = useState('simply-solid-cub');
    const [timeRange, setTimeRange] = useState('24h');
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [sensorSearch, setSensorSearch] = useState('');
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [hasAutoSelected, setHasAutoSelected] = useState(false);

    // Use shared flooding context
    const flooding = useFlooding();
    const floodingSensors = flooding.floodingSensors;
    const floodingSensorIds = floodingSensors.map(s => s.id);

    useEffect(() => {
        fetchSensors();
    }, []);

    // Auto-select first flooding sensor when detected
    useEffect(() => {
        if (floodingSensors.length > 0 && !hasAutoSelected) {
            setSelectedSensor(floodingSensors[0].id);
            setHasAutoSelected(true);
        }
    }, [floodingSensors, hasAutoSelected]);

    useEffect(() => {
        if (selectedSensor) {
            fetchData(selectedSensor, timeRange);
        }
    }, [selectedSensor, timeRange]);

    const fetchSensors = async () => {
        try {
            const res = await fetch('/api/floodnet/sensors');
            if (res.ok) {
                const data = await res.json();
                setSensors(data.deployments || []);
            }
        } catch (e) {
            console.error("Failed to load sensors", e);
        }
    };

    // Smart Downsampling: Preserves Peaks
    // If we have 1000 points, we bucket them and pick the MAX value per bucket.
    // This ensures "spikes" (floods) don't get averaged out, and makes them easier to hover.
    const downsampleData = (rawData: any[], targetPoints: number = 150) => {
        if (rawData.length <= targetPoints) return rawData;

        const bucketSize = Math.ceil(rawData.length / targetPoints);
        const sampled = [];

        for (let i = 0; i < rawData.length; i += bucketSize) {
            const bucket = rawData.slice(i, i + bucketSize);
            // Find the item with the MAX depth in this bucket
            const maxItem = bucket.reduce((prev, curr) =>
                (parseFloat(curr.depth) > parseFloat(prev.depth) ? curr : prev)
                , bucket[0]);

            sampled.push(maxItem);
        }
        return sampled;
    };

    const fetchData = async (sensorId: string, range: string) => {
        setIsLoading(true);
        setError('');
        try {
            // Calculate Start/End based on Range
            const now = new Date();
            const start = new Date();
            if (range === '7d') start.setDate(now.getDate() - 7);
            else if (range === '30d') start.setDate(now.getDate() - 30);
            else start.setHours(now.getHours() - 24);

            const queryParams = new URLSearchParams({
                id: sensorId,
                start: start.toISOString(),
                end: now.toISOString()
            });

            const res = await fetch(`/api/floodnet/history?${queryParams}`);
            if (!res.ok) throw new Error('Failed to load sensor data');

            const rawData = await res.json();
            const items = rawData.depth_data || (Array.isArray(rawData) ? rawData : []);

            let processed = items.map((item: any) => ({
                time: new Date(item.time).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit' }),
                depth: (item.depth_proc_mm * 0.0393701).toFixed(2),
                rawTime: item.time
            }));

            // Fallback: If no data exists (dry/offline), show a meaningful 0-line graph
            if (processed.length === 0) {
                const points = range === '24h' ? 24 : (range === '7d' ? 7 : 15);
                const step = (now.getTime() - start.getTime()) / points;
                processed = Array.from({ length: points + 1 }, (_, i) => {
                    const d = new Date(start.getTime() + (i * step));
                    return {
                        time: d.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit' }),
                        depth: "0.00",
                        rawTime: d.toISOString()
                    };
                });
            }

            // Ensure chronological order
            processed.sort((a: any, b: any) => new Date(a.rawTime).getTime() - new Date(b.rawTime).getTime());

            // Apply Downsampling if needed (e.g. for 30d view which might have thousands of points)
            const finalData = downsampleData(processed);

            setData(finalData);
        } catch (err: any) {
            console.error(err);
            setError(err.message || 'Sensor offline');
        }
        setIsLoading(false);
    };

    const currentDepth = data.length > 0 ? parseFloat(data[data.length - 1].depth) : 0;
    const maxDepth = data.length > 0 ? data.reduce((max, item) => Math.max(max, parseFloat(item.depth)), 0) : 0;
    const isDanger = currentDepth > 4;

    // Helper to format sensor names
    const formatName = (name: string) => {
        if (!name) return name;
        return name
            .replace(/^Q\s*-\s*/, 'Queens - ')
            .replace(/^BK\s*-\s*/, 'Brooklyn - ')
            .replace(/^BX\s*-\s*/, 'Bronx - ')
            .replace(/^M\s*-\s*/, 'Manhattan - ')
            .replace(/^SI\s*-\s*/, 'Staten Island - ');
    };

    return (
        <div className={cn("glass-panel p-6 rounded-xl flex flex-col h-[400px]", className)}>
            {/* Flooding Now - Compact inline */}
            {floodingSensors.length > 0 && (
                <div className="mb-2 flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-medium text-red-400 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" />
                        Flooding:
                    </span>
                    {floodingSensors.slice(0, 3).map(sensor => (
                        <button
                            key={sensor.id}
                            onClick={() => setSelectedSensor(sensor.id)}
                            className={cn(
                                "px-2 py-0.5 rounded text-[11px] transition-all",
                                selectedSensor === sensor.id
                                    ? "bg-red-500 text-white"
                                    : "bg-red-500/20 text-red-300 hover:bg-red-500/30"
                            )}
                        >
                            {formatName(sensor.name).split(' - ')[1]?.substring(0, 15) || sensor.name.substring(0, 15)}... {sensor.depth_in}″
                        </button>
                    ))}
                    {floodingSensors.length > 3 && (
                        <span className="text-[11px] text-slate-500">+{floodingSensors.length - 3}</span>
                    )}
                </div>
            )}

            <div className="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-3">
                <div className="flex items-center gap-3">
                    <div className={cn("p-2 rounded-lg transition-colors", isDanger ? "bg-red-500/10" : "bg-blue-500/10")}>
                        <Droplets className={cn("w-5 h-5", isDanger ? "text-red-500" : "text-blue-400")} />
                    </div>
                    <div>
                        <h3 className="font-semibold text-white">
                            {timeRange === '24h' ? 'Live Water Level' : 'Water Level History'}
                        </h3>
                        <div className="flex flex-col sm:flex-row sm:items-center gap-2 mt-1">
                            <div className="flex items-center gap-2">
                                <MapPin className="w-3 h-3 text-slate-500" />
                                {/* Searchable Dropdown */}
                                <div className="relative">
                                    <div className="flex items-center">
                                        <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500 pointer-events-none z-10" />
                                        <input
                                            type="text"
                                            placeholder={sensors.find(s => s.deployment_id === selectedSensor)?.name ? formatName(sensors.find(s => s.deployment_id === selectedSensor)?.name).substring(0, 18) + '...' : 'Select sensor...'}
                                            value={sensorSearch}
                                            onChange={(e) => setSensorSearch(e.target.value)}
                                            onClick={() => setIsDropdownOpen(true)}
                                            onFocus={() => setIsDropdownOpen(true)}
                                            onBlur={() => setTimeout(() => setIsDropdownOpen(false), 150)}
                                            className="w-[160px] pl-7 pr-2 py-1 text-xs bg-slate-900 border border-slate-800 text-slate-200 rounded hover:border-slate-600 transition-colors focus:outline-none focus:border-blue-500/50"
                                        />
                                    </div>
                                    {isDropdownOpen && (
                                        <div className="absolute top-full left-0 mt-1 w-[220px] max-h-[250px] overflow-auto bg-slate-900 border border-slate-700 rounded-lg shadow-lg z-50">
                                            {sensors
                                                .filter(s =>
                                                    sensorSearch === '' ||
                                                    s.name.toLowerCase().includes(sensorSearch.toLowerCase()) ||
                                                    s.deployment_id.toLowerCase().includes(sensorSearch.toLowerCase())
                                                )
                                                .map(s => (
                                                    <button
                                                        key={s.deployment_id}
                                                        onMouseDown={(e) => {
                                                            e.preventDefault();
                                                            setSelectedSensor(s.deployment_id);
                                                            setSensorSearch('');
                                                            setIsDropdownOpen(false);
                                                        }}
                                                        className={cn(
                                                            "w-full text-left px-3 py-2 text-xs hover:bg-slate-800 transition-colors",
                                                            selectedSensor === s.deployment_id ? "bg-blue-500/20 text-blue-400" : "text-slate-300"
                                                        )}
                                                    >
                                                        {formatName(s.name)}
                                                    </button>
                                                ))}
                                            {sensors.filter(s =>
                                                sensorSearch === '' ||
                                                s.name.toLowerCase().includes(sensorSearch.toLowerCase()) ||
                                                s.deployment_id.toLowerCase().includes(sensorSearch.toLowerCase())
                                            ).length === 0 && (
                                                    <div className="px-3 py-2 text-xs text-slate-500">No sensors found</div>
                                                )}
                                        </div>
                                    )}
                                </div>
                            </div>

                            <span className="hidden sm:inline text-slate-700">|</span>

                            <select
                                value={timeRange}
                                onChange={(e) => setTimeRange(e.target.value)}
                                className="bg-transparent text-xs text-blue-400 font-medium border-none outline-none cursor-pointer hover:text-blue-300 transition-colors appearance-none"
                            >
                                <option value="24h" className="bg-slate-900">Last 24 Hours</option>
                                <option value="7d" className="bg-slate-900">Last 7 Days</option>
                                <option value="30d" className="bg-slate-900">Last 30 Days</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-6 self-end md:self-auto">
                    <div className="text-right">
                        <div className={cn("text-2xl font-bold", isDanger ? "text-red-500" : "text-white")}>
                            {isLoading ? "--" : currentDepth}<span className="text-sm font-normal text-slate-500"> in</span>
                        </div>
                        <div className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Current Depth</div>
                    </div>

                    <div className="text-right hidden sm:block">
                        <div className="text-2xl font-bold text-blue-400">
                            {isLoading ? "--" : maxDepth.toFixed(2)}<span className="text-sm font-normal text-slate-500"> in</span>
                        </div>
                        <div className="text-[10px] text-slate-400 uppercase tracking-widest font-bold flex items-center justify-end gap-1">
                            <TrendingUp className="w-3 h-3" /> Peak
                        </div>
                    </div>

                    <button
                        onClick={() => fetchData(selectedSensor, timeRange)}
                        disabled={isLoading}
                        className="p-2 hover:bg-white/5 rounded-full text-slate-500 transition-colors"
                    >
                        <RefreshCw className={cn("w-4 h-4", isLoading && "animate-spin")} />
                    </button>
                </div>
            </div>

            <div className="flex-1 w-full min-h-0 relative">
                {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 z-10 backdrop-blur-sm">
                        <span className="text-sm text-blue-400 font-medium">Syncing with sensors...</span>
                    </div>
                )}

                {error ? (
                    <div className="absolute inset-0 flex items-center justify-center text-red-400 text-sm">
                        {error}
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data}>
                            <defs>
                                <linearGradient id="colorDepth" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={isDanger ? "#ef4444" : "#38bdf8"} stopOpacity={0.3} />
                                    <stop offset="95%" stopColor={isDanger ? "#ef4444" : "#38bdf8"} stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} vertical={false} />
                            <XAxis
                                dataKey="time"
                                stroke="#64748b"
                                fontSize={10}
                                tickLine={false}
                                axisLine={false}
                                minTickGap={30}
                            />
                            <YAxis
                                stroke="#64748b"
                                fontSize={10}
                                tickLine={false}
                                axisLine={false}
                                unit=" in"
                            />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '8px' }}
                                itemStyle={{ color: '#38bdf8' }}
                                formatter={(value: any) => [`${value} in`, 'Depth']}
                                labelStyle={{ color: '#94a3b8' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="depth"
                                stroke={isDanger ? "#ef4444" : "#38bdf8"}
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#colorDepth)"
                                animationDuration={1500}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                )}
            </div>
        </div>
    );
}
