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
    initial_sidebar_state="collapsed"  # Collapsed by default for mobile
)

# iOS-style CSS - Mobile optimized for iPhone
st.markdown("""
<style>
    /* Viewport meta for mobile */
    @media screen {
        html {
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }
    }
    
    /* Global app background */
    .stApp {
        background-color: #F2F2F7;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main content area - Mobile responsive */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        /* Make columns stack on mobile */
        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        
        /* Larger touch targets for mobile */
        .stButton > button {
            min-height: 44px; /* iOS recommended touch target */
            font-size: 16px; /* Prevents zoom on iOS */
            width: 100%;
        }
        
        /* Larger inputs for mobile */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div,
        .stDateInput > div > div > input {
            font-size: 16px; /* Prevents zoom on iOS */
            min-height: 44px;
            padding: 0.875rem 1rem;
        }
        
        /* Tabs - full width on mobile */
        .stTabs [data-baseweb="tab"] {
            flex: 1;
            padding: 0.75rem 0.5rem;
            font-size: 13px;
        }
        
        /* Headers - smaller on mobile */
        h1 {
            font-size: 24px !important;
        }
        
        h2 {
            font-size: 20px !important;
        }
        
        h3 {
            font-size: 18px !important;
        }
        
        /* Metrics cards - stack on mobile */
        [data-testid="stMetricValue"] {
            font-size: 24px;
        }
        
        /* Sidebar - full screen on mobile */
        [data-testid="stSidebar"] {
            min-width: 100% !important;
        }
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Buttons - iOS style with touch targets */
    .stButton > button {
        background-color: #007AFF;
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        min-height: 44px; /* iOS touch target */
        font-size: 16px;
        transition: all 0.2s;
        -webkit-tap-highlight-color: rgba(0,122,255,0.3);
        cursor: pointer;
        touch-action: manipulation;
    }
    
    .stButton > button:hover,
    .stButton > button:active {
        background-color: #0051D5;
        transform: scale(0.98);
    }
    
    /* Inputs - iOS style with larger touch targets */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 1px solid #E5E5EA;
        padding: 0.875rem 1rem;
        font-size: 16px; /* Prevents zoom on iOS */
        min-height: 44px;
        -webkit-appearance: none;
        -webkit-tap-highlight-color: transparent;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #007AFF;
        box-shadow: 0 0 0 3px rgba(0,122,255,0.1);
        outline: none;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        border-radius: 12px;
        font-size: 16px;
        min-height: 44px;
    }
    
    /* Date input */
    .stDateInput > div > div > input {
        border-radius: 12px;
        font-size: 16px;
        min-height: 44px;
    }
    
    /* Radio buttons - larger touch targets */
    .stRadio > div > label {
        padding: 0.75rem;
        min-height: 44px;
        font-size: 16px;
    }
    
    /* Checkboxes - larger touch targets */
    .stCheckbox > label {
        font-size: 16px;
        padding: 0.5rem 0;
        min-height: 44px;
    }
    
    /* Tabs - mobile friendly */
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 14px;
        min-height: 44px;
        touch-action: manipulation;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #007AFF;
        color: white;
    }
    
    /* Sidebar - mobile optimized */
    [data-testid="stSidebar"] {
        background-color: white;
    }
    
    @media (max-width: 768px) {
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            padding: 1rem;
        }
    }
    
    /* Success/Error/Info messages */
    .stSuccess {
        border-radius: 12px;
        border-left: 4px solid #34C759;
        padding: 1rem;
        font-size: 14px;
    }
    
    .stError {
        border-radius: 12px;
        border-left: 4px solid #FF3B30;
        padding: 1rem;
        font-size: 14px;
    }
    
    .stInfo {
        border-radius: 12px;
        border-left: 4px solid #007AFF;
        padding: 1rem;
        font-size: 14px;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        border-radius: 12px;
        font-weight: 600;
        padding: 1rem;
        min-height: 44px;
        font-size: 16px;
    }
    
    /* Dividers */
    hr {
        border-color: #E5E5EA;
        margin: 1.5rem 0;
    }
    
    /* Prevent text selection on buttons (iOS) */
    .stButton > button,
    .stTabs [data-baseweb="tab"] {
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }
    
    /* Smooth scrolling for mobile */
    html {
        -webkit-overflow-scrolling: touch;
        scroll-behavior: smooth;
    }
    
    /* Fix for iOS Safari viewport */
    @supports (-webkit-touch-callout: none) {
        .main .block-container {
            min-height: -webkit-fill-available;
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
    
    # Get settings
    user, google_script_url, last_synced = get_settings()
    
    conn.close()
    
    # Calculate totals
    total_budget_limit = sum(b['limit_amount'] for b in category_budgets)
    total_spent = sum(e['amount'] for e in current_month_expenses)
    remaining = total_budget_limit - total_spent
    
    # iOS-style Header with Settings Button
    col_header1, col_header2 = st.columns([4, 1])
    
    with col_header1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem 1.5rem; 
                    border-radius: 16px; 
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    position: relative;">
            <h1 style="color: white; 
                       font-size: 32px; 
                       font-weight: 700; 
                       margin: 0 0 0.5rem 0;
                       letter-spacing: -1px;">💰 Family Budget Tracker</h1>
            <p style="color: rgba(255,255,255,0.9); 
                      font-size: 14px; 
                      margin: 0;
                      font-weight: 500;">{current_month} {current_year}{' • Hi, ' + user + '!' if user else ''}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_header2:
        st.markdown("""
        <div style="padding-top: 2rem;">
        </div>
        """, unsafe_allow_html=True)
        
        # Settings button that opens sidebar
        if st.button("⚙️ Settings", use_container_width=True, type="secondary"):
            # Note: Streamlit doesn't allow programmatic sidebar control,
            # but this button makes it clear where settings are
            st.info("💡 Open the sidebar (☰) to access Settings & Sync")
        
        # Show sync status if URL is configured
        if google_script_url:
            if last_synced:
                st.caption(f"🔄 Synced: {last_synced[11:16]}")
            else:
                st.caption("🔄 Not synced")
        else:
            st.caption("☁️ No sync URL")
    
    # Sidebar for settings
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="font-size: 20px; font-weight: 700; margin: 0 0 1.5rem 0;">⚙️ Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # User selection
        st.markdown("### 👤 User Profile")
        selected_user = st.radio(
            "Select User",
            ["Hadi", "Ruhi"],
            index=0 if user == "Hadi" else (1 if user == "Ruhi" else 0),
            key="user_select",
            horizontal=True
        )
        
        if user:
            st.info(f"✓ Currently logged in as **{user}**")
        
        if selected_user != user:
            save_setting('user', selected_user)
            st.rerun()
        
        st.divider()
        
        # Cloud Sync Section
        st.markdown("### ☁️ Google Sheets Sync")
        st.markdown("**Connect to Google Sheets:**")
        
        sync_url = st.text_input(
            "Google Apps Script URL",
            value=google_script_url,
            placeholder="https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec",
            key="sync_url",
            help="Deploy your Google Apps Script as a web app and paste the URL here"
        )
        
        col_save, col_sync = st.columns(2)
        with col_save:
            if sync_url != google_script_url:
                if st.button("💾 Save URL", use_container_width=True):
                    save_setting('googleScriptUrl', sync_url)
                    st.success("URL saved!")
                    st.rerun()
            elif sync_url:
                st.success("✓ URL saved")
        
        with col_sync:
            if sync_url:
                if st.button("🔄 Sync Now", use_container_width=True):
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
    
    # iOS-style Metrics with custom colors
    st.markdown("""
    <style>
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #8E8E93;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .metric-budget {
        color: #FF9500;
    }
    .metric-spent {
        color: #FF3B30;
    }
    .metric-remaining {
        color: #34C759;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Budget</div>
            <div class="metric-value metric-budget">৳{total_budget_limit:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        expense_count = len(current_month_expenses)
        expense_text = f"<div style='font-size: 11px; color: #8E8E93; margin-top: 4px;'>{expense_count} expense{'s' if expense_count != 1 else ''}</div>" if expense_count > 0 else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Spent</div>
            <div class="metric-value metric-spent">৳{total_spent:,.0f}</div>
            {expense_text}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        remaining_color = "#34C759" if remaining >= 0 else "#FF3B30"
        remaining_class = "metric-remaining" if remaining >= 0 else "metric-spent"
        over_budget_text = f"<div style='font-size: 11px; color: #FF3B30; margin-top: 4px;'>Over by ৳{abs(remaining):,.0f}</div>" if remaining < 0 else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Remaining</div>
            <div class="metric-value {remaining_class}" style="color: {remaining_color};">৳{remaining:,.0f}</div>
            {over_budget_text}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Expense", "📊 Dashboard", "📋 History", "⚙️ Budget Config"])
    
    with tab1:
        show_expense_form(category_budgets, selected_user)
    
    with tab2:
        show_dashboard(current_month_expenses, all_expenses, category_budgets)
    
    with tab3:
        show_history(all_expenses, category_budgets)
    
    with tab4:
        show_budget_config(category_budgets)

def show_expense_form(category_budgets, current_user):
    st.markdown("""
    <div style="background: white; 
                padding: 1.5rem; 
                border-radius: 16px; 
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h2 style="margin: 0 0 1rem 0; font-size: 24px; font-weight: 700;">➕ Add New Expense</h2>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    with st.form("expense_form"):
        # Responsive columns - stack on mobile
        col1, col2 = st.columns([1, 1])
        
        with col1:
            expense_date = st.date_input("Date", value=datetime.now())
            expense_item = st.text_input("Item", placeholder="What did you buy?")
        
        with col2:
            expense_amount = st.number_input("Amount (৳)", min_value=0.0, step=0.01, format="%.2f")
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
        
        notes = st.text_area("Notes (optional)")
        
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
                
                st.success(f"Expense added successfully! (৳{expense_amount:,.0f} on {expense_date_str})")
                # Force rerun to refresh the page
                st.rerun()
            else:
                error_msg = "Please fill in all required fields: "
                if not expense_item:
                    error_msg += "Item, "
                if expense_amount <= 0:
                    error_msg += "Amount > 0, "
                if not selected_category:
                    error_msg += "Category"
                st.error(error_msg.rstrip(", "))

def show_dashboard(current_month_expenses, all_expenses, category_budgets):
    st.markdown("""
    <div style="background: white; 
                padding: 1.5rem; 
                border-radius: 16px; 
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h2 style="margin: 0; font-size: 24px; font-weight: 700;">📊 Dashboard</h2>
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
        fig_bar = px.bar(df_payer, x='Person', y='Amount', 
                        title="Spending by Person",
                        color='Person',
                        color_discrete_map={'Hadi': '#007AFF', 'Ruhi': '#34C759'})
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
    <div style="background: white; 
                padding: 1.5rem; 
                border-radius: 16px; 
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h2 style="margin: 0; font-size: 24px; font-weight: 700;">📋 Expense History</h2>
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
            # Display expense
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                with col1:
                    st.write(f"**{expense['item']}**")
                    st.caption(f"{category_icons.get(expense['category'], '📦')} {expense['category']} • {expense['paid_by']}")
                with col2:
                    st.caption(expense['date'])
                    if expense.get('notes'):
                        st.caption(f"💬 {expense['notes']}")
                with col3:
                    st.write(f"**৳{expense['amount']:,.0f}**")
                with col4:
                    if expense.get('recurrence_active'):
                        st.badge("🔄", type="info")
                with col5:
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button("✏️", key=f"edit_btn_{expense_id}", help="Edit"):
                            st.session_state.editing_expense_id = expense_id
                            st.rerun()
                    with col_delete:
                        if st.button("🗑️", key=f"delete_btn_{expense_id}", help="Delete"):
                            # Delete expense
                            conn = get_db()
                            c = conn.cursor()
                            c.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
                            conn.commit()
                            conn.close()
                            
                            # Sync to cloud
                            sync_to_cloud()
                            
                            st.success("Expense deleted successfully!")
                            st.rerun()
                
                st.divider()

def show_budget_config(category_budgets):
    st.markdown("""
    <div style="background: white; 
                padding: 1.5rem; 
                border-radius: 16px; 
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
        <h2 style="margin: 0 0 1rem 0; font-size: 24px; font-weight: 700;">⚙️ Budget Configuration</h2>
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
    
    current_month = datetime.now().strftime('%B')
    
    payload = {
        'expenses': expenses,
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
