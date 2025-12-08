-- Add qualitative analysis columns to call_logs table

ALTER TABLE call_logs
ADD COLUMN IF NOT EXISTS tags text[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS sentiment_score integer, -- 1-10
ADD COLUMN IF NOT EXISTS key_topics text,
ADD COLUMN IF NOT EXISTS processed_at timestamptz;

-- Add checking constraint for sentiment score
ALTER TABLE call_logs
ADD CONSTRAINT check_sentiment_score CHECK (sentiment_score >= 1 AND sentiment_score <= 10);
