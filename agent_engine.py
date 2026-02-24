import os
import json
import uuid
import requests
from datetime import datetime
import google.generativeai as genai

# Configuration (Reusing Supabase config from secrets if possible)
# Note: For local script use, we might need a way to load these without streamlit
# We will try to load from .streamlit/secrets.toml manually
def load_secrets():
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
             # tomllib is standard in Python 3.11+
             import tomllib
        except ImportError:
             import toml as tomllib
             
        with open(secrets_path, "rb") as f:
            return tomllib.load(f)
    return {}

SECRETS = load_secrets()
SUPABASE_URL = SECRETS.get("supabase", {}).get("url")
SUPABASE_KEY = SECRETS.get("supabase", {}).get("api_key")
GEMINI_API_KEY = SECRETS.get("gemini", {}).get("api_key") or os.environ.get("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found in secrets.toml")

# Supabase Helpers
def supabase_request(method, table, data=None, params=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    try:
        response = requests.request(method, url, json=data, params=params, headers=headers, timeout=10)
        return response.json() if response.status_code < 400 else {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def fetch_categories():
    categories = supabase_request("GET", "category_budgets", params={"select": "category,group_name"})
    if isinstance(categories, list):
        return [f"{c['category']} ({c['group_name']})" for c in categories]
    return []

# Agent Tools
def log_expense(item: str, amount: float, category: str, paid_by: str = "Hadi", notes: str = ""):
    """Logs an expense to the database."""
    expense_data = {
        "id": str(uuid.uuid4()),
        "date": datetime.now().strftime('%Y-%m-%d'),
        "item": item,
        "amount": amount,
        "category": category,
        "paid_by": paid_by,
        "notes": notes
    }
    return supabase_request("POST", "expenses", data=expense_data)

def log_income(source: str, amount: float, notes: str = ""):
    """Logs income to the database."""
    income_data = {
        "id": str(uuid.uuid4()),
        "date": datetime.now().strftime('%Y-%m-%d'),
        "source": source,
        "amount": amount,
        "notes": notes
    }
    return supabase_request("POST", "income", data=income_data)

# AI Engine
def process_message(text: str):
    if not GEMINI_API_KEY:
        return "Error: Gemini API Key missing. Please add it to .streamlit/secrets.toml under [gemini]"

    genai.configure(api_key=GEMINI_API_KEY)
    
    # Get available categories for context
    cats = fetch_categories()
    categories_str = ", ".join(cats)
    
    prompt = f"""
    You are a helpful Family Budget Assistant. Your job is to extract financial transactions from text.
    
    Current Categories available: {categories_str}
    
    Rules:
    1. If the user mentions spending money, use 'log_expense'.
    2. Try to match the category to the most relevant one from the list. If it doesn't fit, use 'Others'.
    3. If the user mentions receiving money, use 'log_income'.
    4. Default 'paid_by' to 'Hadi' unless 'Ruhi' is mentioned.
    5. Be concise and confirm the action.
    
    Text: "{text}"
    """
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest',
        tools=[log_expense, log_income]
    )
    
    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(prompt)
    
    return response.text

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(f"Processing: {user_input}")
        result = process_message(user_input)
        print(f"Result: {result}")
    else:
        print("Usage: python agent_engine.py 'Your message here'")
