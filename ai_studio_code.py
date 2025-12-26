import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from streamlit_extras.metric_cards import style_metric_cards

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Family Budget Tracker",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (iOS Style) ---
st.markdown("""
    <style>
        /* Remove top padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
        }
        
        /* iOS Card Styling */
        div[data-testid="stMetric"], div[data-testid="stExpander"] {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }

        /* iOS Button Styling */
        .stButton > button {
            width: 100%;
            background-color: #007AFF;
            color: white;
            font-weight: 600;
            border-radius: 12px;
            border: none;
            padding: 0.75rem 1rem;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            background-color: #005ecb;
            color: white;
            border: none;
        }
        .stButton > button:active {
            transform: scale(0.98);
        }

        /* Input Styling */
        .stTextInput > div > div, .stSelectbox > div > div, .stDateInput > div > div, .stNumberInput > div > div {
            border-radius: 10px;
            border-color: #E5E5EA;
            background-color: #F2F2F7;
            color: #1c1c1e;
        }
        
        /* Hide deploy button */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- DATA CONNECTION ---
# Note: You must set up .streamlit/secrets.toml with your Google Sheet URL
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Load Budgets (Category Definitions)
    try:
        df_budgets = conn.read(worksheet="Budgets", ttl=0)
    except:
        # Fallback if sheet is empty or doesn't exist yet
        df_budgets = pd.DataFrame(columns=["Category", "Sub_Category", "Monthly_Limit"])

    # Load Expenses
    try:
        df_expenses = conn.read(worksheet="Expenses", ttl=0)
        # Ensure date column is datetime
        if not df_expenses.empty:
            df_expenses['Date'] = pd.to_datetime(df_expenses['Date'])
    except:
        df_expenses = pd.DataFrame(columns=["Date", "Item", "Category", "Sub_Category", "Amount", "Paid_By"])
    
    return df_budgets, df_expenses

def save_expense(new_entry, current_df):
    try:
        # Append new row
        updated_df = pd.concat([current_df, pd.DataFrame([new_entry])], ignore_index=True)
        # Sort by date descending
        updated_df = updated_df.sort_values(by="Date", ascending=False)
        # Update Google Sheet
        conn.update(worksheet="Expenses", data=updated_df)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# --- LOAD DATA ---
df_budgets, df_expenses = load_data()

# --- HEADER ---
st.title("💸 Family Budget")
st.write(f"Overview for {datetime.now().strftime('%B %Y')}")

# --- TABS ---
tab1, tab2 = st.tabs(["📝 Log Expense", "📊 Dashboard"])

# ==========================
# TAB 1: LOG EXPENSE
# ==========================
with tab1:
    st.markdown("### New Transaction")
    
    # Check if budgets exist
    if df_budgets.empty:
        st.warning("Please configure your 'Budgets' sheet in Google Sheets first (Columns: Category, Sub_Category, Monthly_Limit).")
    else:
        # 1. Date & Item
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date", datetime.now())
        with col2:
            item_input = st.text_input("Item Description", placeholder="e.g. Grocery")

        # 2. Dynamic Categories
        # Get unique Categories (Groups)
        categories = df_budgets['Category'].unique().tolist()
        
        # Select Category
        selected_category = st.selectbox("Category Group", options=categories, index=0 if categories else None)
        
        # Filter Sub-Categories based on selection
        if selected_category:
            sub_categories = df_budgets[df_budgets['Category'] == selected_category]['Sub_Category'].tolist()
        else:
            sub_categories = []
            
        selected_sub_category = st.selectbox("Sub-Category", options=sub_categories)

        # 3. Amount & Payer
        col3, col4 = st.columns(2)
        with col3:
            amount_input = st.number_input("Amount (৳)", min_value=0.0, step=10.0, format="%.2f")
        with col4:
            payer_input = st.selectbox("Paid By", ["Hadi", "Ruhi"], index=0)

        # 4. Submit Button
        if st.button("Add Expense"):
            if not item_input:
                st.error("Please enter an item description.")
            elif amount_input <= 0:
                st.error("Amount must be greater than 0.")
            elif not selected_category or not selected_sub_category:
                st.error("Please select a valid category.")
            else:
                new_entry = {
                    "Date": date_input.strftime("%Y-%m-%d"),
                    "Item": item_input,
                    "Category": selected_category,
                    "Sub_Category": selected_sub_category,
                    "Amount": amount_input,
                    "Paid_By": payer_input
                }
                
                with st.spinner("Saving to Cloud..."):
                    if save_expense(new_entry, df_expenses):
                        st.success("Expense added successfully!")
                        st.balloons()
                        # Force refresh to clear inputs (Streamlit trick)
                        # st.rerun() # Uncomment for immediate reload, though it clears the success message quickly

# ==========================
# TAB 2: DASHBOARD
# ==========================
with tab2:
    if df_expenses.empty or df_budgets.empty:
        st.info("No data available yet. Start logging expenses!")
    else:
        # --- DATA PROCESSING ---
        # Filter for current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        df_expenses['Date_Dt'] = pd.to_datetime(df_expenses['Date'])
        mask = (df_expenses['Date_Dt'].dt.month == current_month) & (df_expenses['Date_Dt'].dt.year == current_year)
        monthly_expenses = df_expenses.loc[mask]

        # Aggregate Actual Spending
        total_spent = monthly_expenses['Amount'].sum()
        
        # Aggregate Budget Limits
        total_budget = df_budgets['Monthly_Limit'].sum()
        remaining = total_budget - total_spent

        # --- TOP METRICS ---
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Budget", f"৳{total_budget:,.0f}")
        col_m2.metric("Spent", f"৳{total_spent:,.0f}")
        col_m3.metric("Remaining", f"৳{remaining:,.0f}", delta_color="normal" if remaining > 0 else "inverse")
        
        # Apply fancy card styling
        style_metric_cards(background_color="#FFFFFF", border_left_color="#007AFF", border_radius_px=12, box_shadow=True)

        st.divider()

        # --- CHARTS ---
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("##### 🥧 By Category Group")
            if not monthly_expenses.empty:
                pie_data = monthly_expenses.groupby('Category')['Amount'].sum().reset_index()
                fig_pie = px.pie(pie_data, values='Amount', names='Category', hole=0.4)
                fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, showlegend=False)
                st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            st.markdown("##### 💳 Spending by Person")
            if not monthly_expenses.empty:
                bar_data = monthly_expenses.groupby('Paid_By')['Amount'].sum().reset_index()
                fig_bar = px.bar(bar_data, x='Paid_By', y='Amount', color='Paid_By', text_auto='.2s')
                fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, xaxis_title=None, showlegend=False)
                fig_bar.update_traces(textposition='outside')
                st.plotly_chart(fig_bar, use_container_width=True)

        # --- CATEGORY BREAKDOWN LIST ---
        st.markdown("##### 📊 Detailed Breakdown")
        
        # Merge Expenses with Budgets
        spent_by_sub = monthly_expenses.groupby('Sub_Category')['Amount'].sum().reset_index()
        merged_df = pd.merge(df_budgets, spent_by_sub, on='Sub_Category', how='left').fillna(0)
        merged_df['Percent'] = (merged_df['Amount'] / merged_df['Monthly_Limit']) * 100
        
        # Display as a clean list with progress bars
        for index, row in merged_df.iterrows():
            with st.container():
                c_name, c_amt = st.columns([3, 1])
                c_name.write(f"**{row['Sub_Category']}** ({row['Category']})")
                c_amt.write(f"৳{row['Amount']:,.0f} / {row['Monthly_Limit']:,.0f}")
                
                # Custom Progress Bar logic
                pct = min(row['Percent'] / 100, 1.0)
                color = "green"
                if pct > 0.9: color = "red"
                elif pct > 0.75: color = "orange"
                
                st.progress(pct, text=None)
                st.write("") # Spacer

        # --- RECENT HISTORY ---
        st.markdown("##### 🕒 Recent Transactions")
        st.dataframe(
            monthly_expenses[['Date', 'Item', 'Sub_Category', 'Amount', 'Paid_By']].head(5),
            hide_index=True,
            use_container_width=True
        )