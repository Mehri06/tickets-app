import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

st.set_page_config(page_title="IT Ticket Log", page_icon="🧰", layout="wide")

# Detect submit-only public mode
gp = st.query_params
mode = (gp.get("mode") or "").lower()
submit_only = (mode == "submit")

DATA_FILE = "tickets.csv"
DEFAULT_CAP = 8
COLUMNS = ["Ticket ID","Date Opened","Employee Name","Issue","Date Finished","Status","Notes"]

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(DATA_FILE)
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = None
    for dc in ["Date Opened","Date Finished"]:
        if dc in df.columns:
            df[dc] = pd.to_datetime(df[dc], errors="coerce").dt.date
    return df[COLUMNS]

def save_data(df):
    df_copy = df.copy()
    for dc in ["Date Opened","Date Finished"]:
        if dc in df_copy.columns:
            df_copy[dc] = pd.to_datetime(df_copy[dc], errors="coerce").dt.strftime("%Y-%m-%d")
    df_copy.to_csv(DATA_FILE, index=False)

def generate_ticket_id():
    return datetime.now().strftime("T%Y%m%d%H%M%S%f")

# Public submit-only page
if submit_only:
    st.title("📝 Submit a Ticket")
    st.caption("Public submission page — your ticket will be logged.")
    with st.form("public_submit"):
        employee = st.text_input("Your Name")
        issue = st.text_area("Describe the issue", height=140)
        date_opened = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Submit")
        if submitted:
            df = load_data()
            tid = generate_ticket_id()
            new_row = {
                "Ticket ID": tid,
                "Date Opened": date_opened,
                "Employee Name": (employee or "").strip(),
                "Issue": (issue or "").strip(),
                "Date Finished": None,
                "Status": "Open",
                "Notes": "",
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("Thanks! Your ticket was submitted.")
            st.balloons()
    st.stop()

st.sidebar.title("Settings")
monthly_cap = st.sidebar.number_input("Monthly Cap (tickets)", min_value=1, value=DEFAULT_CAP, step=1)
st.sidebar.info("Use '?mode=submit' in the URL to open the public submission page.")

st.title("🧰 IT Ticket Log")
df = load_data()

tab_add, tab_table, tab_sum = st.tabs(["➕ Add Ticket", "📋 Tickets Table", "📈 Summary"])

with tab_add:
    st.subheader("Add a new ticket")
    with st.form("add_ticket"):
        col1, col2 = st.columns(2)
        with col1:
            date_opened = st.date_input("Date Opened", value=date.today())
            employee = st.text_input("Employee Name")
            status = st.selectbox("Status", ["Open","Closed"])
        with col2:
            issue = st.text_area("Issue", height=120)
            date_finished = st.date_input("Date Finished", value=None, help="Optional", key="df_picker")
            notes = st.text_area("Notes", height=120)
        submitted = st.form_submit_button("Add Ticket")
        if submitted:
            tid = generate_ticket_id()
            new_row = {
                "Ticket ID": tid,
                "Date Opened": date_opened,
                "Employee Name": employee.strip(),
                "Issue": issue.strip(),
                "Date Finished": date_finished,
                "Status": status,
                "Notes": notes.strip(),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"Ticket added with ID {tid}")

with tab_table:
    st.subheader("View / Edit tickets")
    if df.empty:
        st.info("No tickets yet. Add your first ticket in the 'Add Ticket' tab.")
    else:
        edited = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="editor",
        )
        colA, colB = st.columns([1,1])
        with colA:
            if st.button("💾 Save changes"):
                save_data(edited)
                st.success("Saved changes.")
        with colB:
            st.write("")
            st.write("")
            to_delete_ids = st.multiselect("Select Ticket ID(s) to delete:", options=edited["Ticket ID"].tolist())
            if st.button("🗑️ Delete selected"):
                if to_delete_ids:
                    remaining = edited[~edited["Ticket ID"].isin(to_delete_ids)].copy()
                    save_data(remaining)
                    st.success(f"Deleted {len(to_delete_ids)} ticket(s). Refresh to see updates.")
                else:
                    st.warning("No Ticket ID selected.")
        st.download_button("⬇️ Download CSV", data=edited.to_csv(index=False), file_name="tickets_export.csv", mime="text/csv")

with tab_sum:
    st.subheader("Monthly Summary")
    if df.empty:
        st.info("No data to summarize yet.")
    else:
        dfx = df.copy()
        dfx["Date Opened"] = pd.to_datetime(dfx["Date Opened"], errors="coerce")
        dfx = dfx.dropna(subset=["Date Opened"])
        if dfx.empty:
            st.info("No valid 'Date Opened' values to summarize.")
        else:
            dfx["month"] = dfx["Date Opened"].dt.to_period("M").astype(str)
            summary = dfx.groupby("month").size().reset_index(name="Tickets")
            summary["Cap"] = monthly_cap
            summary["Extra Tickets"] = (summary["Tickets"] - monthly_cap).clip(lower=0)
            st.dataframe(summary, use_container_width=True)
            st.bar_chart(summary.set_index("month")["Tickets"])
            over = summary[summary["Tickets"] > monthly_cap]
            if not over.empty:
                months = ", ".join(over["month"].tolist())
                st.warning(f"Cap exceeded in: {months}")
            else:
                st.success("All months are within the cap.")
st.caption("Data file: tickets.csv — keep a backup if this is important for payroll.")
