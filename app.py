import streamlit as st
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import sqlite3
import os
import uuid
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATABASE = 'budget_tracker.db'

# Page config - Mobile optimized
st.set_page_config(
    page_title="Family Budget Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsed by default
)

# iOS-style CSS - Mobile optimized for iPhone
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary: #4F46E5;
        --secondary: #10B981;
        --danger: #EF4444;
        --warning: #F59E0B;
        --background: #F8FAFC;
        --surface: #FFFFFF;
        --text-main: #1E293B;
        --text-light: #64748B;
        --radius: 16px;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    .stApp {
        background-color: var(--background);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1000px;
    }

    /* Premium Cards */
    .premium-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255,255,255,0.5);
        backdrop-filter: blur(10px);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease;
    }
    
    .premium-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05);
    }

    /* Gradient Header */
    .header-card {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        border-radius: var(--radius);
        padding: 2.5rem 2rem;
        color: white;
        box-shadow: 0 20px 25px -5px rgba(79, 70, 229, 0.3);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .header-card::before {
        content: '';
        position: absolute;
        top: 0; right: 0;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 60%);
        transform: translate(30%, -30%);
    }

    /* Metric Cards */
    .stat-card {
        background: white;
        border-radius: var(--radius);
        padding: 1.25rem;
        box-shadow: var(--shadow);
        border-left: 4px solid transparent;
        height: 100%;
    }
    
    .stat-label {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-main);
        letter-spacing: -0.02em;
    }
    
    .stat-sub {
        font-size: 12px;
        font-weight: 500;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div, 
    .stDateInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background: white;
        color: var(--text-main);
        height: 48px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div[aria-expanded="true"],
    .stDateInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }

    /* Custom Buttons */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        height: 48px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s;
        border: none;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.15);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px;
        background: white;
        border: 1px solid #E2E8F0;
        color: var(--text-light);
        flex: 1;
        font-weight: 600;
        font-size: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary);
        color: white;
        border-color: var(--primary);
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4F46E5 0%, #818CF8 100%);
        border-radius: 999px;
    }
    
    /* Adjust for mobile */
    @media (max-width: 640px) {
        .header-card {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .stat-value {
            font-size: 24px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Expenses table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        item TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        paid_by TEXT NOT NULL,
        notes TEXT,
        recurrence_frequency TEXT,
        recurrence_next_due TEXT,
        recurrence_active INTEGER DEFAULT 0
    )''')
    
    # Income table
    c.execute('''CREATE TABLE IF NOT EXISTS income (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        source TEXT NOT NULL,
        amount REAL NOT NULL,
        notes TEXT
    )''')
    
    # Category budgets table
    c.execute('''CREATE TABLE IF NOT EXISTS category_budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL UNIQUE,
        group_name TEXT NOT NULL,
        limit_amount REAL NOT NULL,
        icon TEXT
    )''')
    
    # Settings table
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    # Budget month table
    c.execute('''CREATE TABLE IF NOT EXISTS budget_month (
        month TEXT PRIMARY KEY,
        limit_amount REAL DEFAULT 0
    )''')
    
    conn.commit()
    
    # Initialize default category budgets if empty
    c.execute('SELECT COUNT(*) FROM category_budgets')
    if c.fetchone()[0] == 0:
        default_budgets = [
            ('Monthly Rent', 'HOUSING', 15000, '🏠'),
            ('Service Charge / Maintenance', 'HOUSING', 3000, '🛠️'),
            ('Electricity / Gas / Water', 'HOUSING', 3000, '⚡'),
            ('Sinking Fund (Building Repair)', 'HOUSING', 1000, '🏗️'),
            ('Office Commute (Hadi)', 'TRANSPORT', 3000, '🚌'),
            ('Office Commute (Ruhi)', 'TRANSPORT', 3000, '🚗'),
            ("Daughter's School Transport", 'TRANSPORT', 3000, '🚌'),
            ('Car Maintenance / Driver', 'TRANSPORT', 5000, '🔧'),
            ('Hadi (Personal Hangout, Cosmetics)', 'PERSONAL', 3000, '👨'),
            ('Ruhi (Cream, Accessories, Skincare)', 'PERSONAL', 3000, '👩'),
            ('Yusra (Diapers, Wipes, Baby Care)', 'PERSONAL', 5000, '👶'),
            ('Groceries & Food', 'LIVING', 10000, '🛒'),
            ('Household Help (Maid/Cook)', 'LIVING', 4000, '🧹'),
            ('Internet / Phone / Subscriptions', 'LIVING', 2000, '📶'),
            ('Family Hangout', 'LIVING', 4000, '🎉'),
            ('Other', 'OTHERS', 2000, '📦')
        ]
        c.executemany('INSERT INTO category_budgets (category, group_name, limit_amount, icon) VALUES (?, ?, ?, ?)', default_budgets)
        conn.commit()
    
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_next_date(date_str: str, frequency: str) -> str:
    """Calculate next recurring date"""
    date = datetime.strptime(date_str, '%Y-%m-%d')
    if frequency == 'weekly':
        date += timedelta(days=7)
    else:  # monthly
        date += relativedelta(months=1)
    return date.strftime('%Y-%m-%d')

def process_recurring_expenses():
    """Process recurring expenses and create new instances"""
    conn = get_db()
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    added_count = 0
    
    # Get all active recurring expenses
    c.execute('''SELECT * FROM expenses 
                 WHERE recurrence_active = 1 
                 AND recurrence_next_due IS NOT NULL 
                 AND recurrence_next_due <= ?''', (today,))
    
    recurring = c.fetchall()
    
    for expense in recurring:
        expense_dict = dict(expense)
        next_due = expense_dict['recurrence_next_due']
        
        # Create expenses while next_due is today or in the past
        while next_due <= today:
            # Create new expense instance
            new_expense_id = str(uuid.uuid4())
            c.execute('''INSERT INTO expenses 
                        (id, date, item, category, amount, paid_by, notes, recurrence_frequency, recurrence_next_due, recurrence_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (new_expense_id, next_due, expense_dict['item'], expense_dict['category'],
                      expense_dict['amount'], expense_dict['paid_by'], expense_dict['notes'],
                      expense_dict['recurrence_frequency'], None, 0))
            
            added_count += 1
            next_due = calculate_next_date(next_due, expense_dict['recurrence_frequency'])
        
        # Update the parent expense's next_due date
        c.execute('''UPDATE expenses 
                     SET recurrence_next_due = ? 
                     WHERE id = ?''', (next_due, expense_dict['id']))
    
    conn.commit()
    conn.close()
    return added_count

def get_settings():
    """Get app settings"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT value FROM settings WHERE key = ?', ('user',))
    user_row = c.fetchone()
    user = user_row[0] if user_row else None
    
    c.execute('SELECT value FROM settings WHERE key = ?', ('googleScriptUrl',))
    url_row = c.fetchone()
    google_script_url = url_row[0] if url_row else ''
    
    c.execute('SELECT value FROM settings WHERE key = ?', ('lastSynced',))
    last_synced_row = c.fetchone()
    last_synced = last_synced_row[0] if last_synced_row else None
    
    conn.close()
    return user, google_script_url, last_synced

def save_setting(key: str, value: str):
    """Save a setting"""
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

# Initialize database
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# Process recurring expenses on load
if 'recurring_processed' not in st.session_state:
    process_recurring_expenses()
    st.session_state.recurring_processed = True

# Main App
def main():
    # Get current month
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year
    
    # Get data
    conn = get_db()
    c = conn.cursor()
    
    # Get expenses for current month - use year and month number for more reliable comparison
    current_month_num = datetime.now().month
    c.execute('''SELECT * FROM expenses 
                 WHERE strftime('%Y', date) = ? 
                 AND strftime('%m', date) = ?
                 ORDER BY date DESC''', (str(current_year), f"{current_month_num:02d}"))
    
    current_month_expenses = [dict(row) for row in c.fetchall()]
    
    # Get all expenses
    c.execute('SELECT * FROM expenses ORDER BY date DESC')
    all_expenses = [dict(row) for row in c.fetchall()]
    
    # Get category budgets
    c.execute('SELECT * FROM category_budgets ORDER BY group_name, category')
    category_budgets = [dict(row) for row in c.fetchall()]
    
    # Get income for current month
    c.execute('''SELECT * FROM income 
                 WHERE strftime('%Y', date) = ? 
                 AND strftime('%m', date) = ?
                 ORDER BY date DESC''', (str(current_year), f"{current_month_num:02d}"))
    current_month_income = [dict(row) for row in c.fetchall()]

    # Get all income
    c.execute('SELECT * FROM income ORDER BY date DESC')
    all_income = [dict(row) for row in c.fetchall()]

    # Get settings
    user, google_script_url, last_synced = get_settings()
    
    conn.close()
    
    # Calculate totals
    total_budget_limit = sum(b['limit_amount'] for b in category_budgets)
    total_spent = sum(e['amount'] for e in current_month_expenses)
    
    # Core Budget (Excluding 'OTHERS')
    core_budget_categories = [b for b in category_budgets if b['group_name'] != 'OTHERS']
    core_budget_limit = sum(b['limit_amount'] for b in core_budget_categories)
    core_expense_categories = {b['category'] for b in core_budget_categories}
    core_spent = sum(e['amount'] for e in current_month_expenses if e['category'] in core_expense_categories)
    
    total_income = sum(i['amount'] for i in current_month_income)
    
    # Metrics
    investable_surplus = total_income - total_spent
    remaining_budget = total_budget_limit - total_spent
    
    # Premium Header
    st.markdown(f"""
    <div class="header-card">
        <h1 style="margin:0; font-size: 2.2rem; margin-bottom: 0.5rem;">Family Budget</h1>
        <div style="font-size: 1.1rem; opacity: 0.9; font-weight: 500;">
            {current_month} {current_year} {f'• Hello, {user}' if user else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.empty()
    
    # Premium Stats Grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Income breakdown visualization
        income_sources = {}
        for inc in current_month_income:
            src = inc['source']
            income_sources[src] = income_sources.get(src, 0) + inc['amount']
        
        income_bar_html = ""
        if total_income > 0:
            income_bar_html = '<div style="display: flex; height: 8px; width: 100%; background: #F3F4F6; border-radius: 4px; overflow: hidden; margin-top: 12px;">'
            colors = ['#10B981', '#34D399', '#6EE7B7', '#A7F3D0']
            idx = 0
            for source, amount in sorted(income_sources.items(), key=lambda x: x[1], reverse=True):
                pct = (amount / total_income) * 100
                color = colors[idx % len(colors)]
                income_bar_html += f'<div style="width: {pct}%; background: {color};" title="{source}: ৳{amount:,.0f} ({pct:.0f}%)"></div>'
                idx += 1
            income_bar_html += '</div>'
            
            # Simple Legend
            income_bar_html += '<div style="display: flex; gap: 8px; margin-top: 6px; font-size: 10px; color: #64748B; flex-wrap: wrap;">'
            idx = 0
            for source, amount in sorted(income_sources.items(), key=lambda x: x[1], reverse=True)[:3]: # Show top 3
                 color = colors[idx % len(colors)]
                 income_bar_html += f'<div style="display: flex; align-items: center; gap: 3px;"><div style="width: 6px; height: 6px; border-radius: 50%; background: {color};"></div>{source}</div>'
                 idx += 1
            if len(income_sources) > 3:
                income_bar_html += f'<div>+{len(income_sources)-3} more</div>'
            income_bar_html += '</div>'

        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #10B981;">
            <div class="stat-label">Total Income</div>
            <div class="stat-value" style="color: #10B981;">৳{total_income:,.0f}</div>
            <div class="stat-sub" style="color: #10B981;">
                <span>💰</span> Earnings
            </div>
            {income_bar_html}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Budget vs Spent visualization (Core Budget Only)
        budget_pct = (core_spent / core_budget_limit * 100) if core_budget_limit > 0 else 0
        budget_bar_color = "#4F46E5" if budget_pct <= 100 else "#EF4444"
        
        budget_bar_html = f"""
        <div style="margin-top: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748B; margin-bottom: 4px;">
                <span>Spent: ৳{core_spent:,.0f}</span>
                <span>{budget_pct:.0f}%</span>
            </div>
            <div style="height: 8px; width: 100%; background: #F3F4F6; border-radius: 4px; overflow: hidden;">
                <div style="width: {min(budget_pct, 100)}%; height: 100%; background: {budget_bar_color}; border-radius: 4px;"></div>
            </div>
        </div>
        """

        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #4F46E5;">
            <div class="stat-label">Total Budget</div>
            <div class="stat-value">৳{core_budget_limit:,.0f}</div>
            <div class="stat-sub" style="color: #4F46E5;">
                <span>🎯</span> Monthly Goal
            </div>
            {budget_bar_html}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        is_positive = investable_surplus >= 0
        color = "#F59E0B" if is_positive else "#EF4444"
        icon = "🚀" if is_positive else "⚠️"
        
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: {color};">
            <div class="stat-label">Investable Surplus</div>
            <div class="stat-value" style="color: {color}">৳{investable_surplus:,.0f}</div>
            <div class="stat-sub" style="color: {color};">
                <span>{icon}</span> {f'Ready to invest' if is_positive else f'Deficit ৳{abs(investable_surplus):,.0f}'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Settings button in header area
    st.markdown("""
    <div style="text-align: right; margin-bottom: 1rem;">
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs - including Settings tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Add Expense", "📊 Dashboard", "📋 History", "⚙️ Budget Config", "⚙️ Settings & Sync"])
    
    with tab1:
        # Get current user from settings for expense form
        current_user, _, _ = get_settings()
        show_expense_form(category_budgets, current_user)
    
    with tab2:
        show_dashboard(current_month_expenses, all_expenses, category_budgets, current_month_income)
    
    with tab3:
        show_history(all_expenses, category_budgets)
    
    with tab4:
        show_budget_config(category_budgets)
    
    with tab5:
        show_settings_page(user, google_script_url, last_synced, category_budgets)

def show_expense_form(category_budgets, current_user):
    st.markdown("""
    <div class="premium-card">
        <h3 style="margin: 0; color: var(--text-main);">➕ New Transaction</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize form IDs in session state if not present
    if 'expense_form_id' not in st.session_state:
        st.session_state.expense_form_id = 0
    if 'income_form_id' not in st.session_state:
        st.session_state.income_form_id = 0
    
    # Transaction Type Toggle
    transaction_type = st.radio("Type", ["Expense", "Income"], horizontal=True, label_visibility="collapsed")
    
    if transaction_type == "Expense":
        # Initialize session state for category selection
        if 'selected_group' not in st.session_state:
            groups = sorted(list(set(b['group_name'] for b in category_budgets)))
            st.session_state.selected_group = groups[0] if groups else None
        
        # Group selection outside form so it updates immediately
        groups = sorted(list(set(b['group_name'] for b in category_budgets)))
        selected_group = st.selectbox(
            "Category Group", 
            groups,
            index=groups.index(st.session_state.selected_group) if st.session_state.selected_group in groups else 0,
            key="group_select"
        )
        
        # Update session state when group changes
        st.session_state.selected_group = selected_group
        
        # Category selection based on group
        categories_in_group = [b for b in category_budgets if b['group_name'] == selected_group]
        
        if not categories_in_group:
            st.warning("No categories found in this group")
            return
        
        # Create category options with icons
        category_list = [f"{b.get('icon', '📦')} {b['category']}" for b in categories_in_group]
        category_map = {f"{b.get('icon', '📦')} {b['category']}": b['category'] for b in categories_in_group}
        
        selected_category_display = st.selectbox(
            "Category", 
            category_list,
            key="category_select"
        )
        selected_category = category_map[selected_category_display]
        
        # Use dynamic keys for form inputs
        form_id = st.session_state.expense_form_id
        
        with st.form("expense_form", clear_on_submit=False):
            # Responsive columns - stack on mobile
            col1, col2 = st.columns([1, 1])
            
            with col1:
                expense_date = st.date_input("Date", value=datetime.now())
                expense_item = st.text_input("Item", placeholder="What did you buy?", key=f"new_expense_item_{form_id}")
            
            with col2:
                expense_amount = st.number_input("Amount (৳)", min_value=0.0, step=10.0, format="%.0f", key=f"new_expense_amount_{form_id}")
                paid_by = st.radio("Paid By", ["Hadi", "Ruhi"], index=0 if current_user == "Hadi" else 1)
            
            # Recurring expense
            is_recurring = st.checkbox("Recurring Payment?")
            recurrence_frequency = None
            recurrence_next_due = None
            
            if is_recurring:
                col5, col6 = st.columns(2)
                with col5:
                    recurrence_frequency = st.selectbox("Frequency", ["weekly", "monthly"])
                with col6:
                    if recurrence_frequency:
                        next_date = calculate_next_date(expense_date.strftime('%Y-%m-%d'), recurrence_frequency)
                        st.text(f"Next due: {next_date}")
                        recurrence_next_due = next_date
            
            notes = st.text_area("Notes (optional)", key=f"new_expense_notes_{form_id}")
            
            submitted = st.form_submit_button("Add Expense", type="primary")
            
            if submitted:
                if expense_item and expense_amount > 0 and selected_category:
                    expense_id = str(uuid.uuid4())
                    expense_date_str = expense_date.strftime('%Y-%m-%d')
                    
                    conn = get_db()
                    c = conn.cursor()
                    
                    c.execute('''INSERT INTO expenses 
                                (id, date, item, category, amount, paid_by, notes, recurrence_frequency, recurrence_next_due, recurrence_active)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (expense_id, expense_date_str, expense_item, selected_category,
                              expense_amount, paid_by, notes, recurrence_frequency, recurrence_next_due, 1 if is_recurring else 0))
                    
                    conn.commit()
                    conn.close()
                    
                    # Sync to cloud
                    sync_to_cloud()
                    
                    # Increment form ID to clear inputs
                    st.session_state.expense_form_id += 1
                    
                    st.success(f"Expense added successfully! (৳{expense_amount:,.0f} on {expense_date_str})")
                    # Force rerun to refresh the page and show new empty form
                    st.rerun()
                else:
                    st.error("Please fill in all required fields.")

    else: # Income
        # Use dynamic keys for form inputs
        form_id = st.session_state.income_form_id
        
        with st.form("income_form", clear_on_submit=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                income_date = st.date_input("Date", value=datetime.now())
                income_source = st.text_input("Source", placeholder="e.g. Salary, Business, Bonus", key=f"new_income_source_{form_id}")
            
            with col2:
                income_amount = st.number_input("Amount (৳)", min_value=0.0, step=10.0, format="%.0f", key=f"new_income_amount_{form_id}")
            
            notes = st.text_area("Notes (optional)", key=f"new_income_notes_{form_id}")
            
            submitted = st.form_submit_button("Add Income", type="primary")
            
            if submitted:
                if income_source and income_amount > 0:
                    income_id = str(uuid.uuid4())
                    income_date_str = income_date.strftime('%Y-%m-%d')
                    
                    conn = get_db()
                    c = conn.cursor()
                    
                    c.execute('''INSERT INTO income 
                                (id, date, source, amount, notes)
                                VALUES (?, ?, ?, ?, ?)''',
                             (income_id, income_date_str, income_source, income_amount, notes))
                    
                    conn.commit()
                    conn.close()
                    
                    # Sync to cloud
                    sync_to_cloud()
                    
                    # Increment form ID to clear inputs
                    st.session_state.income_form_id += 1
                    
                    st.success(f"Income added successfully! (৳{income_amount:,.0f})")
                    st.rerun()
                else:
                    st.error("Please fill in Source and Amount.")
                
def show_dashboard(current_month_expenses, all_expenses, category_budgets, current_month_income):
    st.markdown("""
    <div class="premium-card">
        <h3 style="margin: 0; color: var(--text-main);">📊 Spending Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not current_month_expenses:
        st.info("No expenses for this month yet.")
        return
    
    # Category Breakdown
    st.subheader("Category Breakdown")
    
    # Group budgets by group
    grouped_budgets = {}
    for budget in category_budgets:
        group = budget['group_name']
        if group not in grouped_budgets:
            grouped_budgets[group] = []
        grouped_budgets[group].append(budget)
    
    # Calculate spent per category
    category_spent = {}
    for expense in current_month_expenses:
        cat = expense['category']
        category_spent[cat] = category_spent.get(cat, 0) + expense['amount']
    
    # Display category breakdown
    for group, budgets in grouped_budgets.items():
        with st.expander(f"📁 {group}", expanded=True):
            for budget in budgets:
                spent = category_spent.get(budget['category'], 0)
                limit = budget['limit_amount']
                percentage = (spent / limit * 100) if limit > 0 else 0
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{budget.get('icon', '📦')} **{budget['category']}**")
                    st.progress(min(percentage / 100, 1.0))
                with col2:
                    st.metric("", f"৳{spent:,.0f}", f"/ ৳{limit:,.0f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Expenses by Category")
        category_data = {}
        for expense in current_month_expenses:
            cat = expense['category']
            category_data[cat] = category_data.get(cat, 0) + expense['amount']
        
        if category_data:
            df_cat = pd.DataFrame(list(category_data.items()), columns=['Category', 'Amount'])
            fig_pie = px.pie(df_cat, values='Amount', names='Category', 
                           title="Spending by Category")
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("Spending by Person")
        payer_data = {'Hadi': 0, 'Ruhi': 0}
        for expense in current_month_expenses:
            payer = expense['paid_by']
            payer_data[payer] = payer_data.get(payer, 0) + expense['amount']
        
        df_payer = pd.DataFrame(list(payer_data.items()), columns=['Person', 'Amount'])
        fig_bar = px.bar(df_payer, x='Person', y='Amount',                         title="Spending by Person",
                         color='Person',
                         color_discrete_map={'Hadi': '#4F46E5', 'Ruhi': '#10B981'})
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            title_font_size=16
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Trends chart
    st.subheader("Spending Trends")
    time_frame = st.radio("Time Frame", ["Daily", "Weekly", "Monthly", "Quarterly"], horizontal=True)
    
    # Prepare trend data
    trend_data = prepare_trend_data(all_expenses, time_frame.lower())
    if trend_data:
        df_trend = pd.DataFrame(trend_data, columns=['Period', 'Amount'])
        fig_trend = px.bar(df_trend, x='Period', y='Amount', 
                          title=f"Spending Trends ({time_frame})")
        st.plotly_chart(fig_trend, use_container_width=True)

def prepare_trend_data(expenses, time_frame):
    """Prepare trend data based on time frame"""
    today = datetime.now()
    data_map = {}
    
    if time_frame == 'daily':
        # Last 30 days
        for i in range(30):
            date = today - timedelta(days=29-i)
            key = date.strftime('%Y-%m-%d')
            data_map[key] = 0
    elif time_frame == 'weekly':
        # Last 12 weeks
        for i in range(12):
            week_start = today - timedelta(weeks=11-i)
            week_num = week_start.isocalendar()[1]
            key = f"{week_start.year}-W{week_num}"
            data_map[key] = 0
    elif time_frame == 'monthly':
        # Last 12 months
        for i in range(12):
            month_date = today - relativedelta(months=11-i)
            key = month_date.strftime('%Y-%m')
            data_map[key] = 0
    elif time_frame == 'quarterly':
        # Last 4 quarters
        for i in range(4):
            quarter_date = today - relativedelta(months=9-i*3)
            quarter = (quarter_date.month - 1) // 3 + 1
            key = f"{quarter_date.year}-Q{quarter}"
            data_map[key] = 0
    
    # Aggregate expenses
    for expense in expenses:
        exp_date = datetime.strptime(expense['date'], '%Y-%m-%d')
        key = None
        
        if time_frame == 'daily':
            key = exp_date.strftime('%Y-%m-%d')
        elif time_frame == 'weekly':
            week_num = exp_date.isocalendar()[1]
            key = f"{exp_date.year}-W{week_num}"
        elif time_frame == 'monthly':
            key = exp_date.strftime('%Y-%m')
        elif time_frame == 'quarterly':
            quarter = (exp_date.month - 1) // 3 + 1
            key = f"{exp_date.year}-Q{quarter}"
        
        if key and key in data_map:
            data_map[key] = data_map.get(key, 0) + expense['amount']
    
    return [(k, v) for k, v in sorted(data_map.items())]

def show_history(all_expenses, category_budgets):
    st.markdown("""
    <div class="premium-card">
        <h3 style="margin: 0; color: var(--text-main);">📋 Transaction History</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not all_expenses:
        st.info("No expenses recorded yet.")
        return
    
    # Create category icon map
    category_icons = {b['category']: b.get('icon', '📦') for b in category_budgets}
    
    # Get all groups and categories for edit form
    groups = sorted(list(set(b['group_name'] for b in category_budgets)))
    categories_by_group = {}
    for budget in category_budgets:
        group = budget['group_name']
        if group not in categories_by_group:
            categories_by_group[group] = []
        categories_by_group[group].append(budget)
    
    # Initialize session state for editing
    if 'editing_expense_id' not in st.session_state:
        st.session_state.editing_expense_id = None
    
    # Display expenses
    for expense in all_expenses[:50]:  # Show last 50
        expense_id = expense['id']
        is_editing = st.session_state.editing_expense_id == expense_id
        
        if is_editing:
            # Edit form
            with st.container():
                st.subheader("✏️ Edit Expense")
                with st.form(f"edit_form_{expense_id}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_date = st.date_input(
                            "Date",
                            value=datetime.strptime(expense['date'], '%Y-%m-%d').date(),
                            key=f"edit_date_{expense_id}"
                        )
                        edit_item = st.text_input(
                            "Item",
                            value=expense['item'],
                            key=f"edit_item_{expense_id}"
                        )
                    
                    with col2:
                        # Group and category selection
                        edit_group = st.selectbox(
                            "Category Group",
                            groups,
                            index=groups.index(expense.get('group', groups[0])) if expense.get('group') in groups else 0,
                            key=f"edit_group_{expense_id}"
                        )
                        
                        categories_in_group = [b for b in category_budgets if b['group_name'] == edit_group]
                        category_list = [f"{b.get('icon', '📦')} {b['category']}" for b in categories_in_group]
                        category_map = {f"{b.get('icon', '📦')} {b['category']}": b['category'] for b in categories_in_group}
                        
                        current_cat_display = f"{category_icons.get(expense['category'], '📦')} {expense['category']}"
                        if current_cat_display not in category_list:
                            current_cat_display = category_list[0] if category_list else ""
                        
                        edit_category_display = st.selectbox(
                            "Category",
                            category_list,
                            index=category_list.index(current_cat_display) if current_cat_display in category_list else 0,
                            key=f"edit_category_{expense_id}"
                        )
                        edit_category = category_map[edit_category_display]
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        edit_amount = st.number_input(
                            "Amount (৳)",
                            min_value=0.0,
                            step=0.01,
                            value=float(expense['amount']),
                            key=f"edit_amount_{expense_id}"
                        )
                    with col4:
                        edit_paid_by = st.radio(
                            "Paid By",
                            ["Hadi", "Ruhi"],
                            index=0 if expense['paid_by'] == "Hadi" else 1,
                            key=f"edit_paid_by_{expense_id}"
                        )
                    
                    # Recurring expense
                    edit_is_recurring = st.checkbox(
                        "Recurring Payment?",
                        value=bool(expense.get('recurrence_active')),
                        key=f"edit_recurring_{expense_id}"
                    )
                    
                    edit_recurrence_frequency = None
                    edit_recurrence_next_due = None
                    
                    if edit_is_recurring:
                        col5, col6 = st.columns(2)
                        with col5:
                            edit_recurrence_frequency = st.selectbox(
                                "Frequency",
                                ["weekly", "monthly"],
                                index=0 if expense.get('recurrence_frequency') == 'weekly' else 1,
                                key=f"edit_frequency_{expense_id}"
                            )
                        with col6:
                            if edit_recurrence_frequency:
                                next_date = calculate_next_date(edit_date.strftime('%Y-%m-%d'), edit_recurrence_frequency)
                                st.text(f"Next due: {next_date}")
                                edit_recurrence_next_due = next_date
                    
                    edit_notes = st.text_area(
                        "Notes (optional)",
                        value=expense.get('notes', ''),
                        key=f"edit_notes_{expense_id}"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Save Changes", type="primary"):
                            # Update expense
                            conn = get_db()
                            c = conn.cursor()
                            
                            c.execute('''UPDATE expenses 
                                        SET date = ?, item = ?, category = ?, amount = ?, paid_by = ?, notes = ?,
                                            recurrence_frequency = ?, recurrence_next_due = ?, recurrence_active = ?
                                        WHERE id = ?''',
                                    (edit_date.strftime('%Y-%m-%d'), edit_item, edit_category, edit_amount,
                                     edit_paid_by, edit_notes, edit_recurrence_frequency, edit_recurrence_next_due,
                                     1 if edit_is_recurring else 0, expense_id))
                            
                            conn.commit()
                            conn.close()
                            
                            # Sync to cloud
                            sync_to_cloud()
                            
                            st.session_state.editing_expense_id = None
                            st.success("Expense updated successfully!")
                            st.rerun()
                    
                    with col_cancel:
                        if st.form_submit_button("❌ Cancel"):
                            st.session_state.editing_expense_id = None
                            st.rerun()
        else:
            # Premium List Item
            with st.container():
                st.markdown(f"""
                <div style="
                    background: white;
                    border-radius: 12px;
                    padding: 1rem;
                    margin-bottom: 0.75rem;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                    border: 1px solid #E2E8F0;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                ">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="
                            background: #F1F5F9;
                            width: 40px; height: 40px;
                            border-radius: 10px;
                            display: flex; align-items: center; justify-content: center;
                            font-size: 20px;
                        ">
                            {category_icons.get(expense['category'], '📦')}
                        </div>
                        <div>
                            <div style="font-weight: 600; color: #1E293B;">{expense['item']}</div>
                            <div style="font-size: 12px; color: #64748B;">
                                {expense['category']} • {expense['paid_by']} { '• 🔄 Recurring' if expense.get('recurrence_active') else ''}
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 700; color: #1E293B;">৳{expense['amount']:,.0f}</div>
                        <div style="font-size: 11px; color: #94A3B8;">{expense['date']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons in a small row below (optional)
                col_edit, col_delete, _ = st.columns([1, 1, 8])
                with col_edit:
                    if st.button("✏️", key=f"edit_btn_{expense_id}", help="Edit"):
                         st.session_state.editing_expense_id = expense_id
                         st.rerun()
                with col_delete:
                    if st.button("🗑️", key=f"delete_btn_{expense_id}", help="Delete"):
                        conn = get_db()
                        c = conn.cursor()
                        c.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
                        conn.commit()
                        conn.close()
                        sync_to_cloud()
                        st.success("Deleted")
                        st.rerun()

def show_settings_page(user, google_script_url, last_synced, category_budgets):
    st.markdown("""
    <div style="background: white; 
                padding: 1.5rem; 
                border-radius: 16px; 
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h2 style="margin: 0 0 1rem 0; font-size: 24px; font-weight: 700;">⚙️ Settings & Sync</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # User selection
    st.markdown("### 👤 User Profile")
    selected_user = st.radio(
        "Select User",
        ["Hadi", "Ruhi"],
        index=0 if user == "Hadi" else (1 if user == "Ruhi" else 0),
        key="settings_user_select",
        horizontal=True
    )
    
    if selected_user != user:
        save_setting('user', selected_user)
        st.success(f"✓ User set to {selected_user}")
        st.rerun()
    
    if user:
        st.info(f"✓ Currently logged in as **{user}**")
    
    st.divider()
    
    # Cloud Sync Section
    st.markdown("### ☁️ Google Sheets Sync")
    st.markdown("**Connect to Google Sheets:**")
    
    sync_url = st.text_input(
        "Google Apps Script URL",
        value=google_script_url,
        placeholder="https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec",
        key="settings_sync_url",
        help="Deploy your Google Apps Script as a web app and paste the URL here"
    )
    
    col_save, col_sync = st.columns(2)
    with col_save:
        if sync_url != google_script_url:
            if st.button("💾 Save URL", use_container_width=True, key="settings_save_url"):
                save_setting('googleScriptUrl', sync_url)
                st.success("URL saved!")
                st.rerun()
        elif sync_url:
            st.success("✓ URL saved")
    
    with col_sync:
        col_pull, col_push = st.columns(2)
        with col_pull:
            if st.button("⬇️ Pull", use_container_width=True, key="settings_pull", help="Overwrite local data with Google Sheet data"):
                with st.spinner("Downloading..."):
                    if sync_from_cloud(sync_url):
                        st.success("Pulled!")
                        st.rerun()
                    else:
                        st.error("Pull failed")
        
        with col_push:
            if st.button("⬆️ Push", use_container_width=True, key="settings_push", help="Upload local data to Google Sheet"):
                with st.spinner("Uploading..."):
                    if sync_to_cloud():
                        st.success("Pushed!")
                        save_setting('lastSynced', datetime.now().isoformat())
                    else:
                        st.error("Push failed")
    
    if last_synced:
        st.info(f"🕒 Last synced: {last_synced[:19]}")
    
    if not sync_url:
        st.markdown("""
        <div style="background-color: #FFF3CD; 
                    border-left: 4px solid #FF9500; 
                    padding: 1rem; 
                    border-radius: 8px; 
                    margin-top: 1rem;">
            <p style="margin: 0; font-size: 13px; color: #856404;">
                <strong>How to set up Google Sheets sync:</strong><br>
                1. Create a Google Apps Script<br>
                2. Deploy it as a web app<br>
                3. Paste the deployment URL above
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Danger Zone
    st.markdown("### 🚨 Danger Zone")
    st.write("Resetting the data will delete all expenses and income records from this device.")
    
    if st.button("🗑️ Reset All Data", type="primary", use_container_width=True):
        # Confirmation dialog simulation using session state
        st.session_state.confirm_reset = True
        st.rerun()
        
    if st.session_state.get('confirm_reset'):
        st.warning("Are you sure? This cannot be undone.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Yes, Delete Everything", type="primary", use_container_width=True):
                conn = get_db()
                c = conn.cursor()
                c.execute('DELETE FROM expenses')
                c.execute('DELETE FROM income')
                conn.commit()
                conn.close()
                
                # Sync empty state to cloud
                if google_script_url:
                    sync_to_cloud()
                
                st.session_state.confirm_reset = False
                st.success("All data has been reset.")
                st.rerun()
        with col_no:
            if st.button("Cancel", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()

def show_settings_page(user, google_script_url, last_synced, category_budgets):
    st.markdown("""
    <div style="background: white; 
                padding: 1.5rem; 
                border-radius: 16px; 
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h2 style="margin: 0 0 1rem 0; font-size: 24px; font-weight: 700;">⚙️ Settings & Sync</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # User selection
    st.markdown("### 👤 User Profile")
    selected_user = st.radio(
        "Select User",
        ["Hadi", "Ruhi"],
        index=0 if user == "Hadi" else (1 if user == "Ruhi" else 0),
        key="settings_user_select",
        horizontal=True
    )
    
    if selected_user != user:
        save_setting('user', selected_user)
        st.success(f"✓ User set to {selected_user}")
        st.rerun()
    
    if user:
        st.info(f"✓ Currently logged in as **{user}**")
    
    st.divider()
    
    # Cloud Sync Section
    st.markdown("### ☁️ Google Sheets Sync")
    st.markdown("**Connect to Google Sheets:**")
    
    sync_url = st.text_input(
        "Google Apps Script URL",
        value=google_script_url,
        placeholder="https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec",
        key="settings_sync_url",
        help="Deploy your Google Apps Script as a web app and paste the URL here"
    )
    
    col_save, col_sync = st.columns(2)
    with col_save:
        if sync_url != google_script_url:
            if st.button("💾 Save URL", use_container_width=True, key="settings_save_url"):
                save_setting('googleScriptUrl', sync_url)
                st.success("URL saved!")
                st.rerun()
        elif sync_url:
            st.success("✓ URL saved")
    
    with col_sync:
        if sync_url:
            if st.button("🔄 Sync Now", use_container_width=True, key="settings_sync_now"):
                with st.spinner("Syncing..."):
                    if sync_from_cloud(sync_url):
                        st.success("Sync completed!")
                        st.rerun()
                    else:
                        st.error("Sync failed. Check your URL.")
    
    if last_synced:
        st.info(f"🕒 Last synced: {last_synced[:19]}")
    
    if not sync_url:
        st.markdown("""
        <div style="background-color: #FFF3CD; 
                    border-left: 4px solid #FF9500; 
                    padding: 1rem; 
                    border-radius: 8px; 
                    margin-top: 1rem;">
            <p style="margin: 0; font-size: 13px; color: #856404;">
                <strong>How to set up Google Sheets sync:</strong><br>
                1. Create a Google Apps Script<br>
                2. Deploy it as a web app<br>
                3. Paste the deployment URL above
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_budget_config(category_budgets):
    st.markdown("""
    <div class="premium-card">
        <h3 style="margin: 0; color: var(--text-main);">Configuration</h3>
    </div>
    """, unsafe_allow_html=True)
    st.info("💡 Tip: Changes saved here will be synced to Google Sheets.")
    
    # Initialize session state for new category
    if 'new_category_group' not in st.session_state:
        st.session_state.new_category_group = 'OTHERS'
    if 'new_category_name' not in st.session_state:
        st.session_state.new_category_name = ''
    if 'new_category_limit' not in st.session_state:
        st.session_state.new_category_limit = 0.0
    if 'new_category_icon' not in st.session_state:
        st.session_state.new_category_icon = '📦'
    
    # Group budgets
    grouped_budgets = {}
    for budget in category_budgets:
        group = budget['group_name']
        if group not in grouped_budgets:
            grouped_budgets[group] = []
        grouped_budgets[group].append(budget)
    
    # Add new category section
    with st.expander("➕ Add New Category", expanded=False):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            # Get existing groups or allow new group
            existing_groups = sorted(list(grouped_budgets.keys()))
            new_group_option = st.selectbox(
                "Group",
                ["Create New Group"] + existing_groups,
                key="new_group_select"
            )
            
            if new_group_option == "Create New Group":
                new_group_name = st.text_input(
                    "New Group Name",
                    value="",
                    placeholder="e.g., ENTERTAINMENT",
                    key="new_group_name_input"
                ).upper()
                if not new_group_name:
                    new_group_name = "OTHERS"
            else:
                new_group_name = new_group_option
        
        with col2:
            new_category_name = st.text_input(
                "Category Name",
                value=st.session_state.new_category_name,
                placeholder="e.g., Netflix Subscription",
                key="new_category_name_input"
            )
        
        with col3:
            new_category_limit = st.number_input(
                "Limit (৳)",
                min_value=0.0,
                step=100.0,
                value=st.session_state.new_category_limit,
                key="new_category_limit_input"
            )
        
        with col4:
            # Icon selector with common icons
            common_icons = {
                '📦 Default': '📦',
                '💰 Money': '💰',
                '🏠 House': '🏠',
                '🚗 Car': '🚗',
                '🍔 Food': '🍔',
                '👕 Clothing': '👕',
                '💊 Health': '💊',
                '📚 Education': '📚',
                '🎮 Entertainment': '🎮',
                '🎬 Movies': '🎬',
                '✈️ Travel': '✈️',
                '💻 Tech': '💻',
                '📱 Phone': '📱',
                '🛒 Shopping': '🛒',
                '⚡ Utilities': '⚡',
                '💧 Water': '💧',
                '🔥 Gas': '🔥',
                '🎁 Gifts': '🎁',
                '🎉 Party': '🎉',
                '🏥 Medical': '🏥',
                '🎓 School': '🎓',
                '💼 Work': '💼',
                '🧹 Cleaning': '🧹',
                '🔧 Maintenance': '🔧',
                '🛠️ Tools': '🛠️',
                '👨 Male': '👨',
                '👩 Female': '👩',
                '👶 Baby': '👶',
                '🚌 Transport': '🚌',
                '🚇 Metro': '🚇',
                '🚲 Bike': '🚲',
                '⛽ Fuel': '⛽'
            }
            
            # Create icon options for selectbox
            icon_display_options = list(common_icons.keys())
            current_icon_display = None
            for key, value in common_icons.items():
                if value == st.session_state.new_category_icon:
                    current_icon_display = key
                    break
            
            selected_icon_display = st.selectbox(
                "Icon",
                icon_display_options,
                index=icon_display_options.index(current_icon_display) if current_icon_display else 0,
                key="new_category_icon_select"
            )
            selected_icon = common_icons[selected_icon_display]
            
            # Also allow custom icon input
            custom_icon = st.text_input(
                "Custom icon (optional)",
                value="",
                max_chars=2,
                key="new_category_icon_custom",
                help="Type a custom emoji (1-2 characters) or leave empty to use selected icon"
            )
            
            new_category_icon = custom_icon if custom_icon else selected_icon
            st.session_state.new_category_icon = new_category_icon if new_category_icon else '📦'
            
            # Show preview
            st.markdown(f"**Preview:** {new_category_icon}")
        
        if st.button("➕ Add Category", type="primary"):
            if new_category_name:
                # Add to category_budgets list
                category_budgets.append({
                    'category': new_category_name,
                    'group_name': new_group_name,
                    'limit_amount': new_category_limit,
                    'icon': new_category_icon or '📦'
                })
                
                # Save to database
                conn = get_db()
                c = conn.cursor()
                c.execute('''INSERT INTO category_budgets (category, group_name, limit_amount, icon)
                             VALUES (?, ?, ?, ?)''',
                         (new_category_name, new_group_name, new_category_limit, new_category_icon or '📦'))
                conn.commit()
                conn.close()
                
                # Sync to cloud
                sync_to_cloud()
                
                # Clear form
                st.session_state.new_category_name = ''
                st.session_state.new_category_limit = 0.0
                st.session_state.new_category_icon = '📦'
                
                st.success(f"Category '{new_category_name}' added!")
                st.rerun()
            else:
                st.error("Please enter a category name")
    
    st.divider()
    
    # Edit existing budgets
    with st.form("budget_config_form"):
        updated_budgets = []
        
        for group, budgets in sorted(grouped_budgets.items()):
            with st.expander(f"📁 {group}", expanded=True):
                for budget in budgets:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        # Allow editing category name
                        new_category_name = st.text_input(
                            "Category",
                            value=budget['category'],
                            key=f"cat_{budget['category']}_{group}"
                        )
                    with col2:
                        new_limit = st.number_input(
                            "Limit",
                            value=float(budget['limit_amount']),
                            min_value=0.0,
                            step=100.0,
                            key=f"limit_{budget['category']}_{group}"
                        )
                    with col3:
                        current_icon = budget.get('icon', '📦')
                        
                        # Icon selector for editing
                        common_icons = {
                            '📦 Default': '📦', '💰 Money': '💰', '🏠 House': '🏠', '🚗 Car': '🚗',
                            '🍔 Food': '🍔', '👕 Clothing': '👕', '💊 Health': '💊', '📚 Education': '📚',
                            '🎮 Entertainment': '🎮', '🎬 Movies': '🎬', '✈️ Travel': '✈️', '💻 Tech': '💻',
                            '📱 Phone': '📱', '🛒 Shopping': '🛒', '⚡ Utilities': '⚡', '💧 Water': '💧',
                            '🔥 Gas': '🔥', '🎁 Gifts': '🎁', '🎉 Party': '🎉', '🏥 Medical': '🏥',
                            '🎓 School': '🎓', '💼 Work': '💼', '🧹 Cleaning': '🧹', '🔧 Maintenance': '🔧',
                            '🛠️ Tools': '🛠️', '👨 Male': '👨', '👩 Female': '👩', '👶 Baby': '👶',
                            '🚌 Transport': '🚌', '🚇 Metro': '🚇', '🚲 Bike': '🚲', '⛽ Fuel': '⛽'
                        }
                        
                        # Find current icon in options
                        current_icon_key = None
                        for key, value in common_icons.items():
                            if value == current_icon:
                                current_icon_key = key
                                break
                        
                        icon_display_options = list(common_icons.keys())
                        selected_icon_display = st.selectbox(
                            "Icon",
                            icon_display_options,
                            index=icon_display_options.index(current_icon_key) if current_icon_key else 0,
                            key=f"icon_select_{budget['category']}_{group}"
                        )
                        selected_icon = common_icons[selected_icon_display]
                        
                        # Allow custom icon
                        custom_icon = st.text_input(
                            "Custom",
                            value="",
                            max_chars=2,
                            key=f"icon_custom_{budget['category']}_{group}",
                            help="Type custom emoji or leave empty"
                        )
                        
                        new_icon = custom_icon if custom_icon else selected_icon
                    with col4:
                        # Checkbox to mark for deletion
                        delete_category = st.checkbox(
                            "Delete",
                            key=f"delete_{budget['category']}_{group}",
                            help="Mark to delete this category"
                        )
                    
                    # Only add if not marked for deletion
                    if not delete_category:
                        updated_budgets.append({
                            'category': new_category_name,
                            'group': group,
                            'limit': new_limit,
                            'icon': new_icon or '📦'
                        })
        
        submitted = st.form_submit_button("💾 Save Changes", type="primary")
        
        if submitted:
            conn = get_db()
            c = conn.cursor()
            
            # Delete all existing budgets
            c.execute('DELETE FROM category_budgets')
            
            # Insert updated budgets (only those not marked for deletion)
            for budget in updated_budgets:
                c.execute('''INSERT INTO category_budgets (category, group_name, limit_amount, icon)
                             VALUES (?, ?, ?, ?)''',
                         (budget['category'], budget['group'], budget['limit'], budget['icon']))
            
            conn.commit()
            conn.close()
            
            # Sync to cloud
            sync_to_cloud()
            
            st.success("Budget configuration updated!")
            st.rerun()

def sync_from_cloud(url: str):
    """Fetch data from Google Apps Script"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            conn = get_db()
            c = conn.cursor()
            
            if 'expenses' in data:
                c.execute('DELETE FROM expenses')
                for expense in data['expenses']:
                    c.execute('''INSERT INTO expenses 
                                (id, date, item, category, amount, paid_by, notes, 
                                 recurrence_frequency, recurrence_next_due, recurrence_active)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (expense['id'], expense['date'], expense['item'], expense['category'],
                              expense['amount'], expense['paidBy'], expense.get('notes', ''),
                              expense.get('recurrence', {}).get('frequency'),
                              expense.get('recurrence', {}).get('nextDue'),
                              1 if expense.get('recurrence', {}).get('active') else 0))
            
            if 'categories' in data and len(data['categories']) > 0:
                c.execute('DELETE FROM category_budgets')
                for cat in data['categories']:
                    c.execute('''INSERT INTO category_budgets (category, group_name, limit_amount, icon)
                                 VALUES (?, ?, ?, ?)''',
                             (cat['category'], cat['group'], cat['limit'], cat.get('icon', '📦')))

            if 'income' in data:
                c.execute('DELETE FROM income')
                for inc in data['income']:
                    c.execute('''INSERT INTO income (id, date, source, amount, notes)
                                 VALUES (?, ?, ?, ?, ?)''',
                             (inc['id'], inc['date'], inc['source'], inc['amount'], inc.get('notes', '')))
            
            conn.commit()
            conn.close()
            
            save_setting('lastSynced', datetime.now().isoformat())
            return True
    except Exception as e:
        st.error(f"Sync error: {e}")
        return False
    return False

def sync_to_cloud():
    """Push data to Google Apps Script"""
    user, google_script_url, _ = get_settings()
    
    if not google_script_url:
        return False
    
    conn = get_db()
    c = conn.cursor()
    
    # Get all expenses
    c.execute('SELECT * FROM expenses')
    expenses = []
    for row in c.fetchall():
        expense = dict(row)
        expense_dict = {
            'id': expense['id'],
            'date': expense['date'],
            'item': expense['item'],
            'category': expense['category'],
            'amount': expense['amount'],
            'paidBy': expense['paid_by'],
            'notes': expense.get('notes', '')
        }
        if expense['recurrence_active']:
            expense_dict['recurrence'] = {
                'frequency': expense['recurrence_frequency'],
                'nextDue': expense['recurrence_next_due'],
                'active': True
            }
        expenses.append(expense_dict)
    
    # Get category budgets
    c.execute('SELECT * FROM category_budgets')
    categories = []
    for row in c.fetchall():
        cat = dict(row)
        categories.append({
            'category': cat['category'],
            'group': cat['group_name'],
            'limit': cat['limit_amount'],
            'icon': cat.get('icon', '📦')
        })
    
    # Get income
    c.execute('SELECT * FROM income')
    income_list = []
    for row in c.fetchall():
        inc = dict(row)
        income_list.append({
            'id': inc['id'],
            'date': inc['date'],
            'source': inc['source'],
            'amount': inc['amount'],
            'notes': inc.get('notes', '')
        })
    
    current_month = datetime.now().strftime('%B')
    
    payload = {
        'expenses': expenses,
        'income': income_list,
        'categories': categories,
        'budgetMonth': current_month,
        'lastUpdated': datetime.now().isoformat()
    }
    
    conn.close()
    
    try:
        response = requests.post(google_script_url, json=payload, timeout=10)
        if response.status_code == 200:
            save_setting('lastSynced', datetime.now().isoformat())
            return True
    except Exception as e:
        print(f"Push sync error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    main()
