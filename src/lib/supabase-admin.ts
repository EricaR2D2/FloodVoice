import { createClient } from '@supabase/supabase-js'

/**
 * Server-side Supabase client that uses the SERVICE_ROLE key.
 * This bypasses Row Level Security (RLS) and should ONLY be used 
 * in server-side code (API routes, webhooks, etc.)
 * 
 * NEVER expose this client to the browser/client-side code!
 */

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || ''

if (!supabaseServiceKey) {
    console.warn('SUPABASE_SERVICE_ROLE_KEY is not set - server operations may fail due to RLS')
}

export const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey, {
    auth: {
        autoRefreshToken: false,
        persistSession: false
    }
})
