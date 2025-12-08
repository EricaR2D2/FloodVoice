-- Reset Schema (Warning: Deletes all data)
drop table if exists public.call_logs cascade;
drop table if exists public.residents cascade;
drop table if exists public.profiles cascade;

-- Create Profiles table (extends Auth)
create table public.profiles (
  id uuid references auth.users not null primary key,
  email text,
  org_name text,
  telegram_chat_id text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create Residents table
create table public.residents (
  id uuid default gen_random_uuid() primary key,
  liaison_id uuid not null, -- Removed FK constraint for easier MVP testing if profiles don't expect
  name text not null,
  phone_number text not null,
  age integer,
  address text,
  health_conditions text,
  zip_code text,
  language text default 'en',
  status text check (status in ('safe', 'distress', 'unresponsive', 'pending')) default 'pending',
  vapi_assistant_id text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create Logs table
create table public.call_logs (
  id uuid default gen_random_uuid() primary key,
  resident_id uuid references public.residents(id) on delete cascade not null,
  vapi_call_id text,
  summary text,
  risk_label text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS
alter table public.profiles enable row level security;
alter table public.residents enable row level security;
alter table public.call_logs enable row level security;

-- Policies (MVP: Allow public access for testing to avoid "Violates RLS" error)
-- In production, replace 'true' with 'auth.uid() = liaison_id'
create policy "MVP Public View" on public.residents for select using (true);
create policy "MVP Public Insert" on public.residents for insert with check (true);
create policy "MVP Public Update" on public.residents for update using (true);

create policy "MVP Public View Logs" on public.call_logs for select using (true);
create policy "MVP Public Insert Logs" on public.call_logs for insert with check (true);
