CREATE TABLE IF NOT EXISTS research_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id TEXT UNIQUE NOT NULL,
    company TEXT NOT NULL,
    ticker TEXT NOT NULL,
    status TEXT NOT NULL,
    result_json JSONB,
    canonical_evidence_json JSONB,
    consistency_json JSONB,
    evaluation_json JSONB,
    timings_json JSONB,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_research_jobs_created_at ON research_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_jobs_ticker ON research_jobs(ticker);
CREATE INDEX IF NOT EXISTS idx_research_jobs_status ON research_jobs(status);
