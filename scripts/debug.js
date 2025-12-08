
const { createClient } = require('@supabase/supabase-js');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function check() {
    const { data, error } = await supabase
        .from('call_logs')
        .select('id, recording_url, created_at')
        .order('created_at', { ascending: false })
        .limit(5);

    if (error) {
        console.error('Supabase Error:', error);
    } else {
        console.log(JSON.stringify(data, null, 2));
    }
}

check();
