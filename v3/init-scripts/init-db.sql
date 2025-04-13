-- Function to check if a table exists
CREATE OR REPLACE FUNCTION table_exists(tbl text) RETURNS boolean AS
$$
DECLARE
    exists boolean;
BEGIN
    SELECT COUNT(*) > 0 INTO exists
    FROM information_schema.tables
    WHERE table_name = tbl;
    RETURN exists;
END;
$$ LANGUAGE plpgsql;

-- Only attempt inserts if tables exist
DO $$
BEGIN
    -- Skip this script entirely - let the Flask application handle initialization
    RAISE NOTICE 'Skipping initial data insertion - tables will be created by the application';
END
$$;