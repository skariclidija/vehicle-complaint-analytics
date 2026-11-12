-- PostgreSQL schema for NHTSA vehicle complaint data

CREATE TABLE IF NOT EXISTS vehicle_complaints (
    id BIGSERIAL PRIMARY KEY,
    odi_number TEXT NOT NULL UNIQUE,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    model_year INTEGER,
    component TEXT,
    date_filed TEXT,
    summary TEXT,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_complaints_make_model_year
    ON vehicle_complaints(make, model, model_year);
