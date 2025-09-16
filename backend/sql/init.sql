-- Initialize database schema for Automated BI Dashboard

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum for processing status
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'processingstatus') THEN
        CREATE TYPE processingstatus AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');
    END IF;
END
$$;

-- Create dataset_analysis table
CREATE TABLE IF NOT EXISTS dataset_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Processing status
    status processingstatus DEFAULT 'PENDING' NOT NULL,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT,
    
    -- Data analysis results
    domain_classification VARCHAR(100),
    confidence_score FLOAT,
    row_count INTEGER,
    column_count INTEGER,
    
    -- Store analysis metadata as JSONB
    data_quality_report JSONB,
    column_analysis JSONB,
    domain_insights JSONB,
    recommended_kpis JSONB,
    recommended_charts JSONB,
    dashboard_structure JSONB
);

-- Create data_points table
CREATE TABLE IF NOT EXISTS data_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES dataset_analysis(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    data JSONB NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_dataset_analysis_status ON dataset_analysis(status);
CREATE INDEX IF NOT EXISTS idx_dataset_analysis_upload_timestamp ON dataset_analysis(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_dataset_analysis_domain ON dataset_analysis(domain_classification);
CREATE INDEX IF NOT EXISTS idx_data_points_dataset_row ON data_points(dataset_id, row_index);
CREATE INDEX IF NOT EXISTS idx_data_points_dataset ON data_points(dataset_id);

-- Create function to automatically clean up old files
CREATE OR REPLACE FUNCTION cleanup_old_datasets()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Delete datasets older than 30 days
    DELETE FROM dataset_analysis 
    WHERE upload_timestamp < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get dataset statistics
CREATE OR REPLACE FUNCTION get_dataset_stats()
RETURNS TABLE(
    total_datasets BIGINT,
    completed_datasets BIGINT,
    processing_datasets BIGINT,
    failed_datasets BIGINT,
    avg_processing_time INTERVAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_datasets,
        COUNT(*) FILTER (WHERE status = 'completed') as completed_datasets,
        COUNT(*) FILTER (WHERE status = 'processing') as processing_datasets,
        COUNT(*) FILTER (WHERE status = 'failed') as failed_datasets,
        AVG(processing_completed_at - processing_started_at) FILTER (WHERE status = 'completed') as avg_processing_time
    FROM dataset_analysis;
END;
$$ LANGUAGE plpgsql;
