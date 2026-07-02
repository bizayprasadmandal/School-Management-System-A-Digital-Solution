-- PostgreSQL initialization for School Management System
-- Runs once when the container is first created

-- ─── Extensions ──────────────────────────────────────────────────────────────

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "unaccent";       -- For accent-insensitive search
CREATE EXTENSION IF NOT EXISTS "btree_gist";     -- For exclusion constraints

-- ─── Text search configuration ────────────────────────────────────────────────

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_ts_config WHERE cfgname = 'sms_search') THEN
        CREATE TEXT SEARCH CONFIGURATION sms_search (COPY = english);
    END IF;
END
$$;
ALTER TEXT SEARCH CONFIGURATION sms_search
    ALTER MAPPING FOR hword, hword_part, word
    WITH unaccent, english_stem;

-- ─── Full-text search indexes (applied after Django migrations) ───────────────
-- These are created as suggestions; actual indexes are managed by Django

-- Example: Full-text search on student names
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_fulltext
--     ON users USING gin(to_tsvector('english', first_name || ' ' || last_name));

-- ─── Audit log partitioning (by month) ───────────────────────────────────────
-- This is managed by Django + PostgreSQL native partitioning for large deployments

-- ─── Performance settings (overrides for containerized PostgreSQL) ────────────
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '768MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = '0.9';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = '100';
ALTER SYSTEM SET random_page_cost = '1.1';
ALTER SYSTEM SET effective_io_concurrency = '200';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET max_connections = '200';

SELECT pg_reload_conf();

-- ─── Read-only replica user ───────────────────────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'sms_readonly') THEN
        CREATE ROLE sms_readonly WITH LOGIN PASSWORD 'sms_readonly_password';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE sms_db TO sms_readonly;
GRANT USAGE ON SCHEMA public TO sms_readonly;
-- Tables granted after Django migrations run:
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO sms_readonly;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO sms_readonly;
