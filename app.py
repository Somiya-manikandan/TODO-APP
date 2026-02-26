import streamlit as st
import sqlite3
from datetime import date

# ---------- DATABASE ---------- #

conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT,
    priority TEXT,
    due_date TEXT,
    status TEXT
)
""")

conn.commit()

# ---------- PASTEL GREEN THEME ---------- #

st.markdown("""
    <style>
    .stApp {
        background-color: #E8F5E9;
    }
    div.stButton > button {
        background-color: #A5D6A7;
        color: black;
        border-radius: 10px;
        height: 3em;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Smart To-Do App")

# ---------- SESSION ---------- #

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------- LOGIN PAGE ---------- #

if st.session_state.user_id is None:

    st.subheader("🔐 Login / Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            cursor.execute(
                "SELECT id FROM users WHERE username=? AND password=?",
                (username, password)
            )
            user = cursor.fetchone()

            if user:
                st.session_state.user_id = user[0]
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        if st.button("Register"):
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()
                st.success("User Registered!")
            except:
                st.error("Username already exists")

# ---------- TODO PAGE ---------- #

else:
    st.success("Logged in successfully!")

    if st.button("🚪 Logout"):
        st.session_state.user_id = None
        st.rerun()

    st.subheader("➕ Add New Task")

    task = st.text_input("Task")
    priority = st.selectbox("Priority", ["High 🔴", "Medium 🟡", "Low 🟢"])
    due_date = st.date_input("Due Date", date.today())

    if st.button("Add Task"):
        if task:
            cursor.execute("""
                INSERT INTO tasks (user_id, task, priority, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (st.session_state.user_id, task, priority, str(due_date), "Pending"))
            conn.commit()
            st.success("Task Added!")
            st.rerun()
        else:
            st.warning("Enter a task")

    st.subheader("📋 My Tasks")

    cursor.execute("""
        SELECT id, task, priority, due_date, status
        FROM tasks WHERE user_id=?
    """, (st.session_state.user_id,))
    tasks = cursor.fetchall()

    for task in tasks:
        col1, col2, col3 = st.columns([4,1,1])
        with col1:
            st.write(f"{task[1]} | {task[2]} | 📅 {task[3]} | {task[4]}")
        with col2:
            if st.button("✔", key=f"done{task[0]}"):
                cursor.execute(
                    "UPDATE tasks SET status='Completed ✔' WHERE id=?",
                    (task[0],)
                )
                conn.commit()
                st.rerun()
        with col3:
            if st.button("🗑", key=f"del{task[0]}"):
                cursor.execute(
                    "DELETE FROM tasks WHERE id=?",
                    (task[0],)
                )
                conn.commit()
                st.rerun()