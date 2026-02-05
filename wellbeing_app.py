import streamlit as st
import json, os, random, time
from datetime import date, datetime
import pandas as pd

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Well-Being for All",
    page_icon="💙",
    layout="wide"
)

DATA_FILE = "wellbeing_data.json"

# ======================================================
# GLOBAL STYLES (FONTS + ANIMATIONS)
# ======================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;500;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.fade {
    animation: fadeIn 0.6s ease;
}
@keyframes fadeIn {
    from {opacity:0; transform:translateY(8px);}
    to {opacity:1; transform:translateY(0);}
}

.main-title {
    font-family:'Poppins',sans-serif;
    font-size:44px;
    font-weight:700;
    background:linear-gradient(90deg,#4facfe,#00f2fe);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.card {
    background:#f9fbff;
    border-radius:18px;
    padding:22px;
    margin-bottom:22px;
    box-shadow:0 10px 30px rgba(0,0,0,0.06);
    transition:0.25s;
}
.card:hover { transform:translateY(-4px); }

.badge {
    display:inline-block;
    padding:6px 14px;
    border-radius:20px;
    background:#e6f4ff;
    color:#0077cc;
    font-size:12px;
    margin-right:6px;
}

.divider {
    height:1px;
    background:linear-gradient(to right, transparent, #cce7ff, transparent);
    margin:24px 0;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# DATA HANDLING
# ======================================================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "users": {},
            "gratitude": [],
            "revenue": 0
        }
    return json.load(open(DATA_FILE))

def save_data(d):
    json.dump(d, open(DATA_FILE, "w"), indent=4)

data = load_data()

# ======================================================
# SESSION
# ======================================================
if "user" not in st.session_state:
    st.session_state.user = None

# ======================================================
# HELPERS
# ======================================================
def today():
    return str(date.today())

def level(score):
    if score < 40: return "Bronze 🟤"
    if score < 75: return "Silver ⚪"
    return "Gold 🟡"
# ======================================================
# AUTH
# ======================================================
def auth():
    st.markdown("<div class='main-title fade'>💙 Well-Being for All</div>", unsafe_allow_html=True)
    st.caption("Student-Led Wellness & Social Enterprise App")

    mode = st.radio("Choose", ["Login", "Sign Up"])
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if mode == "Sign Up":
        cp = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["Student", "Teacher"])

        if st.button("Create Account"):
            if u in data["users"]:
                st.error("User already exists")
            elif p != cp:
                st.error("Passwords do not match")
            else:
                data["users"][u] = {
                    "password": p,
                    "role": role,
                    "moods": [],
                    "journal": [],
                    "habits": {},
                    "tasks": [],
                    "xp": 0,
                    "streak": 0,
                    "score": 0
                }
                save_data(data)
                st.success("Account created. Please login.")
    else:
        if st.button("Login"):
            if u in data["users"] and data["users"][u]["password"] == p:
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

# ======================================================
# DASHBOARD
# ======================================================
def dashboard(u):
    user = data["users"][u]

    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader(f"👋 Welcome, {u}")
    st.write(f"📅 Today: {date.today()}")
    st.metric("Wellness Score", user["score"])
    st.write(f"🏅 Level: {level(user['score'])}")
    st.write(f"✨ XP: {user['xp']}")
    st.write(f"🔥 Streak: {user['streak']} days")
    st.markdown("<span class='badge'>Self-care</span><span class='badge'>Consistency</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# PROFILE
# ======================================================
def profile(u):
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("👤 Profile")
    st.write(f"Role: {data['users'][u]['role']}")
    st.write(f"Mood entries: {len(data['users'][u]['moods'])}")
    st.write(f"Journal entries: {len(data['users'][u]['journal'])}")
    st.write(f"Tasks created: {len(data['users'][u]['tasks'])}")
    st.markdown("</div>", unsafe_allow_html=True)
# ======================================================
# MENTAL HEALTH
# ======================================================
def mental_health(u):
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("🧠 Mental Well-Being")

    mood = st.radio("How do you feel today?", ["Happy 😊","Okay 😐","Stressed 😣"])
    if st.button("Save Mood"):
        data["users"][u]["moods"].append({"date":today(),"mood":mood})
        data["users"][u]["xp"] += 5
        save_data(data)
        st.success("Mood saved +5 XP")

    if data["users"][u]["moods"]:
        df = pd.DataFrame(data["users"][u]["moods"])
        st.bar_chart(df["mood"].value_counts())

    note = st.text_area("📝 Private Reflection")
    if st.button("Save Reflection"):
        if note.strip():
            data["users"][u]["journal"].append({"date":today(),"text":note})
            data["users"][u]["xp"] += 10
            save_data(data)
            st.success("Reflection saved +10 XP")

    if st.button("🌬️ 20-second breathing"):
        with st.spinner("Breathe slowly…"):
            time.sleep(20)
        st.success("Calm session complete")

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# HABITS
# ======================================================
def habits(u):
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("📊 Habit Tracker")

    t = today()
    if t not in data["users"][u]["habits"]:
        data["users"][u]["habits"][t] = {}

    habit_list = ["Exercise","Water","Sleep","Gratitude"]
    done = 0

    for h in habit_list:
        v = st.checkbox(h, data["users"][u]["habits"][t].get(h, False))
        data["users"][u]["habits"][t][h] = v
        if v: done += 1

    score = int((done/len(habit_list))*100)
    data["users"][u]["score"] = score
    if score == 100:
        data["users"][u]["streak"] += 1
        data["users"][u]["xp"] += 20

    save_data(data)
    st.progress(score/100)
    st.write(f"Completion: {score}%")
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# THINGS TO DO (TASK SYSTEM)
# ======================================================
def tasks(u):
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("📝 Things To Do")

    new_task = st.text_input("Add a new task")
    if st.button("Add Task"):
        if new_task.strip():
            data["users"][u]["tasks"].append({
                "task": new_task,
                "done": False,
                "date": today()
            })
            save_data(data)

    for i, t in enumerate(data["users"][u]["tasks"]):
        checked = st.checkbox(t["task"], t["done"], key=f"task_{i}")
        data["users"][u]["tasks"][i]["done"] = checked

    save_data(data)
    st.markdown("</div>", unsafe_allow_html=True)
# ======================================================
# COMMUNITY
# ======================================================
def community():
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("💛 Gratitude Wall")

    g = st.text_input("Share something positive")
    if st.button("Post"):
        if g.strip():
            data["gratitude"].append(g)
            save_data(data)

    for msg in data["gratitude"][-12:]:
        st.write("•", msg)

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# BUSINESS
# ======================================================
def business():
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("💼 Student Wellness Solutions (SWS)")

    products = {
        "Digital Planner":50,
        "Wellness Kit":100,
        "Workshop Access":150
    }

    for p,price in products.items():
        if st.button(f"Buy {p} – ₹{price}"):
            data["revenue"] += price
            save_data(data)
            st.success("Purchase successful (demo)")

    st.info(f"Total Wellness Fund: ₹{data['revenue']}")
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# ACHIEVEMENTS
# ======================================================
def achievements(u):
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("🏆 Achievements")

    xp = data["users"][u]["xp"]
    streak = data["users"][u]["streak"]

    if xp >= 50: st.success("🎖️ Consistent Starter")
    if xp >= 150: st.success("🏅 Wellness Builder")
    if streak >= 3: st.success("🔥 Streak Master")
    if xp < 50: st.info("Keep going to unlock achievements!")

    st.markdown("</div>", unsafe_allow_html=True)
# ======================================================
# SETTINGS
# ======================================================
def settings(u):
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("⚙️ Settings")

    st.write(f"User: {u}")
    st.write(f"Role: {data['users'][u]['role']}")
    st.write(f"XP: {data['users'][u]['xp']}")

    if st.button("Reset today's habits"):
        data["users"][u]["habits"].pop(today(), None)
        save_data(data)
        st.warning("Today's habits reset")

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# MAIN
# ======================================================
if st.session_state.user is None:
    auth()

else:
    u = st.session_state.user

    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard",
            "Profile",
            "Mental Health",
            "Habits",
            "Things To Do",
            "Achievements",
            "Daily Challenge",
            "Reminders",
            "Community",
            "Business",
            "Reports",
            "Certificate",
            "Settings",
            "Logout"
        ]
    )

    if menu == "Dashboard":
        dashboard(u)

    elif menu == "Profile":
        profile(u)

    elif menu == "Mental Health":
        mental_health(u)

    elif menu == "Habits":
        habits(u)

    elif menu == "Things To Do":
        tasks(u)

    elif menu == "Achievements":
        achievements(u)

    elif menu == "Daily Challenge":
        daily_challenge(u)

    elif menu == "Reminders":
        reminders()

    elif menu == "Community":
        community()

    elif menu == "Business":
        business()

    elif menu == "Reports":
        reports(u)

    elif menu == "Certificate":
        certificate(u)

    elif menu == "Settings":
        settings(u)

    elif menu == "Logout":
        st.session_state.user = None
        st.rerun()


