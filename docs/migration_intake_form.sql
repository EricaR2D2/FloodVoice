-- ============================================================
-- FloodVoice — Intake Form Migration
-- Run this in your Supabase SQL editor (Database → SQL Editor)
-- All columns are nullable so existing resident records are unaffected
-- ============================================================

ALTER TABLE residents
  -- Section 1: Personal Information
  ADD COLUMN IF NOT EXISTS date_of_birth      DATE,
  ADD COLUMN IF NOT EXISTS alternate_phone    TEXT,
  ADD COLUMN IF NOT EXISTS email              TEXT,

  -- Section 2: Household & Housing
  ADD COLUMN IF NOT EXISTS floor_apt          TEXT,
  ADD COLUMN IF NOT EXISTS basement_apartment BOOLEAN,
  ADD COLUMN IF NOT EXISTS household_size     INTEGER,

  -- Section 3: Emergency Contact (Next of Kin)
  ADD COLUMN IF NOT EXISTS next_of_kin_name         TEXT,
  ADD COLUMN IF NOT EXISTS next_of_kin_phone        TEXT,
  ADD COLUMN IF NOT EXISTS next_of_kin_relationship TEXT,
  ADD COLUMN IF NOT EXISTS next_of_kin_address      TEXT,

  -- Section 4: Health & Access Needs
  ADD COLUMN IF NOT EXISTS has_disability          BOOLEAN,
  ADD COLUMN IF NOT EXISTS disability_description  TEXT,

  -- Section 5: Contact Preferences
  ADD COLUMN IF NOT EXISTS preferred_languages  TEXT,   -- comma-separated e.g. "English,Bengali"
  ADD COLUMN IF NOT EXISTS contact_method       TEXT,   -- 'call' | 'sms' | 'both'
  ADD COLUMN IF NOT EXISTS best_time_to_reach   TEXT,   -- 'morning' | 'afternoon' | 'evening' | 'anytime'

  -- Section 6: Consent
  ADD COLUMN IF NOT EXISTS consent_signature  TEXT,
  ADD COLUMN IF NOT EXISTS consent_date       DATE,

  -- Liaison Use Only
  ADD COLUMN IF NOT EXISTS liaison_name       TEXT,
  ADD COLUMN IF NOT EXISTS liaison_org        TEXT,
  ADD COLUMN IF NOT EXISTS registration_date  DATE,
  ADD COLUMN IF NOT EXISTS neighborhood       TEXT,
  ADD COLUMN IF NOT EXISTS form_id            TEXT;
