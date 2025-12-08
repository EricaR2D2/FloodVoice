# FloodVoice 🌊🗣️

**FloodVoice** is an AI-powered emergency response platform that transforms qualitative voice data into actionable intelligence for flood response teams. It bridges the gap between residents in distress and community liaisons by converting messy phone calls into structured data.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-Phase%206.5-success.svg)

---

## 🚀 Key Features

### 1. Narrative to Numbers Analytics
We replace binary "Yes/No" inputs with rich sentiment analysis. By analyzing voice content, we extract:
- **Urgency Scores (1-10)**: Automatically prioritizes residents based on distress levels.
- **Visual Priority Queue**: Top 10 critical residents needing immediate attention.
- **Tag Distribution**: Real-time breakdown of concerns (Medical, Evacuation, Power, etc.).
- **4-Week Trends**: AI-generated insights on historical sentiment patterns.

### 2. Role-Based Dashboards
- **Command Center (`/dashboard`)**: High-level view for Directors/Coordinators. Features aggregated analytics, FloodNet sensor maps, and urgency distribution.
- **Live Calls (`/dashboard/calls`)**: Focused real-time feed for Liaisons. Shows incoming transcripts, AI analysis, and allows for immediate callback.

### 3. Real-Time Flood Intelligence
- **FloodNet Integration**: Live sensor data showing street-level flood depth.
- **Automated Triage**: Residents are automatically categorized (Critical, Elevated, Moderate, Safe).

---

## 🛠️ Tech Stack

- **Framework**: [Next.js 14](https://nextjs.org/) (App Router, React 18)
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL + Realtime)
- **Styling**: Tailwind CSS + `framer-motion` for animations
- **AI/LLM**: Google Gemini (via Vapi) for sentiment analysis and tagging
- **Voice**: Vapi for conversational AI agents
- **Icons**: Lucide React

---

## 🚦 Getting Started

### Prerequisites
- Node.js 18+
- Supabase project
- Vapi account

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/flood-voice.git
   cd flood-voice
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Setup**
   Create a `.env.local` file with the following keys:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   VAPI_PRIVATE_KEY=your_vapi_private_key
   NEXT_PUBLIC_VAPI_PUBLIC_KEY=your_vapi_public_key
   GEMINI_API_KEY=your_gemini_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

4. **Run Development Server**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) to view the app.

---

## 📂 Project Structure

```
src/
├── app/
│   ├── api/            # Next.js API Routes (Analytics, Vapi, Cron)
│   ├── dashboard/      # Main Dashboard Interfaces
│   │   ├── calls/      # Liaison Live Feed
│   │   ├── layout.tsx  # Sidebar & Layout
│   │   └── page.tsx    # Director Command Center
│   └── page.tsx        # Landing Page
├── components/
│   ├── analytics/      # Charts & Data Widgets
│   ├── floodnet-graph/ # Sensor Data Visualization
│   └── ui/             # Reusable UI Components
└── lib/                # Utilities & Supabase Client
```

---

## 🔮 Future Roadmap (Phase 7)

- **Organization Support**: Multi-tenant architecture for different CBOs.
- **Role-Based Access Control**: Strict data separation between Liaisons and Coordinators.
- **Coordinator Dashboard**: Cross-liaison aggregated views.
