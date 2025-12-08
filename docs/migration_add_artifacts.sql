-- Migration: Add Artifact Columns to call_logs
-- Run this in your Supabase SQL Editor

ALTER TABLE public.call_logs 
ADD COLUMN IF NOT EXISTS recording_url text,
ADD COLUMN IF NOT EXISTS transcript text;
