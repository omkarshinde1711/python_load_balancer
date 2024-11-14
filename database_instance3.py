import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Unique instance identifier (replace this value for each instance manually or use arguments)
# INSTANCE_ID = "Database Server - Instance 1"  # For instance 1
# INSTANCE_ID = "Database Server - Instance 2"  # For instance 2
INSTANCE_ID = "Database Server - Instance 3"  # For instance 3

# Streamlit UI for the database server instance
st.title(INSTANCE_ID)
st.write("This is a dedicated database server instance.")

# Add the missing database functions
def init_db():
    conn = sqlite3.connect('shared_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS entries
                 (name TEXT, age INTEGER, timestamp TEXT, instance_id TEXT)''')
    conn.commit()
    conn.close()

def add_entry(name, age, instance_id):
    conn = sqlite3.connect('shared_database.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO entries VALUES (?, ?, ?, ?)", 
             (name, age, timestamp, instance_id))
    conn.commit()
    conn.close()

def get_all_entries():
    conn = sqlite3.connect('shared_database.db')
    df = pd.read_sql_query("SELECT * FROM entries", conn)
    conn.close()
    return df

# Initialize database
init_db()

# Simulate a simple database entry form
with st.form("database_entry_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0)
    submitted = st.form_submit_button("Submit")

    if submitted:
        add_entry(name, age, INSTANCE_ID)
        st.success(f"Data submitted to {INSTANCE_ID}.")

# Add metrics section
entries = get_all_entries()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Entries", len(entries))
with col2:
    avg_age = entries['age'].mean() if not entries.empty else 0
    st.metric("Average Age", f"{avg_age:.1f}")
with col3:
    entries_from_this_instance = len(entries[entries['instance_id'] == INSTANCE_ID])
    st.metric("Entries from this Instance", entries_from_this_instance)

# Display all entries
st.subheader("All Database Entries")
if not entries.empty:
    st.dataframe(entries)
else:
    st.info("No entries in the database yet.")
