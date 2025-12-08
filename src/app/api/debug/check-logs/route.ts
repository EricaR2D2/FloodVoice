import { NextResponse } from 'next/server';

export async function GET() {
    try {
        const callId = "bef62f8a-c6ac-4467-b758-23779b45db06"; // Known valid ID

        console.log("Debug: Triggering analysis for", callId);

        const response = await fetch('http://localhost:3000/api/analyze-call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ callId })
        });

        const data = await response.json();

        return NextResponse.json({
            test_target: callId,
            status: response.status,
            result: data
        });
    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
