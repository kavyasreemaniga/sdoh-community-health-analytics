-- Fix column lengths to accommodate Synthea data
-- Run this to update the schema

ALTER TABLE bronze.patients ALTER COLUMN state TYPE VARCHAR(50);
ALTER TABLE bronze.patients ALTER COLUMN marital_status TYPE VARCHAR(50);
ALTER TABLE bronze.patients ALTER COLUMN prefix TYPE VARCHAR(20);
ALTER TABLE bronze.patients ALTER COLUMN ssn TYPE VARCHAR(50);
ALTER TABLE bronze.patients ALTER COLUMN drivers TYPE VARCHAR(50);
ALTER TABLE bronze.patients ALTER COLUMN passport TYPE VARCHAR(50);

-- Also increase other potentially problematic columns
ALTER TABLE bronze.patients ALTER COLUMN zip TYPE VARCHAR(20);
ALTER TABLE bronze.patients ALTER COLUMN county TYPE VARCHAR(200);
ALTER TABLE bronze.patients ALTER COLUMN address TYPE VARCHAR(500);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Schema updated successfully!';
END $$;