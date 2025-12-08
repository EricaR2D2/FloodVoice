'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Users, Activity, Settings, LogOut, Phone } from 'lucide-react';
import { cn } from '@/lib/utils'; // Assuming you have this utility or use simple string concat
import { FloodingProvider } from '@/contexts/flooding-context';

export default function DashboardLayout({ children }: { children: ReactNode }) {
    const pathname = usePathname();

    const navItems = [
        { name: 'Command Center', href: '/dashboard', icon: LayoutDashboard },
        { name: 'Live Calls', href: '/dashboard/calls', icon: Phone },
        { name: 'Residents Pod', href: '/dashboard/residents', icon: Users },
        { name: 'FloodNet Map', href: '/dashboard/map', icon: Activity },
        { name: 'Settings', href: '/dashboard/settings', icon: Settings },
    ];

    return (
        <FloodingProvider>
            <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] flex">
                {/* Sidebar - Glassmorphism */}
                <aside className="w-64 fixed h-full glass-panel border-r border-white/5 z-50 flex flex-col">
                    {/* Logo */}
                    <div className="p-6 border-b border-white/5">
                        <h2 className="text-2xl font-bold tracking-tighter">
                            Flood<span className="text-blue-400">Voice</span>
                        </h2>
                    </div>

                    {/* Nav Links */}
                    <nav className="flex-1 p-4 space-y-2">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = pathname === item.href;

                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all",
                                        isActive
                                            ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                                            : "text-slate-400 hover:text-white hover:bg-white/5"
                                    )}
                                >
                                    <Icon className="w-5 h-5" />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User Profile / Logout */}
                    <div className="p-4 border-t border-white/5">
                        <button className="flex items-center gap-3 w-full px-4 py-3 text-sm text-slate-400 hover:text-red-400 transition-colors">
                            <LogOut className="w-5 h-5" />
                            Sign Out
                        </button>
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="flex-1 ml-64 p-8 relative">
                    {/* ambient background glow */}
                    <div className="absolute top-0 left-0 w-full h-[300px] bg-gradient-to-b from-blue-900/10 to-transparent pointer-events-none" />

                    <div className="relative z-10 max-w-6xl mx-auto">
                        {children}
                    </div>
                </main>
            </div>
        </FloodingProvider>
    );
}
