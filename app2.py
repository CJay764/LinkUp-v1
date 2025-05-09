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
            background-color: #d9e4dd;
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
    password = st.text_input("Password(Make sure you manually input your password-Dont use saved password here)", type="password")

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

    for record in users:
        f = record["fields"]
        fields = record.get("fields", {})
        requester_name = fields.get("Name", "Unknown")
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
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("💬 Chat Me", key=f"chat_{record['id']}"):
                    st.session_state.selected_contact = requester_name
                    st.session_state.page = "chat"
                    st.rerun()
            match_found = True
            st.write(f"### {requester_name}")
            st.write(f"📧 {f['Email']}")
            st.write(f"💡 They can teach you: {', '.join(one_way)}")
            if mutual:
                st.write(f"🔁 You can teach them: {', '.join(mutual)}")
            st.markdown("---")

    if not match_found:
        st.info("😕 No matches found.")

# handle chat interface
def show_chats():
    if "selected_contact" not in st.session_state:
        st.session_state.selected_contact = None
        
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
            has_unread = any(
                m["fields"]["Recipient"] == current_user_name and not m["fields"].get("Read", False)
                for m in chat_history
            )
            if has_unread:
                senders.add(sender)



    if senders:
        st.markdown("### 📥 Messages received from:")
        for sender in senders:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📨 **{sender}** sent you a message")
            with col2:
                if st.button(f"💬 Chat", key=f"chat_{sender}"):
                    st.session_state.selected_contact = sender
                    st.rerun()

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


    # Set default selected contact if it exists in session_state
    default_contact = st.session_state.get("selected_contact", None)
    if default_contact not in contacts:
        default_contact = None  # Fallback if invalid

    if default_contact in contacts:
        selected_contact = st.selectbox("Select a contact to chat with", contacts, index=contacts.index(default_contact))
    else:
        selected_contact = st.selectbox("Select a contact to chat with", contacts)


    # Always update session state so it reflects the latest selection
    st.session_state.selected_contact = selected_contact

    st.session_state.selected_contact = selected_contact


    if selected_contact:
        st.markdown(f"### 🗨️ Chat with {selected_contact}")
        if st.button("🔙 Back to Requests"):
            st.session_state.page = "post_request"
            st.rerun()

        if st.button("🔙 Back to Talents"):
            st.session_state.page = "Talents"
            st.rerun()
            
        if st.button("🔙 Back to Match finder"):
            st.session_state.page = "Match"
            st.rerun()

        # Fetch and display chat history
        messages = fetch_messages(current_user_name, selected_contact)

        for msg in messages:
            fields = msg.get("fields", {})
            sender = fields.get("Sender")
            content = fields.get("Message")
            timestamp = fields.get("Timestamp", "")
            read = fields.get("Read", False)  # Use Airtable checkbox
            # Add scroll-to-bottom JS after all messages
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


            if fields.get("Recipient") == current_user_name and not fields.get("Read", False):
                msg_id = msg["id"]
                update_url = f"https://api.airtable.com/v0/{BASE_ID}/Chats/{msg_id}"
                update_data = {
                    "fields": {
                        "Read": True
                    }
                }
                update_headers = {
                    "Authorization": f"Bearer {AIRTABLE_PAT}",
                    "Content-Type": "application/json"
                }
                try:
                    requests.patch(update_url, headers=update_headers, json=update_data)
                except Exception as e:
                    st.warning(f"Could not update read status: {e}")

            time_display = format_time_ago(timestamp) if timestamp else ""
            is_me = sender == current_user_name

            align = "right" if is_me else "left"
            bubble_color = "#6c757d" if is_me else "#e0ddd5"
            border = "solid 1px #ccc"

            # ✅✅ Tick logic
            tick = "✔✔" if is_me and read else "✔" if is_me else ""
            tick_color = "#34B7F1" if tick == "✔✔" else "gray"

            st.markdown(
                f"""
                <div style='width: 100%; display: flex; justify-content: {"flex-end" if is_me else "flex-start"};'>
                    <div style='background: {bubble_color}; border: {border}; padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 70%; position: relative;'>
                        <strong>{sender}:</strong> {content}<br>
                        <div style='font-size: 12px; text-align: right; color: grey;'>
                            {time_display} <span style='color: {tick_color}'>{tick}</span>
                        </div>
                    </div>
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
    st.session_state.page = None

# Talent zone
def Talent_Zone():
    url = f"https://api.airtable.com/v0/{BASE_ID}/Talent"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }


    st.markdown("### 💼 Offer Your Service(What can you do)")
    with st.form("post_service"):
        name = st.text_input("Full Name(Make sure it's the same name you used to signup)")
        title = st.text_input("Service Title (e.g. 'Logo Design')")
        description = st.text_area("What can you do?")
        price = st.number_input("Your price (₦)", min_value=0)
        contact_pref = st.radio("How should they contact you?", ["In-App Chat", "Phone/Email"])
        contact = st.text_input("If Phone/Email")
        uploaded_files = st.file_uploader("Upload Your Work if any(images ONLY)", accept_multiple_files=True, type=["png", "jpg", "jpeg"])
        submit = st.form_submit_button("📤 Post Service")

        if submit:
            # Convert uploaded files to Airtable attachments
            img_urls = []
            for file in uploaded_files:
                file_bytes = file.read()
                try:
                    image_url = upload_image_to_cloudinary(file_bytes, file.name)
                    img_urls.append(image_url)
                    st.success(f"Uploaded {file.name}")


                except Exception as e:
                    st.error(f"Failed to upload {file.name}")
                    st.exception(e)
            # Airtable expects a comma-separated string or array for custom fields
            works_combined = "\n".join(img_urls) if img_urls else ""
            
            user_data = {
                "fields": {
                    "Name": name,
                    "Title": title,
                    "Description": description,
                    "Price": price,
                    "Contact_pref": contact_pref,
                    "Contact": contact,
                    "Works": works_combined
                }
            }

            try:
                response = requests.post(url, headers=headers, json=user_data)
                response.raise_for_status()
                st.success("✅ Your service has been posted!")
            except requests.exceptions.RequestException as e:
                st.error("❌ Failed to post service.")
                st.exception(e)
                st.code(response.text if 'response' in locals() else 'No response body')

    # 🛠️ Always display available services below
    st.markdown("## 🛠️ Explore Available Services")
    try:
        list_response = requests.get(url, headers=headers)
        list_response.raise_for_status()
        records = list_response.json().get("records", [])
        st.markdown("### 🔎 Search Services")
        search_query = st.text_input("Type a keyword (e.g. 'design', 'math', 'resume')").lower()
        if search_query:
            records = [
                r for r in records
                if search_query in r["fields"].get("Title", "").lower()
                or search_query in r["fields"].get("Description", "").lower()
            ]

        
        
            # 🧰 Filter and Sort Options
        st.markdown("### 🔍 Filter & Sort")
        all_titles = list(set([record["fields"].get("Title", "Others") for record in records]))
        selected_title = st.selectbox("Filter by Title", options=["All"] + all_titles)
        sort_order = st.radio("Sort by Price", ["None", "Low to High", "High to Low"])
        
            # Apply filter
        if selected_title != "All":
            records = [record for record in records if record["fields"].get("Title") == selected_title]

            # Apply sorting
        if sort_order == "Low to High":
            records.sort(key=lambda r: r["fields"].get("Price", 0))
        elif sort_order == "High to Low":
            records.sort(key=lambda r: r["fields"].get("Price", 0), reverse=True)

        
        
        if not records:
            st.info("No services posted yet.")
        else:
            for record in records:
                fields = record.get("fields", {})
                requester_name = fields.get("Name", "Unknown")
                
                if st.button("👁 View Profile", key=record["id"]):
                    st.session_state.selected_talent = record
                    st.session_state.page = "view_talent"
                    st.rerun()
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("💬 Chat Me", key=f"chat_{record['id']}"):
                        st.session_state.selected_contact = requester_name
                        st.session_state.page = "chat"
                        st.rerun()
                st.markdown(
                    f"""
            <b>{fields.get('Title', 'No Title')}</b><br>
            - 👤 Name: {requester_name}<br>
            - 💬 Description: {fields.get('Description', 'No description')}<br>
            - 💸 Price: ₦{fields.get('Price', 0)}<br>
            - 📞 Contact Preference: {fields.get('Contact_pref', 'Not specified')}<br>
            - 📲 Contact: {fields.get('Contact', 'Not provided')}<br>
            
            <hr>
            """,

                    unsafe_allow_html=True
                )
                

    except requests.exceptions.RequestException as e:
        st.error("❌ Could not fetch services.")
        st.exception(e)



#Profile in talent zone
def view_talent_profile():
    talent = st.session_state.get("selected_talent")
    if not talent:
        st.warning("No talent selected.")
        return

    fields = talent.get("fields", {})
    st.markdown(f"## 👤 {fields.get('Name', 'No Name')}")
    st.markdown(f"**💼 Service:** {fields.get('Title', 'No Title')}")
    st.markdown(f"**📝 Bio/Description:** {fields.get('Description', 'No description')}")
    st.markdown(f"**💸 Price:** ₦{fields.get('Price', 0)}")
    st.markdown(f"**📞 Contact Preference:** {fields.get('Contact_pref', 'Not specified')}")
    st.markdown(f"**📲 Contact:** {fields.get('Contact', 'Not provided')}")

    # 🖼 Show uploaded works
    works_raw = fields.get("Works", "")
    if works_raw:
        st.markdown("### 🖼 Works / Portfolio:")
        urls = works_raw.split("\n")
        for url in urls:
            st.image(url, use_container_width=True)
    else:
        st.info("No work samples uploaded.")
        
    # Clear page trigger after showing
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
        name = st.text_input("Full Name(Make sure it's the same name you used to signup)")
        request_title = st.text_input("Need something? (e.g. 'Help with video editing')")
        details = st.text_area("Details of your request")
        budget = st.number_input("Budget (₦)", min_value=0)
        deadline = st.text_input("Deadline (optional)")
        contact_method = st.radio("Preferred Contact Method", ["In-App Chat", "Phone/Email"])
        contact_info = st.text_input("Phone Number or Email (optional)")

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