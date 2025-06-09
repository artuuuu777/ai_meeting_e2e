-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create additional indexes for better performance
-- These will be created by Alembic migrations, but we set them up here for development

-- Note: Actual table creation will be handled by Alembic migrations