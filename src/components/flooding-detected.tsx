'use client';

import { motion } from 'framer-motion';
import { Waves, AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useFlooding } from '@/contexts/flooding-context';

export function FloodingDetected({ className }: { className?: string }) {
    const {
        floodingCount,
        activeSensors,
        isLoading,
        isComplete,
        checked,
        totalToCheck
    } = useFlooding();

    const hasFlooding = floodingCount > 0;
    const progress = totalToCheck > 0 ? (checked / totalToCheck) * 100 : 0;

    // Color states
    const getBorderColor = () => {
        if (!isComplete) return 'border-blue-500/30';
        return hasFlooding ? 'border-red-500/30' : 'border-emerald-500/30';
    };

    const getIconBgColor = () => {
        if (!isComplete) return 'bg-blue-500/10';
        return hasFlooding ? 'bg-red-500/10' : 'bg-emerald-500/10';
    };

    const getIconColor = () => {
        if (!isComplete) return 'text-blue-400';
        return hasFlooding ? 'text-red-500 animate-pulse' : 'text-emerald-400';
    };

    const getCountColor = () => {
        if (!isComplete) return 'text-blue-400';
        return hasFlooding ? 'text-red-500' : 'text-emerald-400';
    };

    return (
        <motion.div
            className={cn(
                "glass-panel p-4 rounded-xl border transition-all duration-500 min-h-[140px]",
                getBorderColor(),
                className
            )}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
        >
            <div className="flex items-center justify-between mb-3">
                <h3 className={cn(
                    "text-sm font-semibold transition-colors",
                    hasFlooding && isComplete ? "text-red-400" : "text-blue-400"
                )}>
                    Flooding Detected
                </h3>
                <div className={cn(
                    "p-1.5 rounded-lg transition-colors",
                    isLoading ? "animate-spin" : ""
                )}>
                    <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
                </div>
            </div>

            <div className="flex items-center gap-4">
                <motion.div
                    className={cn("text-4xl font-bold transition-colors", getCountColor())}
                    key={floodingCount}
                    initial={{ scale: 1.2, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.3 }}
                >
                    {floodingCount}
                </motion.div>

                <div className={cn("p-2 rounded-lg transition-colors", getIconBgColor())}>
                    <Waves className={cn(
                        "w-6 h-6",
                        hasFlooding ? "text-red-500" : isComplete ? "text-emerald-400" : "text-blue-400"
                    )} />
                </div>
            </div>

            <div className="mt-3">
                <div className="text-xs text-slate-400">
                    {isComplete
                        ? `of ${activeSensors} sensors checked`
                        : `Checking... ${checked}/${totalToCheck}`
                    }
                </div>

                {/* Progress bar while loading */}
                {!isComplete && totalToCheck > 0 && (
                    <div className="mt-2 w-full h-1 bg-slate-700 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-blue-500 transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                )}
            </div>
        </motion.div>
    );
}
