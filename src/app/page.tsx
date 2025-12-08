'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Waves, ArrowRight } from 'lucide-react';
import BlurText from '@/components/ui/BlurText';

export default function LandingPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    setIsLoading(true);
    // TODO: Add real Supabase Auth here
    // For MVP demo, simulate login delay then push to dashboard
    setTimeout(() => {
      router.push('/dashboard');
    }, 1000);
  };

  return (
    <main className="min-h-screen relative flex flex-col items-center justify-center p-6 overflow-hidden">
      {/* Background Gradient Orbs */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-blue-900/40 blur-[100px]" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-900/30 blur-[100px]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="z-10 text-center max-w-3xl space-y-8"
      >
        {/* Hero Icon */}
        <div className="mx-auto w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-2xl shadow-blue-500/20">
          <Waves className="w-10 h-10 text-white" />
        </div>

        {/* Hero Text */}
        <div className="space-y-4">
          <div className="flex justify-center items-baseline">
            <BlurText
              text="Flood"
              delay={80}
              animateBy="letters"
              direction="top"
              className="text-5xl md:text-7xl font-bold tracking-tight text-white"
            />
            <BlurText
              text="Voice."
              delay={80}
              animateBy="letters"
              direction="top"
              startDelay={400}
              className="text-5xl md:text-7xl font-bold tracking-tight text-cyan-400"
            />
          </div>
          <p className="text-xl text-slate-400 max-w-xl mx-auto leading-relaxed">
            The minimal-latency triage platform for community flood response.
            <br />
            <span className="text-slate-500 text-sm">Automated Voice Checks • Real-time FloodNet Data • Instant Alerts</span>
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-8">
          {[
            { label: "Response Time", value: "< 2 min" },
            { label: "Active Sensors", value: "85+" },
            { label: "Voice API", value: "Ready" },
          ].map((stat, i) => (
            <div key={i} className="glass-panel p-4 rounded-xl border border-white/5">
              <div className="text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-sm text-slate-500">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="pt-8">
          <button
            onClick={handleLogin}
            disabled={isLoading}
            className="group relative inline-flex items-center gap-3 px-8 py-4 bg-white text-slate-900 rounded-full font-bold text-lg hover:bg-blue-50 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Accessing Command Center...' : 'Launch Dashboard'}
            {!isLoading && <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />}

            {/* Glow Effect */}
            <div className="absolute inset-0 rounded-full ring-2 ring-white/50 blur-md opacity-50 group-hover:opacity-100 transition-opacity" />
          </button>
        </div>
      </motion.div>
    </main>
  );
}
