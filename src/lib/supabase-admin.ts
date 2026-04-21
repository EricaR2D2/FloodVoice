import { createClient } from '@supabase/supabase-js'

/**
 * Server-side Supabase client that uses the SERVICE_ROLE key.
 * Falls back gracefully so the build never crashes when the key is absent.
 * In that case, server routes operate under RLS restrictions.
 */

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co'

// Use service role key if present, otherwise fall back so createClient never throws.
const supabaseServiceKey =
    process.env.SUPABASE_SERVICE_ROLE_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
    'demo-build-placeholder'

export const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey, {
    auth: {
        autoRefreshToken: false,
        persistSession: false
    }
})
