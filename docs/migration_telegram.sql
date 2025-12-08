-- Add telegram_chat_id to profiles table
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS telegram_chat_id bigint;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_telegram_chat_id ON profiles(telegram_chat_id);