# ======================================================
# DAILY CHALLENGE
# ======================================================
CHALLENGES = [
    "Drink 8 glasses of water",
    "Take a 10-minute walk",
    "Write 3 things you’re grateful for",
    "Stretch for 5 minutes",
    "Sleep before 11 PM",
    "Help someone today"
]

def daily_challenge(u):
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("⚡ Daily Challenge")

    today_key = today()
    challenge = CHALLENGES[hash(today_key) % len(CHALLENGES)]

    st.write("Today's Challenge:")
    st.success(challenge)

    if "challenge_done" not in data["users"][u]:
        data["users"][u]["challenge_done"] = {}

    if data["users"][u]["challenge_done"].get(today_key):
        st.info("Challenge already completed today")
    else:
        if st.button("Mark as Completed"):
            data["users"][u]["challenge_done"][today_key] = True
            data["users"][u]["xp"] += 25
            save_data(data)
            st.success("Challenge completed! +25 XP")

    st.markdown("</div>", unsafe_allow_html=True)
# ======================================================
# REMINDERS
# ======================================================
def reminders():
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("⏰ Self-Care Reminders")

    reminder = st.selectbox(
        "Choose a reminder",
        ["Drink Water 💧", "Stand & Stretch 🧍", "Take a Deep Breath 🌬️"]
    )

    if st.button("Trigger Reminder"):
        st.warning(f"Reminder: {reminder}")

    st.caption("Demo reminder system (works without notifications)")
    st.markdown("</div>", unsafe_allow_html=True)
