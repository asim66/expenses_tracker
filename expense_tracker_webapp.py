import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

DB_FILE = "expenses.db"

# --- Database Setup ---
conn = sqlite3.connect(DB_FILE, check_same_thread=False)  # allows multi-user
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT,
    Vendor TEXT,
    Category TEXT,
    Expense REAL,
    Payment REAL,
    Status TEXT,
    Notes TEXT
)
""")
conn.commit()

# --- Helper Functions ---
def add_entry(date, vendor, category, expense, payment, status, notes):
    cursor.execute(
        "INSERT INTO expenses (Date, Vendor, Category, Expense, Payment, Status, Notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(date), vendor, category, expense, payment, status, notes),
    )
    conn.commit()

def load_data():
    return pd.read_sql("SELECT * FROM expenses", conn)

# --- Streamlit UI ---
st.title("🏗️ Interior Project Expense Tracker")
st.subheader("📊 Track your expenses, client payments & profit/loss (multi-user ready)")

# --- Data Entry Form ---
with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date")
        vendor = st.text_input("Vendor Name")
        category = st.text_input("Expense Category")
        expense = st.number_input("Expense Amount (₹)", min_value=0, step=100)
    with col2:
        client_payment = st.number_input("Client Payment Amount (₹)", min_value=0, step=100)
        payment_status = st.selectbox("Payment Status", ["Pending", "Received"])
        notes = st.text_area("Notes")

    submitted = st.form_submit_button("Add Entry")
    if submitted:
        add_entry(date, vendor, category, expense, client_payment, payment_status, notes)
        st.success("✅ Entry added successfully!")

# --- Load Data from DB ---
df = load_data()

st.subheader("📋 Project Records")
st.dataframe(df, use_container_width=True)

# --- Summary ---
if not df.empty:
    total_expenses = df["Expense"].sum()
    total_payments = df["Payment"].sum()
    profit_loss = total_payments - total_expenses

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses (₹)", f"{total_expenses:,.0f}")
    col2.metric("Total Client Payments (₹)", f"{total_payments:,.0f}")
    col3.metric("Net Profit/Loss (₹)", f"{profit_loss:,.0f}")

    # --- Charts ---
    st.subheader("📊 Visual Analysis")

    # Bar chart: Payments vs Expenses
    fig, ax = plt.subplots()
    ax.bar(["Expenses", "Payments"], [total_expenses, total_payments], color=["red", "green"])
    ax.set_ylabel("Amount (₹)")
    st.pyplot(fig)

    # Pie chart: Expense distribution
    if df["Expense"].sum() > 0:
        fig2, ax2 = plt.subplots()
        exp_by_cat = df.groupby("Category")["Expense"].sum()
        ax2.pie(exp_by_cat, labels=exp_by_cat.index, autopct="%1.1f%%")
        ax2.set_title("Expense Distribution")
        st.pyplot(fig2)

# --- Export Option ---
st.download_button(
    label="💾 Download Data as Excel",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="project_expenses.csv",
    mime="text/csv",
)
