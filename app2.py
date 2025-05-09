import streamlit as st
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime
from datetime import datetime, timezone
import cloudinary
import cloudinary.uploader

cloudinary.config(
  cloud_name = "deaprngfl",
  api_key = "186753967323192",
  api_secret = "mlrPlA_KihWJhC00YD-cYwWkqjM"
)


def upload_image_to_cloudinary(file_bytes, filename):
    try:
        result = cloudinary.uploader.upload(file_bytes, public_id=filename)
        return result['secure_url']
    except Exception as e:
        raise Exception("Upload to Cloudinary failed: " + str(e))







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

def format_time_ago(iso_time_str):
    msg_time = datetime.fromisoformat(iso_time_str.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    diff = now - msg_time

    seconds = int(diff.total_seconds())
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if seconds < 60:
        return f"{seconds} seconds ago"
    elif minutes < 60:
        return f"{minutes} minutes ago"
    elif hours < 24:
        return f"{hours} hours ago"
    else:
        return f"{days} days ago"
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
            "Read" : False
            
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
    # CSS Styles
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
        @keyframes typing { from { width: 0 } to { width: 18ch } }
        @keyframes blink { 50% { border-color: transparent } }
        .card, .vision {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border-left: 5px solid #4A90E2;
        }
        .card h3, .vision h3 { color: #4A90E2; }
        .card ul, .card p, .vision p {
            color: #444;
            font-size: 16px;
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
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        </style>
    """, unsafe_allow_html=True)

    # Background SVG Animation
    st.markdown("""
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

        <div class='big-title'>🎯 Welcome to LinkUp</div>
        <div class='subtitle'>Connect. Learn. Grow. </div>
        <br>
    """, unsafe_allow_html=True)

    # Logo (fallback warning)
    try:
        st.image("linkup_logo.png", use_container_width=True)
    except:
        st.warning("Logo not found! Make sure 'linkup_logo.png' is in your GitHub repo.")

    # What is LinkUp?
    st.markdown("""
        <div class='card'>
            <h3>💡 What is LinkUp?</h3>
            <p>LinkUp is your campus network for academic support, tech skills, and student talents:</p>
            <ul>
                <li>🤝 <b>Match with peers</b> based on what you know and what you need</li>
                <li>🧠 <b>Post help requests</b> when you're stuck or need something specific</li>
                <li>🌟 <b>Showcase your talents</b> and discover what others are great at</li>
            </ul>
        </div>

        <div class='vision'>
            <h3>🔭 Vision Statement</h3>
            <p>
                LinkUp is more than just matching—it’s a full ecosystem where students lift each other up. Whether you're struggling with a course, picking up a skill, or just want your work to be seen, LinkUp connects you to the right people on your campus.
            </p>
        </div>

        <div class='card'>
            <h3>🌐 Core Features</h3>
            <ul>
                <li>🎯 <b>Match Finder:</b> Connect based on your strengths and needs</li>
                <li>📝 <b>Post Requests:</b> Ask for help, offer assistance, or collaborate</li>
                <li>🎨 <b>Talent Zone:</b> Upload your projects or skills—get noticed</li>
                <li>💬 <b>Built-in Chat:</b> Instantly message your matches</li>
            </ul>
        </div>

        <div class='card'>
            <h3>📈 Why LinkUp Matters (Investor Snapshot)</h3>
            <ul>
                <li>🔥 Made by students, solving real student challenges</li>
                <li>🚀 Designed to scale to any university or student hub</li>
                <li>📊 Active usage and powerful peer learning outcomes</li>
                <li>💡 Future growth: AI, project hubs, student marketplaces</li>
            </ul>
        </div>
        
        <p class="cta">
            🚀 Use the sidebar to start matching, posting, or showing your skills!
        </p>

        <div class="footer">Made with ❤️ by students, for students</div>
    """, unsafe_allow_html=True)





    
# upgrading the login to show forgot password

def show_login():
    st.markdown("<h1 style='text-align: center;'>🔐 Login to LinkUp</h1>", unsafe_allow_html=True)
    st.markdown("Welcome back! Please enter your credentials to continue.")

    st.write("---")
    st.subheader("👤 Account Login")
    
    email = st.text_input("📧 Email", placeholder="yourname@gmail.com")
    password = st.text_input("🔑 Password", placeholder="Enter your password", type="password", help="Manually type your password. Avoid browser auto-fill here.")

    login_col1, login_col2 = st.columns([1, 2])
    with login_col1:
        login_clicked = st.button("🚪 Login")
    
    if login_clicked:
        user = find_user(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user

            st.success(f"✅ Welcome back, {user['Name']}!")
            st.rerun()
            st.info("✅ Tap the Login button again if you’re not redirected.")
        else:
            st.error("❌ Invalid email or password. Please try again.")

    st.write("---")
    st.subheader("🔁 Forgot Your Password?")
    st.markdown("If you’ve forgotten your password, enter your email and we’ll send it to you.")

    forgot_email = st.text_input("📨 Email for password reset", key="forgot_email")
    if st.button("📬 Send Reset Email"):
        user = next((u["fields"] for u in fetch_users() if u["fields"].get("Email") == forgot_email), None)
        if user:
            sent = send_password_email(forgot_email, user["Password"])
            if sent:
                st.success("✅ Password sent! Please check your email.")
            else:
                st.warning("⚠️ Could not send the email. Try again later.")
        else:
            st.warning("⚠️ No account found with that email.")



def show_sign_up_or_update():
    st.title("✍️ " + ("Update Profile" if st.session_state.logged_in else "Sign Up"))

    st.markdown("Please fill in your details to get better matches! Fields marked with * are required.")

    # --- Personal Info ---
    st.subheader("👤 Personal Information")
    name = st.text_input("Full Name *", st.session_state.current_user.get("Name", ""))
    email = st.text_input("Email *", st.session_state.current_user.get("Email", ""))
    password = st.text_input("Password *", type="password")

    # --- Intent Selection ---
    intent = st.radio("🤔 What are you here for?", ["School Course Help", "Skills"])

    # --- Conditional Academic Info ---
    course_options = ["TMC121", "MTH122", "GST123", "PHY121", "PHY123", "ENT121", "CHM122", "CIT141", "MTH123", "CIT121", "GET121"]
    skill_options = ["Python", "HTML", "CSS", "React", "SQL", "Musical Instrument Help", "Graphics Design", "How to play COD"]
    department_options = ["Computer Engineering", "Chemical Engineering", "Mechanical Engineering", "Petroleum Engineering",
                          "Civil Engineering", "Information and Computer Engineering", "Electrical and Electronics Engineering"]
    college_options = ["Engineering"]

    stored_colleges = st.session_state.current_user.get("College", [])
    stored_departments = st.session_state.current_user.get("Department", [])
    stored_know = st.session_state.current_user.get("What I know", [])
    stored_need = st.session_state.current_user.get("Looking For", [])
    bio = st.text_area("🗒️ Short Bio", st.session_state.current_user.get("Bio", ""))

    # Only show if intent is school-related
    if intent == "School Course Help":
        st.subheader("🏫 Academic Details")
        college = st.multiselect("College", list(set(college_options + stored_colleges)), default=stored_colleges)
        department = st.multiselect("Department", list(set(department_options + stored_departments)), default=stored_departments)
        options = course_options
    else:
        college, department = [], []
        options = skill_options

    # Filter existing skills/courses so they're valid for current intent
    filtered_know = [x for x in stored_know if x in options]
    filtered_need = [x for x in stored_need if x in options]

    st.subheader("🧠 Skill Matching")
    st.markdown("""
    - **What I know:** Topics or skills you can help others with.
    - **Looking For:** Topics or skills you need help with.
    """)
    what_i_know = st.multiselect("✅ What I know", options, default=filtered_know)
    looking_for = st.multiselect("❓ Looking For", options, default=filtered_need)

    if st.button("Update" if st.session_state.logged_in else "Sign Up"):
        if not name or not email or not password:
            st.warning("⚠️ Please fill in all required fields (Name, Email, Password).")
            return

        user_data = {
            "Name": name,
            "Email": email,
            "Password": password,
            "Intent": intent,
            "College": college,
            "Department": department,
            "What I know": what_i_know,
            "Looking For": looking_for,
            "Bio": bio
        }

        record_id = st.session_state.current_user.get("id") if st.session_state.logged_in else None
        success = upsert_user(user_data, record_id)

        if success:
            st.success("✅ Profile saved successfully!")
            st.session_state.current_user = {**user_data, "id": record_id}
            st.session_state.logged_in = True
        else:
            st.error("❌ Failed to save your profile. Please try again.")


def show_users():
    st.markdown("<h1 style='text-align: center;'>📋 Meet Other Students</h1>", unsafe_allow_html=True)
    st.markdown("Find fellow students to collaborate with based on what they know or need help with.")
    st.write("---")

    for r in fetch_users():
        f = r["fields"]
        requester_name = f.get("Name", "Unknown")

        # Layout card container
        with st.container():
            card_col1, card_col2 = st.columns([1, 5])

            # Left column: Chat button
            with card_col1:
                st.markdown("###")
                if st.button("💬 Chat Me", key=f"chat_{r['id']}"):
                    st.session_state.selected_contact = requester_name
                    st.session_state.page = "chat"
                    st.rerun()

            # Right column: User details
            with card_col2:
                st.subheader(f"👤 {requester_name}")
                st.markdown(f"📧 **Email:** {f.get('Email', 'N/A')}")

                knows = ", ".join(f.get("What I know", [])) or "None"
                looking_for = ", ".join(f.get("Looking For", [])) or "None"
                bio = f.get("Bio", "No bio provided.")

                st.markdown(f"💡 **Knows:** {knows}")
                st.markdown(f"🔎 **Looking For:** {looking_for}")
                st.markdown(f"📝 **Bio:** _{bio}_")

            st.markdown("---")


def show_matches():
    st.title("🤝 Match Finder")

    current = st.session_state.current_user
    users = fetch_users()
    you_know = set(current.get("What I know", []))
    you_need = set(current.get("Looking For", []))

    # 👇 Friendly explanation
    with st.expander("❓ How Matching Works"):
        st.markdown("""
        **🔁 Two-Way Match:** You need something they know, **and** they need something you know. You both can help each other!

        **➡️ One-Way Match:** You need something they know, but they don't need anything from you.

        **📌 Tip:** Start with Two-Way matches if you want a fair exchange. One-Way matches are great if you're just seeking help.
        """)

    match_type = st.radio("🔍 Show Matches By Type:", ["All Matches", "Only Two-Way Matches", "Only One-Way Matches"])

    match_found = False  # Track if any match is shown

    for record in users:
        f = record.get("fields", {})
        requester_name = f.get("Name", "Unknown")
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
            st.markdown("----")
            st.write(f"### {requester_name}")
            st.write(f"📧 {f.get('Email', 'No email')}")
            st.write(f"💡 They can help you with: **{', '.join(one_way)}**")
            if mutual:
                st.write(f"🔁 You can help them with: **{', '.join(mutual)}**")

            if st.button("💬 Chat Me", key=f"chat_{record['id']}"):
                st.session_state.selected_contact = requester_name
                st.session_state.page = "chat"
                st.rerun()

    if not match_found:
        st.info("😕 No matches found. Try changing your interests or check back later.")


# handle chat interface
def show_chats():
    if "selected_contact" not in st.session_state:
        st.session_state.selected_contact = None

    st.title("💬 Chats")
    current_user_name = st.session_state.current_user.get("Name")
    users = fetch_users()
    contacts = [user["fields"]["Name"] for user in users if user["fields"]["Name"] != current_user_name]

    all_msgs = fetch_received_messages(current_user_name)
    senders = set()

    for msg in all_msgs:
        fields = msg.get("fields", {})
        sender = fields.get("Sender")
        if fields.get("Recipient") == current_user_name:
            chat_history = fetch_messages(current_user_name, sender)
            has_unread = any(
                m["fields"]["Recipient"] == current_user_name and not m["fields"].get("Read", False)
                for m in chat_history
            )
            if has_unread:
                senders.add(sender)

    if senders:
        st.markdown("### 📥 New Messages From")
        for sender in senders:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📨 **{sender}** sent you a message")
            with col2:
                if st.button("💬 Chat", key=f"chat_{sender}"):
                    st.session_state.selected_contact = sender
                    st.rerun()
    else:
        st.info("No new messages yet.")

        if st.button("📂 Show Chat History"):
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
                    st.markdown("### 💬 You've Chatted With")
                    for contact in sorted(unique_contacts):
                        st.write(f"- {contact}")
                else:
                    st.info("You haven’t chatted with anyone yet.")
            else:
                st.error("Failed to fetch chat history.")

    # Select contact
    default_contact = st.session_state.selected_contact
    if default_contact not in contacts:
        default_contact = None

    selected_contact = st.selectbox("👥 Select a contact to chat with", contacts, index=contacts.index(default_contact) if default_contact else 0)
    st.session_state.selected_contact = selected_contact

    # --- Chat Interface ---
    if selected_contact:
        # 🧭 Back buttons section - aligned horizontally
        colA, colB, colC = st.columns(3)
        with colA:
            if st.button("⬅️ Back to Requests"):
                st.session_state.page = "post_request"
                st.rerun()
        with colB:
            if st.button("⬅️ Back to Talents"):
                st.session_state.page = "Talents"
                st.rerun()
        with colC:
            if st.button("⬅️ Back to Match Finder"):
                st.session_state.page = "Match"
                st.rerun()

        st.markdown(f"### 🗨️ Chat with **{selected_contact}**")

        messages = fetch_messages(current_user_name, selected_contact)

        for msg in messages:
            fields = msg.get("fields", {})
            sender = fields.get("Sender")
            content = fields.get("Message")
            timestamp = fields.get("Timestamp", "")
            read = fields.get("Read", False)
            recipient = fields.get("Recipient")

            # Mark message as read if necessary
            if recipient == current_user_name and not read:
                msg_id = msg["id"]
                try:
                    requests.patch(
                        f"https://api.airtable.com/v0/{BASE_ID}/Chats/{msg_id}",
                        headers={
                            "Authorization": f"Bearer {AIRTABLE_PAT}",
                            "Content-Type": "application/json"
                        },
                        json={"fields": {"Read": True}}
                    )
                except Exception as e:
                    st.warning(f"Could not update read status: {e}")

            time_display = format_time_ago(timestamp) if timestamp else ""
            is_me = sender == current_user_name
            align = "right" if is_me else "left"
            bubble_color = "#6c757d" if is_me else "#e0ddd5"
            border = "solid 1px #ccc"
            tick = "✔✔" if is_me and read else "✔" if is_me else ""
            tick_color = "#34B7F1" if tick == "✔✔" else "gray"

            st.markdown(
                f"""
                <div style='width: 100%; display: flex; justify-content: {"flex-end" if is_me else "flex-start"};'>
                    <div style='background: {bubble_color}; border: {border}; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 70%;'>
                        <strong>{sender}:</strong> {content}<br>
                        <div style='font-size: 12px; text-align: right; color: grey;'>
                            {time_display} <span style='color: {tick_color}'>{tick}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Auto scroll to bottom after all messages
        st.markdown(
            """
            <script>
            const chatContainer = window.parent.document.querySelector('section.main');
            if (chatContainer) {
                chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
            }
            </script>
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
    st.session_state.page = None

# Talent zone
def Talent_Zone():
    url = f"https://api.airtable.com/v0/{BASE_ID}/Talent"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    st.title("🎯 Talent Zone")

    st.markdown("### 📝 Post a Service You Offer")
    with st.form("post_service"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Full Name (same as used in signup)")
            title = st.text_input("🎨 Service Title (e.g. 'Logo Design', 'Selling of products')")
            price = st.number_input("💸 Price (₦)", min_value=0)
        with col2:
            contact_pref = st.radio("📞 Preferred Contact Method", ["In-App Chat", "Phone/Email"])
            contact = st.text_input("📧 Contact Info (if using Phone/Email)")
            uploaded_files = st.file_uploader("📷 Upload Work Samples/Product (images only)", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

        description = st.text_area("🛠️ Describe Your Service")

        submit = st.form_submit_button("📤 Post Service")

        if submit:
            img_urls = []
            for file in uploaded_files:
                try:
                    file_bytes = file.read()
                    image_url = upload_image_to_cloudinary(file_bytes, file.name)
                    img_urls.append(image_url)
                    st.success(f"✅ Uploaded: {file.name}")
                except Exception as e:
                    st.error(f"❌ Failed to upload {file.name}")
                    st.exception(e)

            user_data = {
                "fields": {
                    "Name": name,
                    "Title": title,
                    "Description": description,
                    "Price": price,
                    "Contact_pref": contact_pref,
                    "Contact": contact,
                    "Works": "\n".join(img_urls)
                }
            }

            try:
                response = requests.post(url, headers=headers, json=user_data)
                response.raise_for_status()
                st.success("🎉 Your service has been posted!")
            except requests.exceptions.RequestException as e:
                st.error("❌ Failed to post service.")
                st.exception(e)
                st.code(response.text if 'response' in locals() else 'No response body')

    # Display Existing Services
    st.markdown("---")
    st.markdown("## 🔍 Explore Available Services")

    try:
        list_response = requests.get(url, headers=headers)
        list_response.raise_for_status()
        records = list_response.json().get("records", [])

        st.markdown("### 🔎 Search & Filter")
        search_query = st.text_input("Search by keyword (e.g. 'design', 'resume')").lower()
        if search_query:
            records = [
                r for r in records
                if search_query in r["fields"].get("Title", "").lower()
                or search_query in r["fields"].get("Description", "").lower()
            ]

        all_titles = sorted(set([r["fields"].get("Title", "Others") for r in records]))
        selected_title = st.selectbox("🎯 Filter by Title", options=["All"] + all_titles)
        sort_order = st.radio("🧮 Sort by Price", ["None", "Low to High", "High to Low"])

        if selected_title != "All":
            records = [r for r in records if r["fields"].get("Title") == selected_title]

        if sort_order == "Low to High":
            records.sort(key=lambda r: r["fields"].get("Price", 0))
        elif sort_order == "High to Low":
            records.sort(key=lambda r: r["fields"].get("Price", 0), reverse=True)

        if not records:
            st.info("No matching services found.")
        else:
            for record in records:
                fields = record.get("fields", {})
                requester = fields.get("Name", "Unknown")
                title = fields.get("Title", "No Title")
                description = fields.get("Description", "No description")
                price = fields.get("Price", 0)
                contact_pref = fields.get("Contact_pref", "Not specified")
                contact = fields.get("Contact", "Not provided")

                st.markdown("----")
                col1, col2 = st.columns([5, 1])
                
                st.markdown(
                        f"""
                        <h4>{title}</h4>
                        <p>👤 Name: <strong>{requester}</strong></p>
                        <p>🛠️ Description: {description}</p>
                        <p>💸 Price: <strong>₦{price}</strong></p>
                        <p>📞 Contact preference: <strong>{contact_pref}</strong></p>
                        <p>📲 Contact: {contact}</p>
                        
                        """, unsafe_allow_html=True
                    )
                with col1:
                    if st.button("💬 Chat Me", key=f"chat_{record['id']}"):
                        st.session_state.selected_contact = requester
                        st.session_state.page = "chat"
                        st.rerun()
                    if st.button("👁 View Profile", key=f"profile_{record['id']}"):
                        st.session_state.selected_talent = record
                        st.session_state.page = "view_talent"
                        st.rerun()

    except requests.exceptions.RequestException as e:
        st.error("❌ Could not fetch services.")
        st.exception(e)



#Profile in talent zone
def view_talent_profile():
    if st.button("🔙 Back to Talent Zone"):
        st.session_state.page = "Talent zone"
        st.rerun()

    talent = st.session_state.get("selected_talent")
    if not talent:
        st.warning("⚠️ No talent selected.")
        return

    fields = talent.get("fields", {})
    name = fields.get("Name", "No Name")
    title = fields.get("Title", "No Title")
    description = fields.get("Description", "No description")
    price = fields.get("Price", 0)
    contact_pref = fields.get("Contact_pref", "Not specified")
    contact = fields.get("Contact", "Not provided")
    works_raw = fields.get("Works", "")

    st.markdown(f"## 👤 {name}'s Profile")

    
    st.markdown(
            f"""
            <div style="padding: 15px; border-radius: 10px; background-color: #d6d8db; margin-top: 10px;">
                <h4>💼 {title}</h4>
                <p>📝 <strong>Description:</strong><br>{description}</p>
                <p>💸 <strong>Price:</strong> ₦{price}</p>
                <p>📞 <strong>Contact Preference:</strong> {contact_pref}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    if contact_pref == "Phone/Email":
        st.markdown(f"📲 **Contact Info:** {contact}")


    st.markdown("### 🖼️ Work Samples / Portfolio")
    if works_raw:
        urls = [u.strip() for u in works_raw.split("\n") if u.strip()]
        cols = st.columns(2)
        for i, url in enumerate(urls):
            with cols[i % 2]:
                st.image(url, use_container_width=True)
    else:
        st.info("This user hasn't uploaded any work samples yet.")

    # Clear page state after loading profile
    st.session_state.page = None


# post requests
def post_request():
    url = f"https://api.airtable.com/v0/{BASE_ID}/Request"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    st.markdown('### ✨Post Your Request(What do u want)')
    st.markdown("""
        <div class='card'>
            <ul>
                <li>🙆‍♂️ <b>Need help in a task</b> – Find people who are skilled at the task</li>
                <li>🖊 <b>Just fill the form</b> – Wait for users to respond</li>
                <li>🔍 <b>Talent zone</b> – You can manually look for people with skills by going to the talent zone</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    with st.form("post_request_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Full Name(Make sure it's the same name you used to signup)")
            request_title = st.text_input("Need something? (e.g. 'Help with video editing')")
            budget = st.number_input("💸 Budget (₦)", min_value=0)
        with col2:
            deadline = st.text_input("⏰ Deadline (optional)")
            contact_method = st.radio("📞 Preferred Contact Method", ["In-App Chat", "Phone/Email"])
            contact_info = st.text_input("📧 Phone Number or Email (optional)")
        details = st.text_area("🖊 Details of your request")
                
        submit_request = st.form_submit_button("📤 Post Request")

        if submit_request:
            user_data = {
                "fields": {
                    "Name": name,
                    "Request": request_title,
                    "Details": details,
                    "Budget": budget,
                    "Deadline": deadline,
                    "Contact_pref": contact_method,
                    "Contact": contact_info
                }
            }

            try:
                response = requests.post(url, headers=headers, json=user_data)
                response.raise_for_status()
                st.success("✅ Your Request has been posted!")
            except requests.exceptions.RequestException as e:
                st.error("❌ Failed to post Request.")
                st.exception(e)
                st.code(response.text if 'response' in locals() else 'No response body')

    # 🔍 Browse Requests
    st.markdown("## 🔎 Open Requests")
    try:
        list_response = requests.get(url, headers=headers)
        list_response.raise_for_status()
        records = list_response.json().get("records", [])

        if not records:
            st.info("No requests posted yet.")
        else:
            
            for record in records:
                fields = record.get("fields", {})
                requester_name = fields.get("Name", "Unknown")
    
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; margin-bottom:10px; border-radius:5px;">
                    <h4>{fields.get('Request', 'No Title')}</h4>
                    <p><b>🙋 Name:</b> {requester_name}</p>
                    <p><b>📝 Details:</b> {fields.get('Details', 'No details')}</p>
                    <p><b>💰 Budget:</b> ₦{fields.get('Budget', 0)}</p>
                    <p><b>📆 Deadline:</b> {fields.get('Deadline', 'Not specified')}</p>
                    <p><b>📬 Contact Method:</b> {fields.get('Contact_pref', 'Not specified')}</p>
                    <p><b>📱 Contact:</b> {fields.get('Contact', 'N/A')}</p>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("💬 Chat Me", key=f"chat_{record['id']}"):
                        st.session_state.selected_contact = requester_name
                        st.session_state.page = "chat"
                        st.rerun()

    except requests.exceptions.RequestException as e:
        st.error("❌ Could not fetch requests.")
        st.exception(e)


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
        "🏠 Home", "✍️ Update Profile", "📋 View Students", "🤝 Match Finder", "💬 Chats","📥 Service Requests","🛠 Talent Zone", "🚪 Logout"
    ])

    # If user clicked "View Profile" in Talent Zone, redirect here
    if st.session_state.get("page") == "view_talent":
        page = "🔍 View Talent"
    elif st.session_state.get("page") == "chat":
        page = "💬 Chats"
    
    elif st.session_state.get("page") == "post_request":
        page = "post_request"
    elif st.session_state.get("page") == "Talents":
        page = "Talents"
    elif st.session_state.get("page") == "Match":
        page = "Match"
    elif st.session_state.get("page") == "Talent zone":
        page = "Talent zone"

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
    st.rerun()
    
elif page=="💬 Chats":
    show_chats()
elif page=="🛠 Talent Zone":
    Talent_Zone()
elif page=="📥 Service Requests":
    post_request()

elif page == "🔍 View Talent":
    view_talent_profile()

elif page == "💬 Chats":
    show_chats()

elif page == "post_request":
    post_request()
    
elif page == "Talents":
    Talent_Zone()

elif page == "Match":
    show_matches()
    
elif page == "Talent Zone":
    Talent_Zone()