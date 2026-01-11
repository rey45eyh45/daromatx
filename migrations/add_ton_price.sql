-- Migration: Add ton_price column to courses table
-- Date: 2026-01-11
-- Description: Admin paneldan TON narxini belgilash imkoniyati

-- Add ton_price column with default value 0
ALTER TABLE courses ADD COLUMN IF NOT EXISTS ton_price FLOAT DEFAULT 0;

-- Update existing courses to have ton_price = 0 (they will use auto-calculated price)
UPDATE courses SET ton_price = 0 WHERE ton_price IS NULL;