# ======================================================
# ADVANCED REPORTS
# ======================================================
def reports(u):
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("📈 Advanced Wellness Report")

    user = data["users"][u]

    report_data = {
        "XP": user["xp"],
        "Score": user["score"],
        "Streak": user["streak"],
        "Mood Entries": len(user["moods"]),
        "Journal Entries": len(user["journal"]),
        "Tasks": len(user["tasks"])
    }

    df = pd.DataFrame([report_data])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Report (CSV)",
        csv,
        "wellbeing_report.csv",
        "text/csv"
    )

    st.markdown("</div>", unsafe_allow_html=True)
# ======================================================
# TEACHER DASHBOARD
# ======================================================
def teacher_dashboard():
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("👩‍🏫 Teacher Dashboard")

    mood_count = {}
    total_xp = 0
    users = 0

    for user in data["users"].values():
        users += 1
        total_xp += user.get("xp", 0)
        for m in user.get("moods", []):
            mood_count[m["mood"]] = mood_count.get(m["mood"], 0) + 1

    if mood_count:
        st.write("Overall Mood Distribution")
        st.bar_chart(mood_count)

    st.metric("Total Users", users)
    st.metric("Total XP Earned", total_xp)

    st.markdown("</div>", unsafe_allow_html=True)
# ======================================================
# CERTIFICATE
# ======================================================
def certificate(u):
    st.markdown("<div class='card fade'>", unsafe_allow_html=True)
    st.subheader("📜 Wellness Certificate")

    st.markdown(f"""
    **Certificate of Participation**

    This certifies that **{u}** has actively participated in the  
    **Well-Being for All Student Wellness Program**

    🏅 Level Achieved: **{level(data["users"][u]["score"])}**  
    ✨ XP Earned: **{data["users"][u]["xp"]}**
    """)

    if st.button("Generate Certificate"):
        st.success("Certificate generated successfully (demo)")

    st.markdown("</div>", unsafe_allow_html=True)


