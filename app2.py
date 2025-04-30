import streamlit as st
import requests

# ---------- Configuration ----------
st.set_page_config(layout="wide")

# Airtable Configuration (REPLACE with your own credentials securely)
AIRTABLE_PAT = st.secrets["AIRTABLE_PAT"]
BASE_ID = st.secrets["BASE_ID"]
TABLE_NAME = st.secrets["TABLE_NAME"]
AIRTABLE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_PAT}",
    "Content-Type": "application/json"
}

# ---------- Airtable Functions ----------

def fetch_users():
    response = requests.get(AIRTABLE_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["records"]
    st.error("❌ Failed to fetch users.")
    return []

def add_user(name, email, skills, needs, bio):
    payload = {
        "fields": {
            "Name": name,
            "Email": email,
            "What I know": skills,
            "Looking For": needs,
            "Bio": bio
        }
    }
    response = requests.post(AIRTABLE_URL, headers=HEADERS, json=payload)
    if response.status_code == 201:
        st.success(f"✅ {name}, your profile was created!")
    else:
        st.error(f"❌ Failed to create profile.\nDetails: {response.text}")

# ---------- UI Pages ----------

def show_home():
    st.title("Welcome to LinkUp 🎯")
    st.subheader("Connect. Learn. Grow.")
    st.markdown("""
    LinkUp is a student connection platform.  
    - 🤝 Share what you know  
    - 🔍 Find what you need  
    - 🌱 Grow together
    """)

def show_sign_up():
    st.title("Student Sign-Up ✍️")
    with st.form("sign_up_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        skills = st.multiselect("What do you know?", ['Python', 'Java', 'JavaScript', 'C++', 'HTML', 'CSS'])
        needs = st.multiselect("What are you looking for?", ['Python', 'Java', 'JavaScript', 'C++', 'HTML', 'CSS'])
        bio = st.text_area("Tell us a bit about you")
        submit = st.form_submit_button("Sign Up")

        if submit:
            if name and email:
                add_user(name, email, skills, needs, bio)
            else:
                st.warning("Please fill in your Name and Email.")

def show_users():
    st.title("📋 All Students")
    records = fetch_users()

    if records:
        for r in records:
            f = r.get("fields", {})
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader(f.get("Name", "N/A"))
                st.write(f"📧 **Email:** {f.get('Email', 'N/A')}")
                st.write(f"💡 **Knows:** {', '.join(f.get('What I know', []))}")
                st.write(f"🔎 **Looking for:** {', '.join(f.get('Looking For', []))}")
                st.write(f"📝 **Bio:** {f.get('Bio', '')}")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No users found.")

def show_matches():
    st.title("🤝 Find Your Matches")

    users = [
        {
            "id": r["id"],
            "name": f.get("Name", ""),
            "email": f.get("Email", ""),
            "know": f.get("What I know", []),
            "looking_for": f.get("Looking For", []),
            "bio": f.get("Bio", "")
        }
        for r in fetch_users() if (f := r.get("fields"))
    ]

    if not users:
        st.warning("No users available.")
        return

    selected_name = st.selectbox("Select your name:", [u["name"] for u in users])
    current_user = next((u for u in users if u["name"] == selected_name), None)

    if not current_user:
        st.error("User not found.")
        return

    match_mode = st.radio("Match Type", [
        "🎯 One-way Match",
        "🔁 Skill Exchange Match"
    ])

    def show_match_card(user, title, you_get=None, you_give=None):
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"### {title}")
            st.write(f"📧 **Email:** {user['email']}")
            if you_get: st.write(f"💡 **They can teach you:** {', '.join(you_get)}")
            if you_give: st.write(f"🎓 **You can teach them:** {', '.join(you_give)}")
            st.write(f"📝 **Bio:** {user['bio']}")
            st.markdown('</div>', unsafe_allow_html=True)

    if match_mode == "🎯 One-way Match":
        st.subheader(f"Matches for {current_user['name']}")
        results = [
            (u, set(current_user["looking_for"]) & set(u["know"]))
            for u in users if u["id"] != current_user["id"]
        ]
        matches = [(u, m) for u, m in results if m]

        if matches:
            st.success(f"{len(matches)} match(es) found.")
            for u, m in matches:
                show_match_card(u, u["name"], you_get=m)
        else:
            st.info("No one-way matches found.")

    elif match_mode == "🔁 Skill Exchange Match":
        st.subheader(f"Skill Exchanges for {current_user['name']}")
        matches = []

        for u in users:
            if u["id"] == current_user["id"]:
                continue
            mutual_teach = set(current_user["looking_for"]) & set(u["know"])
            mutual_learn = set(u["looking_for"]) & set(current_user["know"])
            if mutual_teach and mutual_learn:
                matches.append((u, mutual_teach, mutual_learn))

        if matches:
            st.success(f"{len(matches)} exchange match(es) found.")
            for u, teach, learn in matches:
                show_match_card(u, u["name"], you_get=teach, you_give=learn)
        else:
            st.info("No skill exchange matches yet.")

# ---------- Custom CSS Styling ----------

st.markdown("""
<style>
    button[data-baseweb="tab"] > div {
        font-size: 20px;
        font-weight: bold;
        padding: 10px 18px;
        border-radius: 10px;
    }
    section.main > div { padding: 2rem 4rem; }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #0066cc;
        color: white;
    }
    .card {
        background-color: #fff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- App Runner ----------

def main():
    tabs = st.tabs(["🏠 Home", "📝 Sign Up", "🔍 Find Matches", "📋 View Students"])
    with tabs[0]: show_home()
    with tabs[1]: show_sign_up()
    with tabs[2]: show_matches()
    with tabs[3]: show_users()

main()
