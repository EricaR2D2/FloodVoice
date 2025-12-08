import { GoogleGenerativeAI } from "@google/generative-ai";

const API_KEY = process.env.GOOGLE_GENERATIVE_AI_API_KEY;
const genAI = new GoogleGenerativeAI(API_KEY || "");

// Fixed Taxonomy for Aggregation
const VALID_TAGS = [
    "Medical",
    "Food/Water",
    "Power",
    "Evacuation",
    "Mental Health",
    "Property Damage",
    "Safe"
];

// Interface for Structured Output
export interface CallAnalysis {
    tags: string[];
    sentiment_score: number;
    key_topics: string;
}

export async function analyzeTranscript(transcript: string): Promise<CallAnalysis | null> {
    if (!API_KEY) {
        console.error("Gemini API Key missing");
        return null;
    }

    // Model fallback chain - each has separate quota
    // Using lite variants as they have separate quota pools
    const MODELS = [
        "gemini-2.5-flash-lite",   // Ultra fast, separate quota
        "gemini-2.5-flash",        // Fast and intelligent
        "gemini-2.0-flash-lite",   // Previous gen lite
        "gemini-2.0-flash"         // Previous gen workhorse
    ];

    const prompt = `
      You are an emergency response AI. Analyze this transcript for a liaison dashboard.
      
      TRANSCRIPT:
      "${transcript}"

      RULES:
      1. SCORING (1-10):
         - 1-3: Calm, informational, safe.
         - 4-6: Concerned, anxious, mild needs.
         - 7-8: Distressed, urgent needs, crying.
         - 9-10: Panic, life-threatening, screaming.
      
      2. TAGGING:
         - Select strictly from: ${JSON.stringify(VALID_TAGS)}
         - If uncertain, default to "Safe".
      
      3. KEY TOPICS:
         - Write a 1-sentence summary (max 15 words) focusing on NEEDS.
      
      OUTPUT JSON FORMAT:
      {
        "tags": ["Tag1", "Tag2"],
        "sentiment_score": number, 
        "key_topics": "Summary string here"
      }
    `;

    let lastError: any = null;

    for (const modelName of MODELS) {
        try {
            console.log(`Trying model: ${modelName}`);
            const model = genAI.getGenerativeModel({
                model: modelName,
                generationConfig: { responseMimeType: "application/json" }
            });

            const result = await model.generateContent(prompt);
            const text = result.response.text();

            // Parse JSON safely
            const data = JSON.parse(text) as CallAnalysis;
            console.log(`Success with model: ${modelName}`);
            return data;

        } catch (error: any) {
            console.error(`Model ${modelName} failed:`, error.message || error);
            lastError = error;

            // If it's a rate limit error (429), try next model
            if (error.message?.includes('429') || error.message?.includes('quota')) {
                console.log(`Rate limited on ${modelName}, trying next model...`);
                continue;
            }

            // For other errors, throw immediately
            throw new Error(`Gemini Error: ${error.message || error}`);
        }
    }

    // All models exhausted
    throw new Error(`All Gemini models rate limited. Please try again later. Last error: ${lastError?.message || lastError}`);
}

