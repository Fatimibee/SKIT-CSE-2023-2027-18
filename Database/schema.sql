-- schema.sql
-- Database Schema for Yojana Sahayak (PostgreSQL)

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    age INT CHECK (age >= 0 AND age <= 120),
    gender VARCHAR(20),
    category VARCHAR(50),
    occupation VARCHAR(100),
    state VARCHAR(100),
    annual_income NUMERIC(12, 2),
    education VARCHAR(100),
    disability VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. SCHEMES TABLE (35-column dataset mapping)
CREATE TABLE IF NOT EXISTS schemes (
    scheme_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    ministry VARCHAR(255),
    scheme_category TEXT,
    description TEXT,
    beneficiary_state VARCHAR(100),
    npi_ministry VARCHAR(255),
    tags TEXT,
    typename VARCHAR(50),
    categories_normalized TEXT,
    tags_normalized TEXT,
    
    -- Content fields
    eligibility TEXT,
    beneficiaries TEXT,
    benefits TEXT,
    documents_required TEXT,
    application_process TEXT,
    application_mode VARCHAR(50),
    state VARCHAR(100),
    department VARCHAR(255),
    
    -- Raw fields
    eligibility_raw TEXT,
    beneficiaries_raw TEXT,
    benefits_raw TEXT,
    documents_required_raw TEXT,
    
    -- Structured eligibility fields
    age_min INT,
    age_max INT,
    gender VARCHAR(20),
    income_max NUMERIC(12, 2),
    category VARCHAR(50),
    occupation VARCHAR(100),
    eligibility_state VARCHAR(100),
    education VARCHAR(100),
    disability VARCHAR(50),
    
    -- Provenance
    source_url TEXT,
    official_url TEXT,
    last_updated VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. RECOMMENDATION HISTORY TABLE
CREATE TABLE IF NOT EXISTS recommendation_history (
    recommendation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    scheme_id INT REFERENCES schemes(scheme_id) ON DELETE CASCADE,
    score NUMERIC(5, 2),
    matched_criteria JSONB,
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. DATA INGESTION RUNS TABLE
CREATE TABLE IF NOT EXISTS data_ingestion_runs (
    run_id SERIAL PRIMARY KEY,
    run_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_file VARCHAR(255),
    records_read INT DEFAULT 0,
    records_inserted INT DEFAULT 0,
    records_updated INT DEFAULT 0,
    records_rejected INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS'
);

-- INDEXES FOR FAST QUERY PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_schemes_slug ON schemes(slug);
CREATE INDEX IF NOT EXISTS idx_schemes_state ON schemes(eligibility_state);
CREATE INDEX IF NOT EXISTS idx_schemes_age ON schemes(age_min, age_max);
CREATE INDEX IF NOT EXISTS idx_schemes_income ON schemes(income_max);
CREATE INDEX IF NOT EXISTS idx_schemes_gender ON schemes(gender);
CREATE INDEX IF NOT EXISTS idx_schemes_category ON schemes(category);
CREATE INDEX IF NOT EXISTS idx_schemes_occupation ON schemes(occupation);
CREATE INDEX IF NOT EXISTS idx_schemes_education ON schemes(education);
CREATE INDEX IF NOT EXISTS idx_schemes_disability ON schemes(disability);
