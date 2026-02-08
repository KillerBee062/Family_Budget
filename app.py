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
import streamlit.components.v1 as components
import textwrap

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
    /* iOS Design System */
    /* SF Pro Display is Apple-proprietary, falling back to system fonts */

    :root {
        --ios-bg: #F2F2F7;
        --ios-card-bg: #FFFFFF;
        --ios-text: #000000;
        --ios-text-secondary: #8E8E93;
        --ios-blue: #007AFF;
        --ios-green: #34C759;
        --ios-red: #FF3B30;
        --ios-orange: #FF9500;
        --ios-indigo: #5856D6;
        --ios-gray: #8E8E93;
        --ios-separator: #C6C6C8;
        --radius: 12px;
    }

    .stApp {
        background-color: var(--ios-bg);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: var(--ios-text);
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 1000px;
    }

    /* iOS Card Style (replaces Premium Card) */
    .premium-card {
        background: var(--ios-card-bg);
        border-radius: var(--radius);
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
        border: none;
    }

    /* iOS Header Style */
    .header-card {
        background: transparent;
        padding: 0 0 16px 0;
        margin-bottom: 16px;
        color: var(--ios-text);
        box-shadow: none;
        border-radius: 0;
    }
    
    .header-card h1 {
        font-size: 34px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: var(--ios-text);
        margin-bottom: 4px;
    }

    /* iOS Grid / Stat Card Style */
    .stat-card {
        background: var(--ios-card-bg);
        border-radius: var(--radius);
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .stat-label {
        font-size: 13px;
        font-weight: 600;
        color: var(--ios-text-secondary);
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    
    .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--ios-text);
        letter-spacing: -0.5px;
    }
    
    .stat-sub {
        font-size: 13px;
        font-weight: 500;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
        color: var(--ios-text-secondary);
    }

    /* Input Fields - iOS Grouped Style */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div, 
    .stDateInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #E5E5EA; /* System Gray 5 */
        background: white;
        color: var(--ios-text);
        height: 44px;
        box-shadow: none;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div[aria-expanded="true"],
    .stDateInput > div > div > input:focus {
        border-color: var(--ios-blue);
        box-shadow: 0 0 0 1px var(--ios-blue);
    }

    /* Custom Buttons - iOS Style */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        height: 44px;
        box-shadow: none;
        border: none;
        background: #E5E5EA; /* System Gray 5 */
        color: var(--ios-blue);
    }
    
    .stButton > button[kind="primary"] {
        background: var(--ios-blue);
        color: white;
    }
    
    .stButton > button:hover {
        opacity: 0.8;
        transform: none;
        box-shadow: none;
    }
    
    /* Tabs - iOS Segmented Control Style */
    .stTabs [data-baseweb="tab-list"] {
        background: #E5E5EA;
        padding: 4px;
        border-radius: 10px;
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 36px;
        border-radius: 7px;
        background: transparent;
        border: none;
        color: var(--ios-text);
        font-weight: 500;
        font-size: 13px;
        box-shadow: none;
        margin: 0;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: var(--ios-text);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: var(--ios-blue);
        border-radius: 999px;
    }

    /* Custom Scrollbar for iframes */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent; 
    }
    ::-webkit-scrollbar-thumb {
        background: #C1C1C1; 
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #A8A8A8; 
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
    
    # Initialize default category budgets (safe insert)
    default_budgets = [
        ('Monthly Rent', 'HOUSING', 15000, '🏠'),
        ('Service Charge / Maintenance', 'HOUSING', 3000, '🛠️'),
        ('Electricity / Gas / Water', 'HOUSING', 3000, '⚡'),
        ('Sinking Fund (Building Repair)', 'HOUSING', 1000, '🏗️'),
        ('Office Commute (Hadi)', 'TRANSPORT', 3000, '🚌'),
        ('Office Commute (Ruhi)', 'TRANSPORT', 3000, '🚗'),
        ("Daughter's School Transport", 'TRANSPORT', 3000, '🚌'),
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
    ]
    c.executemany('INSERT OR IGNORE INTO category_budgets (category, group_name, limit_amount, icon) VALUES (?, ?, ?, ?)', default_budgets)
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
    
    if added_count > 0:
        sync_to_cloud()
        
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
    # Default URL provided by user
    default_url = "https://script.google.com/macros/s/AKfycbxi45hDC5UiXLxxdGqNzrfKP9uydfZDb0YVSifE3W-2q9saFiHINQrSeub5QrrCkZkA/exec"
    google_script_url = url_row[0] if url_row else default_url
    
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
    
    # iOS Header
    st.markdown(f"""
    <div class="header-card">
        <h1>Family Budget</h1>
        <div style="font-size: 17px; font-weight: 600; color: var(--ios-text-secondary);">{current_month} {current_year}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.empty()
    
    # iOS Grid Layout (2x2)
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    # Card 1: Income (Green)
    with row1_col1:
        income_pct = min((total_income / core_budget_limit * 100), 100) if core_budget_limit > 0 else 0
        
        # iOS Reminders Style: Green Card
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #34C759 0%, #30B0C7 100%); color: white; border: none;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="width: 38px; height: 38px; border-radius: 50%; background: rgba(255,255,255,0.2); color: white; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                    💰
                </div>
                <div style="font-size: 28px; font-weight: 700; color: white;">
                    {total_income:,.0f}
                </div>
            </div>
            <div style="font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.9); margin-top: 8px;">
                Income
            </div>
            <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 99px; overflow: hidden; margin-top: 12px;">
                <div style="width: {income_pct}%; height: 100%; background: white; border-radius: 99px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Card 2: Budget (Blue)
    with row1_col2:
        # iOS Reminders Style: Blue Card
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%); color: white; border: none;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="width: 38px; height: 38px; border-radius: 50%; background: rgba(255,255,255,0.2); color: white; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                    🎯
                </div>
                <div style="font-size: 28px; font-weight: 700; color: white;">
                    {core_budget_limit:,.0f}
                </div>
            </div>
            <div style="font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.9); margin-top: 8px;">
                Budget
            </div>
            <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 99px; overflow: hidden; margin-top: 12px;">
                <div style="width: 100%; height: 100%; background: white; border-radius: 99px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Card 3: Spent (Red/Orange)
    with row2_col1:
        budget_pct = (core_spent / core_budget_limit * 100) if core_budget_limit > 0 else 0
        if budget_pct >= 100:
            bg_gradient = "linear-gradient(135deg, #FF9500 0%, #FF3B30 100%)" # Red/Orange
        elif budget_pct >= 85:
            bg_gradient = "linear-gradient(135deg, #FFCC00 0%, #FF9500 100%)" # Orange/Yellow
        else:
            bg_gradient = "linear-gradient(135deg, #FFD60A 0%, #FF9F0A 100%)" # Yellow/Orange for spent 
            
        spent_width = min(budget_pct, 100)
        
        # iOS Reminders Style: Orange/Yellow (Warm) Card
        st.markdown(f"""
        <div class="stat-card" style="background: {bg_gradient}; color: white; border: none; margin-top: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="width: 38px; height: 38px; border-radius: 50%; background: rgba(255,255,255,0.2); color: white; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                    💸
                </div>
                <div style="font-size: 28px; font-weight: 700; color: white;">
                    {core_spent:,.0f}
                </div>
            </div>
            <div style="font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.9); margin-top: 8px;">
                Spent
            </div>
            <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 99px; overflow: hidden; margin-top: 12px;">
                <div style="width: {spent_width}%; height: 100%; background: white; border-radius: 99px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Card 4: Remaining (Gray/Blue)
    with row2_col2:
        remaining_amount = core_budget_limit - core_spent
        if remaining_amount < 0:
             bg_gradient = "linear-gradient(135deg, #FF453A 0%, #FF3B30 100%)" # Red for danger
             label = "Over Budget"
             rem_width = 100
        else:
             bg_gradient = "linear-gradient(135deg, #8E8E93 0%, #636366 100%)" # System Gray
             label = "Remaining"
             rem_width = max(0, min((remaining_amount / core_budget_limit * 100), 100)) if core_budget_limit > 0 else 0

        # iOS Reminders Style: Gray Card
        st.markdown(f"""
        <div class="stat-card" style="background: {bg_gradient}; color: white; border: none; margin-top: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="width: 38px; height: 38px; border-radius: 50%; background: rgba(255,255,255,0.2); color: white; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                    📊
                </div>
                <div style="font-size: 28px; font-weight: 700; color: white;">
                    {remaining_amount:,.0f}
                </div>
            </div>
            <div style="font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.9); margin-top: 8px;">
                {label}
            </div>
            <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 99px; overflow: hidden; margin-top: 12px;">
                <div style="width: {rem_width}%; height: 100%; background: white; border-radius: 99px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Surplus Banner
    is_positive = investable_surplus >= 0
    surplus_color = "#34C759" if is_positive else "#FF3B30" # iOS Green / Red
    surplus_icon = "🚀" if is_positive else "⚠️"
    surplus_bg = "#E4F9E9" if is_positive else "#FFEBEA"
    
    st.markdown(f"""
    <div class="stat-card" style="margin-top: 16px; flex-direction: row; align-items: center; justify-content: space-between; background: {surplus_bg}; border: 1px solid {surplus_color}20;">
        <div>
            <div class="stat-label" style="color: {surplus_color}; opacity: 0.9;">Investable Surplus</div>
            <div class="stat-value" style="color: {surplus_color};">৳{investable_surplus:,.0f}</div>
        </div>
        <div style="text-align: right; display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 15px; font-weight: 600; color: {surplus_color};">
                {f'Ready to invest' if is_positive else f'Deficit'}
            </div>
            <div style="font-size: 32px;">{surplus_icon}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Settings button in header area
    st.markdown("""
    <div style="text-align: right; margin-bottom: 1rem;">
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs - including Settings and Live Sheet tab
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["➕ Add Expense", "📊 Dashboard", "📋 History", "🌐 Live Sheet", "⚙️ Budget Config", "⚙️ Settings & Sync"])
    
    with tab1:
        # Get current user from settings for expense form
        current_user, _, _ = get_settings()
        show_expense_form(category_budgets, current_user)
    
    with tab2:
        show_dashboard(current_month_expenses, all_expenses, category_budgets, current_month_income)
    
    with tab3:
        show_history(all_expenses, category_budgets, all_income)
    
    with tab4:
        show_live_sheet(google_script_url)

    with tab5:
        show_budget_config(category_budgets)
    
    with tab6:
        show_settings_page(user, google_script_url, last_synced, category_budgets)

def show_expense_form(category_budgets, current_user):
    st.markdown("""
    <div class="premium-card">
        <h3 style="margin: 0; color: var(--ios-text); font-size: 20px; font-weight: 700;">➕ New Transaction</h3>
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
        <h3 style="margin: 0; color: var(--ios-text); font-size: 20px; font-weight: 700;">📊 Spending Analytics</h3>
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
                
                # Dynamic coloring
                # Dynamic coloring with Gradients
                if percentage >= 100:
                    bar_background = "linear-gradient(90deg, #FF9500 0%, #FF3B30 100%)" 
                    bg_color = "#FFEBEA"
                    text_color = "#FF3B30"
                elif percentage >= 85:
                    bar_background = "linear-gradient(90deg, #FFCC00 0%, #FF9500 100%)"
                    bg_color = "#FFF3D6" 
                    text_color = "#FF9500"
                else:
                    bar_background = "linear-gradient(90deg, #34C759 0%, #30B0C7 100%)"
                    bg_color = "#E4F9E9"
                    text_color = "#34C759"
                
                # Cap progress bar width at 100% for visual sanity
                width_pct = min(percentage, 100)
                
                html_card = f"""
                <div style="background: white; border-bottom: 1px solid #E5E5EA; padding: 12px 4px; margin-bottom: 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.2rem; width: 24px; text-align: center;">{budget.get('icon', '📦')}</span>
                            <span style="font-weight: 600; color: var(--ios-text); font-size: 16px;">{budget['category']}</span>
                        </div>
                        <div style="background: {bg_color}; color: {text_color}; padding: 2px 8px; border-radius: 6px; font-size: 13px; font-weight: 600;">{percentage:.0f}%</div>
                    </div>
                    <div style="width: 100%; height: 10px; background: #E5E5EA; border-radius: 99px; overflow: hidden; margin-bottom: 6px;">
                        <div style="width: {width_pct}%; height: 100%; background: {bar_background}; border-radius: 99px;"></div>
                    </div>
                    <div style="display: flex; justify-content: flex-end; align-items: baseline; gap: 4px;">
                        <span style="font-weight: 600; color: var(--ios-text); font-size: 15px;">৳{spent:,.0f}</span>
                        <span style="color: var(--ios-text-secondary); font-size: 13px;">/ ৳{limit:,.0f}</span>
                    </div>
                </div>"""
                st.markdown(html_card, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Expenses by Category")
        category_data = {}
        for expense in current_month_expenses:
            cat = expense['category']
            category_data[cat] = category_data.get(cat, 0) + expense['amount']
        
        if category_data:
            total_spent = sum(category_data.values())
            df_cat = pd.DataFrame(list(category_data.items()), columns=['Category', 'Amount'])
            fig_pie = px.pie(df_cat, values='Amount', names='Category', 
                           title=None,
                           hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
            # Enhanced Pie Chart with "Cool" Font and Rounded Labels
            fig_pie.update_traces(
                textposition='outside', 
                textinfo='percent+label',
                insidetextorientation='horizontal',
                textfont=dict(family="Arial Black", size=12, color="var(--ios-text)"),
                marker=dict(line=dict(color='#FFFFFF', width=2)),
                pull=[0.05] * len(df_cat) # Slightly pull slices apart
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Arial Black", # Cool font
                margin=dict(l=100, r=100, t=40, b=40),
                showlegend=False,
                annotations=[dict(text=f"Total<br>৳{total_spent:,.0f}", x=0.5, y=0.5, font_size=14, showarrow=False, font=dict(family="Arial Black", color="var(--ios-text)"))] # Center text
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("Spending by Person")
        payer_data = {'Hadi': 0, 'Ruhi': 0}
        for expense in current_month_expenses:
            payer = expense['paid_by']
            payer_data[payer] = payer_data.get(payer, 0) + expense['amount']
        
        df_payer = pd.DataFrame(list(payer_data.items()), columns=['Person', 'Amount'])
        fig_bar = px.bar(df_payer, x='Person', y='Amount', 
                         title="Spending by Person",
                         color='Person',
                         text_auto='.2s',
                         color_discrete_map={'Hadi': '#4F46E5', 'Ruhi': '#10B981'})
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            title_font_size=16,
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Trends chart
    st.subheader("Spending Trends")
    time_frame = st.radio("Time Frame", ["Daily", "Weekly", "Monthly", "Quarterly"], horizontal=True)
    
    # Prepare trend data
    trend_data = prepare_trend_data(all_expenses, time_frame.lower())
    if trend_data:
        df_trend = pd.DataFrame(trend_data, columns=['Period', 'Amount'])
        
        # Forecast for Monthly View
        if time_frame == "Monthly":
            current_month_str = datetime.now().strftime('%Y-%m')
            
            # Find current month data
            current_amount = 0
            for p, a in trend_data:
                if p == current_month_str:
                    current_amount = a
                    break
            
            # Simple Forecast: Daily Avg * Days in Month
            today = datetime.now()
            days_in_month = (today.replace(day=1) + relativedelta(months=1) - timedelta(days=1)).day
            current_day = today.day
            
            if current_day > 0:
                daily_avg = current_amount / current_day
                forecast_amount = daily_avg * days_in_month
                
                # Add forecast data row
                # We want a dotted line from current actual to forecast
                # But creating a separate trace is cleaner
                pass 

        # Create figure with simplified approach
        fig_trend = px.area(df_trend, x='Period', y='Amount', 
                          title=f"Spending Trends ({time_frame})",
                          markers=True)
        
        # Add Spline Smoothing
        fig_trend.update_traces(line_shape='spline', line_color='#6366f1', fillcolor='rgba(99, 102, 241, 0.2)')

        # Add Forecast Trace if Monthly
        if time_frame == "Monthly" and 'forecast_amount' in locals():
            fig_trend.add_scatter(
                x=[current_month_str, current_month_str], 
                y=[current_amount, forecast_amount],
                mode='lines+markers+text',
                line=dict(color='#FF9500', dash='dot', width=2),
                marker=dict(symbol='star', size=10, color='#FF9500'),
                name='Forecast',
                text=[f"", f"Forecast: ৳{forecast_amount:,.0f}"],
                textposition="top center"
            )

        fig_trend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            title_font_size=16,
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
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

def show_history(all_expenses, category_budgets, all_income):
    st.markdown("""
    <div class="premium-card">
        <h3 style="margin: 0; color: var(--text-main);">📋 Transaction History</h3>
    </div>
    """, unsafe_allow_html=True)
    
    tab_expenses, tab_income = st.tabs(["Expenses", "Income"])
    
    with tab_expenses:
        if not all_expenses:
            st.info("No expenses recorded yet.")
        else:
            # Create category icon map
            category_icons = {b['category']: b.get('icon', '📦') for b in category_budgets}
            
            # Get all groups and categories for edit form
            groups = sorted(list(set(b['group_name'] for b in category_budgets)))
            
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
                            # ... (Save button logic remains same but needs 'conn' context if inlined) ...
                            # To keep it clean, I'll provide the full block
                            with col_save:
                                if st.form_submit_button("💾 Save Changes", type="primary"):
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
                                    sync_to_cloud()
                                    st.session_state.editing_expense_id = None
                                    st.success("Expense updated successfully!")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state.editing_expense_id = None
                                    st.rerun()
                else:
                    # Expense List Item
                    with st.container():
                        row_col1, row_col2 = st.columns([5, 1])
                        with row_col1:
                            
                            # Construct HTML manually to ensure no indentation issues
                            notes_html = f'<div style="font-size: 13px; color: var(--ios-text-secondary); margin-top: 4px; margin-left: 42px;">{expense["notes"]}</div>' if expense.get('notes') else ''
                            recurrence_html = ' • 🔄' if expense.get('recurrence_active') else ''
                            
                            html_content = f'''
<div style="background: white; border-bottom: 0.5px solid #C6C6C8; padding: 12px 0;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div style="display: flex; align-items: center; gap: 12px;">
<div style="font-size: 24px; min-width: 30px; text-align: center;">{category_icons.get(expense['category'], '📦')}</div>
<div>
<div style="font-weight: 600; font-size: 16px; color: var(--ios-text);">{expense['item']}</div>
<div style="font-size: 13px; color: var(--ios-text-secondary);">
{expense['category']} • {expense['paid_by']}{recurrence_html}
</div>
</div>
</div>
<div style="text-align: right;">
<div style="font-weight: 600; font-size: 16px; color: var(--ios-text);">-৳{expense['amount']:,.0f}</div>
<div style="font-size: 13px; color: var(--ios-text-secondary);">{expense['date']}</div>
</div>
</div>
{notes_html}
</div>'''
                            st.markdown(html_content, unsafe_allow_html=True)
                        
                        with row_col2:
                            # Action Buttons vertically stacked or side-by-side
                            if st.button("✏️", key=f"edit_btn_{expense_id}", help="Edit"):
                                 st.session_state.editing_expense_id = expense_id
                                 st.rerun()
                            if st.button("🗑️", key=f"delete_btn_{expense_id}", help="Delete"):
                                conn = get_db()
                                c = conn.cursor()
                                c.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
                                conn.commit()
                                conn.close()
                                sync_to_cloud()
                                st.success("Deleted")
                                st.rerun()

    with tab_income:
        if not all_income:
            st.info("No income recorded yet.")
        else:
            if 'editing_income_id' not in st.session_state:
                st.session_state.editing_income_id = None
                
            for income in all_income[:50]:
                income_id = income['id']
                is_editing = st.session_state.editing_income_id == income_id
                
                if is_editing:
                    # Edit Income Form
                    with st.container():
                        st.subheader("✏️ Edit Income")
                        with st.form(f"edit_income_form_{income_id}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_date = st.date_input("Date", value=datetime.strptime(income['date'], '%Y-%m-%d').date(), key=f"edit_inc_date_{income_id}")
                                edit_source = st.text_input("Source", value=income['source'], key=f"edit_inc_source_{income_id}")
                            with col2:
                                edit_amount = st.number_input("Amount (৳)", min_value=0.0, step=10.0, value=float(income['amount']), key=f"edit_inc_amount_{income_id}")
                            
                            edit_notes = st.text_area("Notes", value=income.get('notes', ''), key=f"edit_inc_notes_{income_id}")
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Save Changes", type="primary"):
                                    conn = get_db()
                                    c = conn.cursor()
                                    c.execute('UPDATE income SET date=?, source=?, amount=?, notes=? WHERE id=?',
                                             (edit_date.strftime('%Y-%m-%d'), edit_source, edit_amount, edit_notes, income_id))
                                    conn.commit()
                                    conn.close()
                                    sync_to_cloud()
                                    st.session_state.editing_income_id = None
                                    st.success("Income updated!")
                                    st.rerun()
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state.editing_income_id = None
                                    st.rerun()
                else:
                    # Income List Item
                    with st.container():
                        row_col1, row_col2 = st.columns([5, 1])
                        with row_col1:
                            
                            # Construct HTML manually
                            inc_notes_html = f'<div style="font-size: 13px; color: var(--ios-text-secondary); margin-top: 4px; margin-left: 42px;">{income["notes"]}</div>' if income.get('notes') else ''
                            
                            html_content = f'''
<div style="background: white; border-bottom: 0.5px solid #C6C6C8; padding: 12px 0;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div style="display: flex; align-items: center; gap: 12px;">
<div style="font-size: 24px; min-width: 30px; text-align: center;">💰</div>
<div>
<div style="font-weight: 600; font-size: 16px; color: var(--ios-text);">{income['source']}</div>
<div style="font-size: 13px; color: var(--ios-text-secondary);">{income['date']}</div>
</div>
</div>
<div style="text-align: right;">
<div style="font-weight: 600; font-size: 16px; color: #34C759;">+৳{income['amount']:,.0f}</div>
</div>
</div>
{inc_notes_html}
</div>'''
                            st.markdown(html_content, unsafe_allow_html=True)
                        
                        with row_col2:
                            if st.button("✏️", key=f"edit_inc_btn_{income_id}", help="Edit"):
                                 st.session_state.editing_income_id = income_id
                                 st.rerun()
                            if st.button("🗑️", key=f"delete_inc_btn_{income_id}", help="Delete"):
                                conn = get_db()
                                c = conn.cursor()
                                c.execute('DELETE FROM income WHERE id = ?', (income_id,))
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

def show_live_sheet(google_script_url):
    st.markdown("""
    <div class="premium-card">
        <h3 style="margin: 0; color: var(--text-main);">🌐 Live Family Budget Sheet</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if google_script_url:
        st.info("💡 You may need to sign in to Google to view the sheet below.")
        # Embed the Apps Script web app
        components.iframe(google_script_url, height=800, scrolling=True)
    else:
        st.warning("Google Apps Script URL is not configured. Please go to Settings & Sync to configure it.")

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
