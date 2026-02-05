import streamlit as st
import json, os, csv
from datetime import date, datetime
import time
import random
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Well-Being for All",
    page_icon="💙",
    layout="wide"
)

DATA_FILE = "wellbeing_data.json"

QUOTES = [
    "Small steps every day lead to big change.",
    "Your well-being matters.",
    "It’s okay to ask for help.",
    "Healthy mind, healthy body.",
    "Be kind to yourself today."
]

CHALLENGES = [
    "Drink 6–8 glasses of water",
    "Take a 10-minute walk",
    "Write one thing you are grateful for",
    "Stretch for 5 minutes",
    "Talk to someone you trust"
]

# ---------------- DATA ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "users": {},
            "gratitude_wall": [],
            "total_revenue": 0
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- AUTH ----------------
def auth_page():
    st.title("💙 Well-Being for All")
    st.caption("Student Wellness & Social Enterprise App")

    mode = st.radio("Choose", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if mode == "Sign Up":
        confirm = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["Student", "Teacher"])

        if st.button("Create Account"):
            if username in data["users"]:
                st.error("User already exists")
            elif password != confirm:
                st.error("Passwords do not match")
            else:
                data["users"][username] = {
                    "password": password,
                    "role": role,
                    "moods": [],
                    "journal": [],
                    "habits": {},
                    "challenges": {},
                    "suggestions": [],
                    "score": 0
                }
                save_data(data)
                st.success("Account created. Please login.")

    else:
        if st.button("Login"):
            if username in data["users"] and data["users"][username]["password"] == password:
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------------- DASHBOARD ----------------
def dashboard(user):
    st.header(f"👋 Welcome, {user}")

    col1, col2, col3 = st.columns(3)

    col1.metric("Wellness Score", data["users"][user]["score"], "/100")
    col2.write("📅 Today:", date.today())
    col3.write("💬 Quote:", random.choice(QUOTES))

    st.info("Track your health, support others, and grow together.")

# ---------------- MENTAL HEALTH ----------------
def mental_health(user):
    st.header("🧠 Mental Well-Being")

    mood = st.radio("How are you feeling today?", ["Happy", "Okay", "Stressed"])
    if st.button("Save Mood"):
        data["users"][user]["moods"].append({
            "date": str(date.today()),
            "mood": mood
        })
        save_data(data)
        st.success("Mood saved")

    if data["users"][user]["moods"]:
        df = pd.DataFrame(data["users"][user]["moods"])
        st.line_chart(df["mood"].value_counts())

    st.subheader("📝 Daily Reflection")
    note = st.text_area("Write privately")
    if st.button("Save Reflection"):
        data["users"][user]["journal"].append({
            "date": str(date.today()),
            "note": note
        })
        save_data(data)
        st.success("Saved")

    st.subheader("🌬️ Breathing Exercise")
    if st.button("Start 20-Second Breathing"):
        with st.spinner("Breathe slowly…"):
            time.sleep(20)
        st.success("Nice work!")

# ---------------- PHYSICAL HEALTH ----------------
def physical_health():
    st.header("💪 Physical Health")

    st.selectbox("Daily activity goal", ["10 min", "20 min", "30 min"])
    st.checkbox("Stretching done")
    st.checkbox("Drank enough water")
    st.checkbox("Reduced screen time")

# ---------------- HABITS ----------------
def habit_tracker(user):
    st.header("📊 Habit Tracker")

    today = str(date.today())
    if today not in data["users"][user]["habits"]:
        data["users"][user]["habits"][today] = {}

    habits = ["Exercise", "Water", "Sleep", "Gratitude"]
    completed = 0

    for h in habits:
        val = st.checkbox(h, data["users"][user]["habits"][today].get(h, False))
        data["users"][user]["habits"][today][h] = val
        if val:
            completed += 1

    score = int((completed / len(habits)) * 100)
    data["users"][user]["score"] = score
    save_data(data)

    st.progress(score / 100)
    st.write(f"Today's Score: {score}%")

# ---------------- CHALLENGES ----------------
def challenges(user):
    st.header("🎯 Daily Wellness Challenge")

    today = str(date.today())
    challenge = random.choice(CHALLENGES)

    done = st.checkbox(f"Challenge: {challenge}")
    data["users"][user]["challenges"][today] = done
    save_data(data)

# ---------------- SUGGESTIONS ----------------
def suggestion_box(user):
    st.header("📬 Suggestion Box")

    category = st.selectbox("Category", ["Stress", "Academic", "General"])
    anon = st.checkbox("Submit anonymously")
    text = st.text_area("Your message")

    if st.button("Submit"):
        data["users"][user]["suggestions"].append({
            "category": category,
            "text": text,
            "anonymous": anon,
            "time": str(datetime.now())
        })
        save_data(data)
        st.success("Submitted")

# ---------------- COMMUNITY ----------------
def community():
    st.header("🧑‍🤝‍🧑 Gratitude Wall")

    msg = st.text_input("Post something positive")
    if st.button("Post"):
        if msg.strip():
            data["gratitude_wall"].append(msg)
            save_data(data)

    for g in data["gratitude_wall"][-10:]:
        st.write("💛", g)

# ---------------- BUSINESS ----------------
def business():
    st.header("💼 Student Wellness Solutions (SWS)")

    products = {
        "Digital Planner": 50,
        "Wellness Kit": 100,
        "Workshop Pass": 150
    }

    for p, price in products.items():
        if st.button(f"Buy {p} – ₹{price}"):
            data["total_revenue"] += price
            save_data(data)
            st.success("Purchase successful (demo)")

    st.info(f"Total Wellness Fund Raised: ₹{data['total_revenue']}")

# ---------------- REPORT ----------------
def report(user):
    st.header("📁 Personal Wellness Report")

    st.write("Mood entries:", len(data["users"][user]["moods"]))
    st.write("Journal entries:", len(data["users"][user]["journal"]))
    st.write("Current Score:", data["users"][user]["score"])

    if st.button("Export Mood Data (CSV)"):
        df = pd.DataFrame(data["users"][user]["moods"])
        df.to_csv("mood_report.csv", index=False)
        st.success("Exported as mood_report.csv")

# ---------------- MAIN ----------------
if st.session_state.user is None:
    auth_page()
else:
    user = st.session_state.user

    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard",
            "Mental Health",
            "Physical Health",
            "Habit Tracker",
            "Challenges",
            "Suggestion Box",
            "Community",
            "Business (SWS)",
            "Report",
            "Logout"
        ]
    )

    if menu == "Dashboard":
        dashboard(user)
    elif menu == "Mental Health":
        mental_health(user)
    elif menu == "Physical Health":
        physical_health()
    elif menu == "Habit Tracker":
        habit_tracker(user)
    elif menu == "Challenges":
        challenges(user)
    elif menu == "Suggestion Box":
        suggestion_box(user)
    elif menu == "Community":
        community()
    elif menu == "Business (SWS)":
        business()
    elif menu == "Report":
        report(user)
    elif menu == "Logout":
        st.session_state.user = None
        st.rerun()
