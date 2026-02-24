-- Migration script for Supabase (PostgreSQL)

-- Create expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    item TEXT NOT NULL,
    category TEXT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    paid_by TEXT NOT NULL,
    notes TEXT,
    recurrence_frequency TEXT,
    recurrence_next_due DATE,
    recurrence_active INTEGER DEFAULT 0
);

-- Create income table
CREATE TABLE IF NOT EXISTS income (
    id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    source TEXT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    notes TEXT
);

-- Create category_budgets table
CREATE TABLE IF NOT EXISTS category_budgets (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL UNIQUE,
    group_name TEXT NOT NULL,
    limit_amount DECIMAL(12, 2) NOT NULL,
    icon TEXT
);

-- Create settings table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Create budget_month table
CREATE TABLE IF NOT EXISTS budget_month (
    month TEXT PRIMARY KEY,
    limit_amount DECIMAL(12, 2) DEFAULT 0
);

-- Insert default category budgets
INSERT INTO category_budgets (category, group_name, limit_amount, icon) 
VALUES 
    ('Monthly Rent', 'HOUSING', 15000, '🏠'),
    ('Service Charge / Maintenance', 'HOUSING', 3000, '🛠️'),
    ('Electricity / Gas / Water', 'HOUSING', 3000, '⚡'),
    ('Sinking Fund (Building Repair)', 'HOUSING', 1000, '🏗️'),
    ('Office Commute (Hadi)', 'TRANSPORT', 3000, '🚌'),
    ('Office Commute (Ruhi)', 'TRANSPORT', 3000, '🚗'),
    ('Daughter''s School Transport', 'TRANSPORT', 3000, '🚌'),
    ('Car Maintenance / Driver', 'TRANSPORT', 5000, '🔧'),
    ('Hadi', 'PERSONAL', 2000, '👤'),
    ('Hadi (Personal Hangout, Cosmetics)', 'PERSONAL', 3000, '👨'),
    ('Ruhi (Cream, Accessories, Skincare)', 'PERSONAL', 3000, '👩'),
    ('Yusra (Diapers, Wipes, Baby Care)', 'PERSONAL', 5000, '👶'),
    ('Groceries & Food', 'LIVING', 10000, '🛒'),
    ('Household Help (Maid/Cook)', 'LIVING', 4000, '🧹'),
    ('Internet / Phone / Subscriptions', 'LIVING', 2000, '📶'),
    ('Family Hangout', 'LIVING', 4000, '🎉'),
    ('Other', 'OTHERS', 2000, '📦')
ON CONFLICT (category) DO NOTHING;
