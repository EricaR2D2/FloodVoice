'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface FloodingSensor {
    id: string;
    name: string;
    depth_mm: number;
    depth_in: number;
}

interface FloodingContextType {
    floodingCount: number;
    floodingSensors: FloodingSensor[];
    isLoading: boolean;
    isComplete: boolean;
    checked: number;
    totalToCheck: number;
    activeSensors: number;
}

const FloodingContext = createContext<FloodingContextType>({
    floodingCount: 0,
    floodingSensors: [],
    isLoading: true,
    isComplete: false,
    checked: 0,
    totalToCheck: 0,
    activeSensors: 0,
});

export function useFlooding() {
    return useContext(FloodingContext);
}

export function FloodingProvider({ children }: { children: ReactNode }) {
    const [data, setData] = useState<FloodingContextType>({
        floodingCount: 0,
        floodingSensors: [],
        isLoading: true,
        isComplete: false,
        checked: 0,
        totalToCheck: 0,
        activeSensors: 0,
    });

    useEffect(() => {
        const fetchFloodingData = async () => {
            try {
                const response = await fetch('/api/floodnet/flooding-stream');
                const reader = response.body?.getReader();
                const decoder = new TextDecoder();

                if (!reader) return;

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const text = decoder.decode(value);
                    const lines = text.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const parsed = JSON.parse(line.slice(6));

                                setData({
                                    floodingCount: parsed.floodingCount || 0,
                                    floodingSensors: parsed.floodingSensors || [],
                                    isLoading: parsed.type !== 'complete',
                                    isComplete: parsed.type === 'complete',
                                    checked: parsed.checked || 0,
                                    totalToCheck: parsed.totalToCheck || 0,
                                    activeSensors: parsed.activeSensors || 0,
                                });
                            } catch {
                                // Ignore parse errors
                            }
                        }
                    }
                }
            } catch (e) {
                console.error("Flooding stream error", e);
                setData(prev => ({ ...prev, isLoading: false, isComplete: true }));
            }
        };

        fetchFloodingData();

        // Refresh every 5 minutes
        const interval = setInterval(fetchFloodingData, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <FloodingContext.Provider value={data}>
            {children}
        </FloodingContext.Provider>
    );
}
