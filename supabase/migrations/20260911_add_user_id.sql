-- Add user_id to research_jobs and link to Supabase Auth user
ALTER TABLE research_jobs ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- Enable Row Level Security (RLS)
ALTER TABLE research_jobs ENABLE ROW LEVEL SECURITY;

-- Note: The Python backend uses the Service Role key which bypasses RLS.
-- This RLS policy adds defense in depth in case the API is ever exposed or
-- if frontend clients are allowed direct Supabase access in the future.

-- Policy: Users can read their own jobs
CREATE POLICY "Users can view own jobs"
ON research_jobs FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can insert their own jobs
CREATE POLICY "Users can create own jobs"
ON research_jobs FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own jobs
CREATE POLICY "Users can update own jobs"
ON research_jobs FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
