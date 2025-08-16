import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- File persistence ---
DATA_FILE = "project_expenses.csv"

# Load data if file exists, else create empty DataFrame
if "data" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.data = pd.read_csv(DATA_FILE)
    else:
        st.session_state.data = pd.DataFrame(
            columns=["Date", "Vendor Name", "Expense Category", "Expense Amount (₹)",
                     "Client Payment Amount (₹)", "Payment Status", "Notes"]
        )

st.title("🏗️ Interior Project Expense Tracker")

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
        new_row = {
            "Date": str(date),
            "Vendor Name": vendor,
            "Expense Category": category,
            "Expense Amount (₹)": expense,
            "Client Payment Amount (₹)": client_payment,
            "Payment Status": payment_status,
            "Notes": notes,
        }
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([new_row])], ignore_index=True
        )

        # ✅ Save to file after every new entry
        st.session_state.data.to_csv(DATA_FILE, index=False)

        st.success("Entry added successfully and saved!")

# --- Display Data ---
st.subheader("📋 Project Records")
st.dataframe(st.session_state.data, use_container_width=True)

# --- Summary ---
if not st.session_state.data.empty:
    total_expenses = st.session_state.data["Expense Amount (₹)"].sum()
    total_payments = st.session_state.data["Client Payment Amount (₹)"].sum()
    profit_loss = total_payments - total_expenses

    st.metric("Total Expenses (₹)", f"{total_expenses:,.0f}")
    st.metric("Total Client Payments (₹)", f"{total_payments:,.0f}")
    st.metric("Net Profit/Loss (₹)", f"{profit_loss:,.0f}")

    # --- Charts ---
    st.subheader("📊 Visual Analysis")

    # Bar chart: Payments vs Expenses
    fig, ax = plt.subplots()
    ax.bar(["Expenses", "Payments"], [total_expenses, total_payments], color=["red", "green"])
    ax.set_ylabel("Amount (₹)")
    st.pyplot(fig)

    # Pie chart: Expense distribution
    if st.session_state.data["Expense Amount (₹)"].sum() > 0:
        fig2, ax2 = plt.subplots()
        exp_by_cat = st.session_state.data.groupby("Expense Category")["Expense Amount (₹)"].sum()
        ax2.pie(exp_by_cat, labels=exp_by_cat.index, autopct="%1.1f%%")
        ax2.set_title("Expense Distribution")
        st.pyplot(fig2)

# --- Export Option ---
st.download_button(
    label="💾 Download Data as Excel",
    data=st.session_state.data.to_csv(index=False).encode("utf-8"),
    file_name="project_expenses.csv",
    mime="text/csv",
)
