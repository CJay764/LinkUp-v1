import streamlit as st
import requests

# ------------------ Config ------------------
st.set_page_config(layout="wide")
AIRTABLE_PAT = st.secrets["AIRTABLE_PAT"]
BASE_ID = st.secrets["BASE_ID"]
TABLE_NAME = st.secrets["TABLE_NAME"]
AIRTABLE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_PAT}", "Content-Type": "application/json"}

# ------------------ Session State ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = {}

# ------------------ Airtable Functions ------------------
def fetch_users():
    res = requests.get(AIRTABLE_URL, headers=HEADERS)
    if res.ok:
        return res.json()["records"]
    st.error("❌ Couldn't load users.")
    return []

def find_user(email, password):
    users = fetch_users()
    for u in users:
        f = u.get("fields", {})
        if f.get("Email") == email and f.get("Password") == password:
            return {"id": u["id"], **f}
    return None

def upsert_user(data, record_id=None):
    payload = {"fields": data}
    if record_id:
        url = f"{AIRTABLE_URL}/{record_id}"
        res = requests.patch(url, headers=HEADERS, json=payload)
    else:
        res = requests.post(AIRTABLE_URL, headers=HEADERS, json=payload)
    return res.ok

# ------------------ Pages ------------------
def show_home():
    st.title("Welcome to LinkUp 🎯")
    st.subheader("Connect. Learn. Grow.")
    st.markdown("""
    LinkUp is a student connection platform.  
    - 🤝 Share what you know  
    - 🔍 Find what you need  
    - 🌱 Grow together
    """)

def show_login():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = find_user(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.success(f"Welcome {user['Name']}!")
        else:
            st.error("Invalid credentials.")

def show_sign_up_or_update():
    st.title("✍️ " + ("Update Profile" if st.session_state.logged_in else "Sign Up"))

    intent = st.radio("Purpose", ["School Course Help", "Skills"])
    name = st.text_input("Full Name", st.session_state.current_user.get("Name", ""))
    email = st.text_input("Email", st.session_state.current_user.get("Email", ""))
    password = st.text_input("Password", type="password")

    course_options = ["CSC111", "MTH111", "CHM101", "PHY101"]
    skill_options = ["Python", "HTML", "CSS", "React", "SQL"]
    department_options = ["Mechanical Engineering", "Computer Engineering ", "Chemical Engineering"]

    # Combine stored departments with known options
    stored_departments = st.session_state.current_user.get("Department", [])
    combined_departments = list(set(department_options + stored_departments))

    department = st.multiselect(
        "Department",
        combined_departments,
        default=stored_departments
    )

    # Choose options based on intent
    options = course_options if intent == "School Course Help" else skill_options

    # Safely filter defaults so there's no mismatch
    stored_know = st.session_state.current_user.get("What I know", [])
    stored_know = [x for x in stored_know if x in options]

    stored_need = st.session_state.current_user.get("Looking For", [])
    stored_need = [x for x in stored_need if x in options]

    what_i_know = st.multiselect("What I know", options, default=stored_know)
    looking_for = st.multiselect("Looking For", options, default=stored_need)

    bio = st.text_area("Bio", st.session_state.current_user.get("Bio", ""))

    if st.button("Update" if st.session_state.logged_in else "Sign Up"):
        if not name or not email or not password:
            st.warning("Fill all required fields.")
            return

        user_data = {
            "Name": name,
            "Email": email,
            "Password": password,
            "Intent": intent,
            "Department": department,
            "What I know": what_i_know,
            "Looking For": looking_for,
            "Bio": bio
        }

        record_id = st.session_state.current_user.get("id") if st.session_state.logged_in else None
        success = upsert_user(user_data, record_id)

        if success:
            st.success("Profile saved.")
            st.session_state.current_user = {**user_data, "id": record_id}
            st.session_state.logged_in = True
        else:
            st.error("Failed to save profile.")

def show_users():
    st.title("📋 All Students")
    for r in fetch_users():
        f = r["fields"]
        st.subheader(f.get("Name", "N/A"))
        st.write(f"📧 {f.get('Email', '')}")
        st.write(f"💡 Knows: {', '.join(f.get('What I know', []))}")
        st.write(f"🔎 Looking For: {', '.join(f.get('Looking For', []))}")
        st.write(f"📝 Bio: {f.get('Bio', '')}")
        st.markdown("---")

def show_matches():
    st.title("🤝 Match Finder")
    current = st.session_state.current_user
    users = fetch_users()
    you_know = set(current.get("What I know", []))
    you_need = set(current.get("Looking For", []))

    for r in users:
        f = r["fields"]
        if f.get("Email") == current.get("Email"):
            continue
        they_know = set(f.get("What I know", []))
        they_need = set(f.get("Looking For", []))

        one_way = you_need & they_know
        mutual = one_way & (they_need & you_know)

        if one_way:
            st.write(f"### {f['Name']}")
            st.write(f"📧 {f['Email']}")
            st.write(f"💡 They can teach you: {', '.join(one_way)}")
            if mutual:
                st.write(f"🔁 You can teach them: {', '.join(mutual)}")
            st.markdown("---")

# ------------------ Navigation ------------------
st.sidebar.title("🔗 Navigation")

if st.session_state.logged_in:
    # Display user emoji and name in the sidebar
    user_name = st.session_state.current_user.get("Name", "Guest")
    st.sidebar.write(f"👤 {user_name}")
else:
    st.sidebar.write("👤 Guest")


if not st.session_state.logged_in:
    page = st.sidebar.radio("Go to", ["🏠 Home", "🔐 Login", "✍️ Sign Up"])
    
else:
    page = st.sidebar.radio("Go to", [
        "🏠 Home", "✍️ Update Profile", "📋 View Students", "🤝 Match Finder", "🚪 Logout"
    ])

if page == "🏠 Home":
    show_home()
elif page == "🔐 Login":
    show_login()
elif page == "✍️ Sign Up":
    show_sign_up_or_update()
elif page == "✍️ Update Profile":
    show_sign_up_or_update()
elif page == "📋 View Students":
    show_users()
elif page == "🤝 Match Finder":
    show_matches()
elif page == "🚪 Logout":
    st.session_state.logged_in = False
    st.session_state.current_user = {}
    st.success("Logged out.")
