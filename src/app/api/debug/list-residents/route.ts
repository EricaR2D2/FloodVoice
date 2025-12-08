import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

/**
 * GET /api/debug/list-residents
 * Lists all residents for testing purposes
 */
export async function GET() {
    try {
        const { data: residents, error } = await supabase
            .from('residents')
            .select('id, name, status')
            .limit(10);

        if (error) {
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json({
            count: residents?.length || 0,
            residents
        });
    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
