import streamlit as st
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime
import humanize
from datetime import datetime, timezone

# ------------------ Session State ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = {}

# ------------------ Airtable Functions ------------------
def fetch_users():
    # Fetch users from Airtable
    pass

def find_user(email, password):
    # Check user credentials
    pass

#time ago code
def format_time_ago(iso_time_str):
    msg_time = datetime.fromisoformat(iso_time_str.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    return humanize.naturaltime(now - msg_time)

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

    # Debugging line
    if not res.ok:
        st.error(f"❌ Airtable Error: {res.status_code} - {res.text}")
    return res.ok





# chat section

def fetch_messages(user_name, contact_name):
    try:
        url = f"https://api.airtable.com/v0/{BASE_ID}/Chats"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_PAT}",
            "Content-Type": "application/json"
        }

        filter_formula = (
        f"OR("
        f"AND(Sender='{user_name}', Recipient='{contact_name}'),"
        f"AND(Sender='{contact_name}', Recipient='{user_name}')"
        f")"
        )


        params = {
            "filterByFormula": filter_formula,
            "sort[0][field]": "Timestamp",
            "sort[0][direction]": "asc"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json().get("records", [])

    except Exception as e:
        st.error("❌ Failed to fetch messages.")
        st.exception(e)  # Display detailed error
        st.code(response.text if 'response' in locals() else 'No response body')
        return []

def send_message(sender_name, recipient_name, message):
    url = f"https://api.airtable.com/v0/{BASE_ID}/Chats"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }
    data = {
        "fields": {
            "Sender": sender_name,
            "Recipient": recipient_name,
            "Message": message,
            
        }
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise error if status is not 2xx
        return True
    except requests.exceptions.RequestException as e:
        st.error("❌ Failed to send message.")
        st.exception(e)  # Show full error details
        st.code(response.text if 'response' in locals() else 'No response body')
        return False



def fetch_received_messages(current_user_name):
    try:
        url = f"https://api.airtable.com/v0/{BASE_ID}/Chats"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_PAT}",
            "Content-Type": "application/json"
        }

        filter_formula = f"Recipient='{current_user_name}'"

        params = {
            "filterByFormula": filter_formula,
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("records", [])

    except Exception as e:
        st.error("❌ Failed to fetch received messages.")
        st.exception(e)
        return []




# forgot password-chidi idea

def send_password_email(to_email, password):
    msg = EmailMessage()
    msg.set_content(f"Your LinkUp password is: {password}")
    msg["Subject"] = "LinkUp Password Reset"
    msg["From"] = st.secrets["EMAIL_ADDRESS"]
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(st.secrets["EMAIL_ADDRESS"], st.secrets["EMAIL_APP_PASSWORD"])
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False



# ------------------ Pages ------------------


def show_home():
    # CSS first (NO HTML inside style tag!)
    st.markdown("""
        <style>
        body {
            background: linear-gradient(135deg, #E6F0FF, #f0f4ff, #d9eaff);
            color: #333;
            font-family: 'Arial', sans-serif;
        }

        .bg-animate {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            z-index: -1;
        }

        .big-title {
            font-size: 48px;
            color: #4A90E2;
            text-align: center;
            font-weight: bold;
            margin-bottom: 0;
        }

        .subtitle {
            font-size: 24px;
            color: #555;
            text-align: center;
            margin-top: 0;
            overflow: hidden;
            white-space: nowrap;
            border-right: 3px solid #4A90E2;
            width: 18ch;
            margin: 0 auto;
            animation: typing 3s steps(18), blink .75s step-end infinite;
        }

        @keyframes typing {
            from { width: 0 }
            to { width: 18ch }
        }

        @keyframes blink {
            50% { border-color: transparent }
        }

        .card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border-left: 5px solid #4A90E2;
        }

        .card h3 {
            color: #4A90E2;
        }

        .card ul, .card p {
            color: #444;
            font-size: 16px;
        }

        .vision {
            background-color: #F0F8FF;
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid #4A90E2;
            margin-bottom: 20px;
        }

        .vision h3 {
            color: #4A90E2;
        }

        .footer {
            text-align: center;
            font-size: 14px;
            color: #999;
        }

        .cta {
            text-align: center;
            font-size: 18px;
            color: #4A90E2;
            font-style: italic;
            animation: fadeIn 2s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        </style>
    """, unsafe_allow_html=True)

    # HTML content now (NO CSS here)
    st.markdown("""
        <!-- Floating animated circles SVG -->
        <div class='bg-animate'>
          <svg height="100vh" width="100%">
            <circle cx="20%" cy="20%" r="60" fill="#4A90E2" opacity="0.08">
              <animate attributeName="cy" from="20%" to="80%" dur="10s" repeatCount="indefinite" />
            </circle>
            <circle cx="80%" cy="60%" r="40" fill="#4A90E2" opacity="0.08">
              <animate attributeName="cy" from="60%" to="30%" dur="12s" repeatCount="indefinite" />
            </circle>
          </svg>
        </div>

        </div>

        <div class='big-title'>🎯 Welcome to LinkUp</div>
        <div class='subtitle'>Connect. Learn. Grow. </div>
        <br>
    """, unsafe_allow_html=True)

    # Optional: fallback if image doesn't render
    try:
        st.image("linkup_logo.png", use_container_width=True)
    except:
        st.warning("Logo not found! Make sure 'linkup_logo.png' is in your GitHub repo.")

    st.markdown("""
        <div class='card'>
            <h3>💡 What is LinkUp?</h3>
            <p>LinkUp is a student-powered platform that helps you:</p>
            <ul>
                <li>🤝 <b>Share what you know</b> – Help others in your department or with skills you're good at</li>
                <li>🔍 <b>Find what you need</b> – Get help with tough courses or discover who’s learning the same skill</li>
                <li>🌱 <b>Grow together</b> – Build your network and improve together</li>
            </ul>
        </div>

        <div class='vision'>
            <h3>🔭 Vision Statement</h3>
            <p>
            At LinkUp, our vision is to empower students by creating a dynamic peer-to-peer platform where academic support meets skill development.
            We aim to foster meaningful connections that go beyond the classroom—whether you're seeking help with your courses or looking to collaborate
            on tech projects. LinkUp envisions a future where every student has the network and resources to thrive, grow, and succeed together.
            </p>
        </div>

        <div class='card'>
            <h3>📈 Why LinkUp Matters (Investor's Snapshot)</h3>
            <ul>
                <li>🔥 Built by students, for students – real campus pain points, real solutions</li>
                <li>🚀 Scalable model – customizable for any university or learning community</li>
                <li>📊 Growing engagement – active users, frequent logins, and high peer match success rate</li>
                <li>💡 Future vision – integrated learning tools, AI study assistant, community marketplace</li>
            </ul>
        </div>

        <p class="cta">
            🚀 Get started by heading over to the navigation pane located at the top left of your screen.
        </p>

        <div class="footer">Made with ❤️ by students, for students</div>
    """, unsafe_allow_html=True)





    
# upgrading the login to show forgot password

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

    if st.checkbox("Forgot Password?"):
        forgot_email = st.text_input("Enter your email to reset password")
        if st.button("Send Reset Email"):
            user = next((u["fields"] for u in fetch_users() if u["fields"].get("Email") == forgot_email), None)
            if user:
                sent = send_password_email(forgot_email, user["Password"])
                if sent:
                    st.success("✅ Check your email for your password.")
            else:
                st.warning("No account found with that email.")



def show_sign_up_or_update():
    st.title("✍️ " + ("Update Profile" if st.session_state.logged_in else "Sign Up"))

    intent = st.radio("Purpose", ["School Course Help", "Skills"])
    name = st.text_input("Full Name", st.session_state.current_user.get("Name", ""))
    email = st.text_input("Email", st.session_state.current_user.get("Email", ""))
    password = st.text_input("Password", type="password")

    course_options = ["TMC121", "MTH122", "GST123", "PHY121","PHY123", "ENT121", "CHM122", "CIT141","MTH123", "CIT121", "GET121"]
    skill_options = ["Python", "HTML", "CSS", "React", "SQL", "Musical Instrument Help", "Graphics Design", "How to play COD"]
    department_options = ["Computer Engineering", "Chemical Engineering","Mechanical Engineering","Petroleum Engineering","Civil Engineering","Information and Computer Engineering","Electrical and Electronics Engineering"]
    college_options=["Engineering"]
    
    # Combine stored college with known options
    stored_colleges = st.session_state.current_user.get("College", [])
    combined_colleges = list(set(college_options + stored_colleges))

    college = st.multiselect(
        "College",
        combined_colleges,
        default=stored_colleges
    )

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
            "Bio": bio,
            "College": college
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

    match_type = st.radio("🔍 Show Matches:", ["All Matches", "Only Two-Way Matches", "Only One-Way Matches"])

    match_found = False  # Track if any match is shown

    for r in users:
        f = r["fields"]
        if f.get("Email") == current.get("Email"):
            continue

        they_know = set(f.get("What I know", []))
        they_need = set(f.get("Looking For", []))

        one_way = you_need & they_know
        mutual = one_way & (they_need & you_know)

        show = False
        if match_type == "All Matches" and one_way:
            show = True
        elif match_type == "Only One-Way Matches" and one_way and not mutual:
            show = True
        elif match_type == "Only Two-Way Matches" and mutual:
            show = True

        if show:
            match_found = True
            st.write(f"### {f['Name']}")
            st.write(f"📧 {f['Email']}")
            st.write(f"💡 They can teach you: {', '.join(one_way)}")
            if mutual:
                st.write(f"🔁 You can teach them: {', '.join(mutual)}")
            st.markdown("---")

    if not match_found:
        st.info("😕 No matches found.")

# handle chat interface
def show_chats():
    st.title("💬 Chats")

    current_user_name = st.session_state.current_user.get("Name")
    users = fetch_users()
    contacts = [user["fields"]["Name"] for user in users if user["fields"]["Name"] != current_user_name]

    
    # Fetch all messages received by the current user
    all_msgs = fetch_received_messages(current_user_name)


    senders = set()
    for msg in all_msgs:
        fields = msg.get("fields", {})
        sender = fields.get("Sender")
        if fields.get("Recipient") == current_user_name:
            # Check if current user has replied to this sender
            chat_history = fetch_messages(current_user_name, sender)
            has_replied = any(m["fields"]["Sender"] == current_user_name for m in chat_history)
            if not has_replied:
                senders.add(sender)


    if senders:
        st.markdown("### 📥 Messages received from:")
        for sender in senders:
            st.write(f"- {sender}")
    else:
        st.info("No messages received yet.")


        if st.button("📂 Show Chat History"):
            # Fetch messages where current user is either sender or recipient
            url = f"https://api.airtable.com/v0/{BASE_ID}/Chats"
            headers = {
            "Authorization": f"Bearer {AIRTABLE_PAT}",
            "Content-Type": "application/json"
            }

            params = {
            "filterByFormula": f"OR(Sender='{current_user_name}', Recipient='{current_user_name}')"
            }

            response = requests.get(url, headers=headers, params=params)
            if response.ok:
                records = response.json().get("records", [])
                unique_contacts = set()
                for r in records:
                    f = r["fields"]
                    if f.get("Sender") != current_user_name:
                        unique_contacts.add(f.get("Sender"))
                    elif f.get("Recipient") != current_user_name:
                        unique_contacts.add(f.get("Recipient"))
                if unique_contacts:
                    st.markdown("### 💬 You have chatted with:")
                    for contact in sorted(unique_contacts):
                        st.write(f"- {contact}")
                else:
                    st.info("You haven’t chatted with anyone yet.")
            else:
                st.error("Failed to fetch chat history.")


    selected_contact = st.selectbox("Select a contact to chat with", contacts)

    if selected_contact:
        st.markdown(f"### 🗨️ Chat with {selected_contact}")
    
        # Fetch and display chat history
        messages = fetch_messages(current_user_name, selected_contact)

        for msg in messages:
            fields = msg.get("fields", {})
            sender = fields.get("Sender")
            content = fields.get("Message")
            timestamp = fields.get("Timestamp", "")
            time_display = format_time_ago(timestamp) if timestamp else ""

            align = "right" if sender == current_user_name else "left"
            bubble_color = "#6c757d" if sender == current_user_name else "#fff"
            border = "solid 1px #ccc"

            st.markdown(
                f"""
                <div style='text-align: {align}; background: {bubble_color}; border: {border}; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 70%; display: inline-block;'>
                    <strong>{sender}:</strong> {content}<br><small>{time_display}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

        def send_and_refresh():
            message = st.session_state.chat_input.strip()
            if message:
                send_message(current_user_name, selected_contact, message)
                st.session_state.chat_input = ""
                st.session_state.last_sent = datetime.utcnow().isoformat()

        st.text_input("Type your message:", key="chat_input", on_change=send_and_refresh)

        if st.session_state.get("last_sent"):
            st.caption(f"Last sent at: {st.session_state.last_sent}")


 




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
        "🏠 Home", "✍️ Update Profile", "📋 View Students", "🤝 Match Finder", "💬 Chats", "🚪 Logout"
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
elif page=="💬 Chats":
    show_chats()