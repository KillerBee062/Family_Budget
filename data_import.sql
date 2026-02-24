-- DATA IMPORT FROM GOOGLE SHEETS JSON

-- 1. Import Expenses
INSERT INTO expenses (id, date, item, category, amount, paid_by, notes)
VALUES 
('262d5016-3efa-4647-aed9-a2bfcc05a8e1', '2026-02-01', 'Vegetables ', 'Electricity / Gas / Water', 180, 'Hadi', '1. Beet root 
2. Carrots 
3. Cucumber 
4. Tomatoes '),
('0dd8222e-6728-488f-b53c-08e906820cf0', '2026-02-01', 'Gym Rickshaw ', 'Electricity / Gas / Water', 50, 'Hadi', ''),
('e972f434-a7b5-4007-868a-f5449170733e', '2026-02-01', '1. Face wash 2. sunscreen 3. Moisturiser 4. Splendora 5. Hair Wax', 'Hadi', 3270, 'Hadi', ''),
('ee993877-50d5-412f-9d46-d3180f09d76e', '2026-02-05', 'Fruits', 'Family Hangout', 1500, 'Ruhi', ''),
('2579412a-5ddf-4201-a7da-55c5209d04d7', '2026-02-04', 'Hangout', 'Family Hangout', 155, 'Hadi', 'Fuchka ,shwapno'),
('440a15d3-d0ba-42b7-ba6e-f682f13e9a9a', '2026-02-05', 'Hangout', 'Family Hangout', 1050, 'Hadi', 'Breakfast, sweet,rickshaw vara'),
('ee2c86d3-33ff-4d6f-a75e-2088cdee07b2', '2026-02-08', 'Gym', 'Hadi', 8000, 'Hadi', ''),
('25dd0c95-f229-4f2c-bad0-572251d248cc', '2026-02-08', 'Bus', 'Hadi', 3000, 'Hadi', ''),
('6e8f8b0f-cc5d-4a49-bbaf-48ca47f2d262', '2026-02-08', 'Gazipur', 'Hadi', 2270, 'Hadi', ''),
('dcb54454-7099-4021-9204-8c02372bc9c7', '2026-02-08', 'Etc', 'Hadi', 3570, 'Hadi', '1. Shoes
2. Hair
3. Badam, chola'),
('9f31482b-1562-41c7-9d46-b0e5a5ee3f2f', '2026-02-08', 'Cash', 'Ruhi (Cream, Accessories, Skincare)', 6700, 'Hadi', 'Lotion'),
('93ca96fc-f92c-4e00-9f94-ef0a5a474dc7', '2026-02-08', 'Diaper', 'Yusra (Diapers, Wipes, Baby Care)', 5000, 'Ruhi', 'From : January '),
('b0728078-df22-429b-ac94-d80f3fff74a8', '2026-02-08', 'Return from Natore', 'Family Hangout', 1400, 'Hadi', ''),
('6629d948-ec48-48d2-8b3a-780638657909', '2026-02-08', 'Cod Lever oil', 'Hadi', 330, 'Hadi', ''),
('35d7dcc3-1561-4ea7-beb8-41d5048784e9', '2026-02-06', 'Fuchka', 'Family Hangout', 1000, 'Hadi', ''),
('4e17ffbb-697f-4e5a-94e5-332042c5e6ce', '2026-02-04', 'Hangouts ', 'Family Hangout', 500, 'Hadi', ''),
('0057c89a-a5c1-454f-a988-9e928684d616', '2026-02-04', 'Breakfast ', 'Family Hangout', 1000, 'Hadi', ''),
('d06e812d-d948-41ff-a08b-3030b245a673', '2026-02-04', 'Sami bhai’s', 'Hadi', 200, 'Hadi', ''),
('2d37f2cc-8ae8-4efb-99b4-1370884dc59e', '2026-02-04', 'House Rent', 'Monthly Rent', 22700, 'Hadi', ''),
('c8acfd48-b90e-4ae4-a3a1-f6a6d8e072e5', '2026-02-04', 'Bua', 'Household Help (Maid/Cook)', 4000, 'Hadi', ''),
('9f39427d-2f61-4072-a12f-9e464ac56ce2', '2026-02-04', 'Wifi', 'Internet / Phone / Subscriptions', 1000, 'Hadi', ''),
('a0f2936e-a5dc-4282-b38f-13e1423021e7', '2026-02-10', 'Office Commute', 'Hadi (Personal Hangout, Cosmetics)', 190, 'Hadi', ''),
('9f45004d-b656-4756-9001-0388c7cf12c5', '2026-02-10', 'Fast Food', 'Family Hangout', 900, 'Hadi', ''),
('e240b82c-19bd-409d-801a-88bce001e85a', '2026-02-12', 'Foodpanda', 'Groceries & Food', 4238, 'Hadi', ''),
('94da97d5-5094-4963-9cec-79b6bce73f88', '2026-02-12', 'Foodpanda', 'Groceries & Food', 4238, 'Hadi', 'Steak,toothpaste, biriyani masla,letus, bit lobon, chat masala,noodles,kabuli chola, yogurt,kacha marich, parsely, zukiniisabgula hask,'),
('bc4bc60f-afa0-470c-a1bb-e7ea9535ba88', '2026-02-12', 'Swapno', 'Groceries & Food', 3700, 'Hadi', 'Kola,komla,anar,tometo,lebu,betroot,motorsuti,brookli,loti,beef,egg,chukur pani,mistykumra,'),
('259b6108-de25-41af-9a37-69f9456cbb6b', '2026-02-12', 'Foodpanda', 'Groceries & Food', 765, 'Hadi', 'Burger,cold coffee'),
('9cb3fad4-6742-4b31-826b-15471f8cc696', '2026-02-13', 'Groceries ', 'Groceries & Food', 1100, 'Hadi', '1. Chal
2. Atta
3. Muri
4. Zero Cal
5. Sugar'),
('a5977fdc-c69e-4db1-a9de-c56accb52109', '2026-02-13', 'Groceries ', 'Groceries & Food', 1100, 'Hadi', '1. Chal
2. Atta
3. Muri
4. Zero Cal
5. Sugar'),
('6191073c-9af6-42e7-8abc-da2f3c08e114', '2026-02-13', 'Weight Scale', 'Other', 1500, 'Hadi', ''),
('adb87d84-aa44-4a6e-8b1e-873b6790c837', '2026-02-14', 'Ruhi''s parcel', 'Ruhi (Cream, Accessories, Skincare)', 1815, 'Ruhi', 'Micronil, streax'),
('24bccbce-6d90-4bae-823c-0b165e8473d5', '2026-02-14', 'Chap,muri ', 'Family Hangout', 1000, 'Hadi', '')
ON CONFLICT (id) DO NOTHING;

-- 2. Import Income
INSERT INTO income (id, date, source, amount, notes)
VALUES 
('98610e96-6420-4c2b-83aa-208e8008603e', '2026-02-08', 'Salary', 109000, '')
ON CONFLICT (id) DO NOTHING;

-- 3. Update Category Budgets
INSERT INTO category_budgets (category, group_name, limit_amount, icon)
VALUES 
('Electricity / Gas / Water', 'HOUSING', 3000, '⚡'),
('Monthly Rent', 'HOUSING', 17000, '🏠'),
('Service Charge / Maintenance', 'HOUSING', 3000, '🛠️'),
('Sinking Fund (Building Repair)', 'HOUSING', 1000, '📦'),
('Family Hangout', 'LIVING', 2000, '🎉'),
('Groceries & Food', 'LIVING', 10000, '�'),
('Household Help (Maid/Cook)', 'LIVING', 4000, '🧹'),
('Internet / Phone / Subscriptions', 'LIVING', 2000, '📦'),
('Other', 'OTHERS', 2000, '�'),
('Hadi', 'PERSONAL', 2000, '�'),
('Hadi (Personal Hangout, Cosmetics)', 'PERSONAL', 3000, '👨'),
('Ruhi (Cream, Accessories, Skincare)', 'PERSONAL', 10000, '👩'),
('Yusra (Diapers, Wipes, Baby Care)', 'PERSONAL', 12000, '👶'),
('Office Commute (Hadi)', 'TRANSPORT', 3000, '�'),
('Office Commute (Ruhi)', 'TRANSPORT', 3000, '🚗'),
('Daughter''s School Transport', 'TRANSPORT', 3000, '�'),
('Car Maintenance / Driver', 'TRANSPORT', 5000, '�')
ON CONFLICT (category) DO UPDATE 
SET group_name = EXCLUDED.group_name, 
    limit_amount = EXCLUDED.limit_amount, 
    icon = EXCLUDED.icon;
