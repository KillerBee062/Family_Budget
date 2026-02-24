-- ADDITIONAL DATA IMPORT (Feb 14 - Feb 24)

INSERT INTO expenses (id, date, item, category, amount, paid_by, notes)
VALUES 
-- Feb 14-16 (from Image 1)
(gen_random_uuid(), '2026-02-14', 'Ticket', 'Office Commute (Hadi)', 1500, 'Hadi', ''),
(gen_random_uuid(), '2026-02-14', 'Hadis dress iron', 'Hadi', 150, 'Hadi', ''),
(gen_random_uuid(), '2026-02-14', 'Hadis pant', 'Hadi', 4816, 'Hadi', ''),
(gen_random_uuid(), '2026-02-14', 'Transport', 'Office Commute (Hadi)', 210, 'Hadi', ''),
(gen_random_uuid(), '2026-02-14', 'Transport', 'Office Commute (Hadi)', 240, 'Hadi', ''),
(gen_random_uuid(), '2026-02-14', 'Laptop charger', 'Other', 2500, 'Hadi', ''),
(gen_random_uuid(), '2026-02-14', 'Bread', 'Groceries & Food', 50, 'Hadi', ''),
(gen_random_uuid(), '2026-02-14', 'Parcel ordhek', 'Other', 100, 'Hadi', ''),

-- Feb 18 (from Images)
(gen_random_uuid(), '2026-02-18', 'Earpods', 'Other', 24000, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Chukur wet wipes chocolate', 'Yusra (Diapers, Wipes, Baby Care)', 700, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Tika', 'Other', 1519, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Tika', 'Other', 983, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Gari vara', 'Office Commute (Hadi)', 1000, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Lipus cost - lunch', 'Groceries & Food', 1050, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Transport', 'Office Commute (Hadi)', 240, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Plumber', 'Service Charge / Maintenance', 200, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Bua', 'Household Help (Maid/Cook)', 300, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Milk powder', 'Groceries & Food', 180, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Unimart: kola, daul, alu, piaj, soyabin tel', 'Groceries & Food', 1246, 'Hadi', ''),
(gen_random_uuid(), '2026-02-18', 'Chaul, dal, oats, begun, lebu', 'Groceries & Food', 1082, 'Hadi', ''),

-- Feb 19 (from Images)
(gen_random_uuid(), '2026-02-19', 'Dudh, beson, dhonepata, fulkopi', 'Groceries & Food', 350, 'Hadi', ''),
(gen_random_uuid(), '2026-02-19', 'Foodpanda iftar', 'Groceries & Food', 779, 'Hadi', ''),

-- Feb 20 (from Text)
(gen_random_uuid(), '2026-02-20', 'Uber vara', 'Office Commute (Hadi)', 3800, 'Hadi', ''),
(gen_random_uuid(), '2026-02-20', 'Bajar gazipur', 'Groceries & Food', 1550, 'Hadi', ''),

-- Feb 21 (from Text)
(gen_random_uuid(), '2026-02-21', 'Yusrar diaper', 'Yusra (Diapers, Wipes, Baby Care)', 2100, 'Hadi', ''),
(gen_random_uuid(), '2026-02-21', 'Chul dari', 'Hadi (Personal Hangout, Cosmetics)', 400, 'Hadi', ''),
(gen_random_uuid(), '2026-02-21', 'Vara', 'Office Commute (Hadi)', 100, 'Hadi', ''),

-- Feb 22 (from Text)
(gen_random_uuid(), '2026-02-22', 'Cng vara', 'Office Commute (Hadi)', 750, 'Hadi', ''),
(gen_random_uuid(), '2026-02-22', 'Locar (Hadi''s gym)', 'Hadi', 2500, 'Hadi', ''),
(gen_random_uuid(), '2026-02-22', 'Peaju, beguni', 'Groceries & Food', 70, 'Hadi', ''),

-- Feb 23 (from Text)
(gen_random_uuid(), '2026-02-23', 'Jilapi, kola', 'Groceries & Food', 300, 'Hadi', ''),
(gen_random_uuid(), '2026-02-23', 'Vara', 'Office Commute (Hadi)', 250, 'Hadi', ''),

-- Feb 24 (from Text)
(gen_random_uuid(), '2026-02-24', 'Vara', 'Office Commute (Hadi)', 230, 'Hadi', ''),
(gen_random_uuid(), '2026-02-24', 'Yusra', 'Yusra (Diapers, Wipes, Baby Care)', 1450, 'Hadi', ''),
(gen_random_uuid(), '2026-02-24', 'Biriyani mashla', 'Groceries & Food', 60, 'Hadi', ''),
(gen_random_uuid(), '2026-02-24', 'Chukur dress purpose (delivery in April)', 'Other', 1000, 'Hadi', '');
