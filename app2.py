import streamlit as st
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
import cloudinary
import cloudinary.uploader
import time    
from streamlit_autorefresh import st_autorefresh









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
    # Enhanced CSS with modern design and animations
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        .main-container {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .hero-section {
            text-align: center;
            padding: 3rem 1rem;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
            border-radius: 20px;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: float 6s ease-in-out infinite;
        }
        
        .hero-section::after {
            content: '';
            position: absolute;
            background: url('https://yourdomain.com/linkup_logo.png') no-repeat center;
            background-size: 60%;
            opacity: 0.05;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            z-index: 1;
        }

        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 2;
        }
        
        .hero-subtitle {
            font-size: 1.4rem;
            color: #f8f9ff;
            margin-bottom: 2rem;
            position: relative;
            z-index: 2;
            opacity: 0;
            animation: fadeInUp 1s ease-out 0.5s forwards;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .stats-container {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 2rem;
            position: relative;
            z-index: 2;
        }
        
        .stat-box {
            background: rgba(255,255,255,0.2);
            padding: 1rem 1.5rem;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.3);
        }
        
        .stat-box h3 {
            color: #ffffff;
            font-size: 2rem;
            margin: 0;
            font-weight: 600;
        }
        
        .stat-box p {
            color: #f8f9ff;
            margin: 0;
            font-size: 0.9rem;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .feature-card {
            background: linear-gradient(145deg, #ffffff, #f0f4ff);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 1px solid rgba(102, 126, 234, 0.2);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
            transition: left 0.5s;
        }
        
        .feature-card:hover::before {
            left: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }
        
        .feature-card h3 {
            color: #4A5568;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .feature-card p, .feature-card li {
            color: #718096;
            line-height: 1.6;
            font-size: 1rem;
        }
        
        .feature-card ul {
            padding-left: 1.2rem;
        }
        
        .cta-section {
            background: linear-gradient(135deg, #4299e1, #667eea);
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
            position: relative;
            overflow: hidden;
        }
        
        .cta-section::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            pointer-events: none;
        }
        
        .cta-title {
            color: #ffffff;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            position: relative;
            z-index: 2;
        }
        
        .cta-text {
            color: #f7fafc;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            position: relative;
            z-index: 2;
        }
        
        .pulse-icon {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .footer {
            text-align: center;
            color: #a0aec0;
            font-size: 0.9rem;
            margin-top: 3rem;
            padding: 2rem;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
        }
        
        .highlight {
            background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">
            🎯 Welcome to <span class="highlight">LinkUp</span>
        </div>
        <div class="hero-subtitle">
            The Ultimate Campus Network for Academic Excellence & Collaboration
        </div>
        <div class="stats-container">
            <div class="stat-box">
                <h3>📚</h3>
                <p>Academic Help</p>
            </div>
            <div class="stat-box">
                <h3>🤝</h3>
                <p>Peer Matching</p>
            </div>
            <div class="stat-box">
                <h3>💼</h3>
                <p>Talent Showcase</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Logo with error handling
    try:
        st.image("linkup_logo.png", use_container_width=True)
    except:
        st.info("🖼️ Upload your LinkUp logo as 'linkup_logo.png' to display it here!")

    # Features Grid - Fixed with proper card separation
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <span class="feature-icon pulse-icon">🎯</span>
            <h3>Smart Match Finder</h3>
            <p>Our intelligent algorithm connects you with peers based on:</p>
            <ul>
                <li><strong>What you know</strong> - Your expertise areas</li>
                <li><strong>What you need</strong> - Topics you're learning</li>
                <li><strong>Two-way matching</strong> - Mutual help opportunities</li>
                <li><strong>Academic compatibility</strong> - Same courses & interests</li>
            </ul>
        </div>

    <style>
    .feature-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .feature-icon {
        font-size: 24px;
        margin-right: 10px;
    }
    </style>

    <div class="feature-card">
        <span class="feature-icon">📌</span>
        <h3>Request Hub</h3>
        <p>Need specific help? Post your request and get responses from qualified students:</p>
        <ul>
            <li><strong>Assignment assistance</strong> - Get help when stuck</li>
            <li><strong>Study group formation</strong> - Find study partners</li>
            <li><strong>Skill development</strong> - Learn from peers</li>
            <li><strong>Project collaboration</strong> - Team up on assignments</li>
        </ul>
    </div>

    <div class="feature-card">
        <span class="feature-icon">🌟</span>
        <h3>Talent Marketplace</h3>
        <p>Showcase your skills and discover amazing student talents:</p>
        <ul>
            <li><strong>Portfolio showcase</strong> - Display your best work</li>
            <li><strong>Service offerings</strong> - Monetize your skills</li>
            <li><strong>Creative discovery</strong> - Find talented peers</li>
            <li><strong>Skill exchange</strong> - Trade expertise</li>
        </ul>
    </div>

    <div class="feature-card">
        <span class="feature-icon">💬</span>
        <h3>Instant Communication</h3>
        <p>Built-in chat system for seamless collaboration:</p>
        <ul>
            <li><strong>Real-time messaging</strong> - Chat with matches instantly</li>
            <li><strong>Read receipts</strong> - Know when messages are seen</li>
            <li><strong>Auto-refresh</strong> - Stay updated on conversations</li>
            <li><strong>Contact preferences</strong> - Choose how to connect</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Vision and Mission Section
    st.markdown("""
    <div class="feature-card" style="margin: 2rem 0;">
        <span class="feature-icon">🔭</span>
        <h3>Our Vision: Transforming Campus Learning</h3>
        <p>
            LinkUp isn't just another student app—it's a comprehensive ecosystem designed to revolutionize how students learn, collaborate, and succeed together. We believe that every student has unique knowledge and skills that can benefit others, creating a powerful network of peer-to-peer learning.
        </p>
        <p>
            <strong>🎓 Academic Excellence:</strong> Transform struggling students into confident learners through peer support.<br>
            <strong>🌐 Community Building:</strong> Break down barriers between departments and create lasting academic relationships.<br>
            <strong>💡 Innovation Hub:</strong> Foster creativity and entrepreneurship by connecting talented students with opportunities.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # How It Works Section
    st.markdown("""
    <div class="feature-card" style="margin: 2rem 0;">
        <span class="feature-icon">⚡</span>
        <h3>How LinkUp Works: Simple Yet Powerful</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">1️⃣</div>
                <strong>Sign Up</strong><br>
                <small>Create your profile with skills and learning needs</small>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">2️⃣</div>
                <strong>Get Matched</strong><br>
                <small>Our algorithm finds your perfect study partners</small>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">3️⃣</div>
                <strong>Connect & Learn</strong><br>
                <small>Chat, collaborate, and grow together</small>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">4️⃣</div>
                <strong>Succeed</strong><br>
                <small>Achieve academic goals through peer support</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Success Stories Preview
    st.markdown("""
    <div class="feature-card" style="background: linear-gradient(145deg, #f0fff4, #e6fffa);">
        <span class="feature-icon">🏆</span>
        <h3>Student Success Stories</h3>
        <div style="font-style: italic; color: #2d3748;">
            <p>"LinkUp helped me find a study group for Organic Chemistry. My grades improved from C to A!"</p>
            <p>"I discovered amazing graphic designers through the Talent Zone. Now I have a team for my startup!"</p>
            <p>"The match finder connected me with someone who needed help with Python - I made money tutoring!"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Call to Action
    st.markdown("""
    <div class="cta-section">
        <div class="cta-title">Ready to Transform Your Academic Journey?</div>
        <div class="cta-text">
            Join thousands of students who are already collaborating, learning, and succeeding together on LinkUp!
        </div>
        <div style="font-size: 1.1rem; color: #ffffff;">
            📱 Use the sidebar to start matching, posting requests, or showcasing your talents<br>
            🚀 Your next breakthrough is just one connection away!
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        <div style="font-size: 1.1rem; margin-bottom: 1rem;">
            🎓 Made with ❤️ by students, for students
        </div>
        <div>
            Empowering academic excellence through peer collaboration • 
            Building the future of campus networking • 
            Where knowledge meets opportunity
        </div>
    </div>
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

    # College → Departments mapping
    college_to_departments = {
        "College of Engineering": [
            "Computer Engineering", "Chemical Engineering", "Mechanical Engineering",
            "Petroleum Engineering", "Civil Engineering", "Information and Computer Engineering",
            "Electrical and Electronics Engineering"
        ],
        "College of Science and Technology": [
            "Industrial Chemistry", "Biochemistry", "Computer Science", "Microbiology"
        ],
        "College of Management and Security Service": [
            "Business Admin", "Accounting", "International Relations"
        ],
        "College of Leadership and Development Services": [
            "Leadership Studies", "Development Studies", "Political Science"
        ]
    }

    course_options = ["TMC121", "MTH122", "GST123", "PHY121", "PHY123", "ENT121", "CHM122", "CIT141", "MTH123", "CIT121", "GET121"]
    skill_options = ["Python", "HTML", "CSS", "React", "SQL", "Musical Instrument Help", "Graphics Design", "How to play COD"]

    stored_college = st.session_state.current_user.get("College", "")
    stored_department = st.session_state.current_user.get("Department", "")
    stored_know = st.session_state.current_user.get("What I know", [])
    stored_need = st.session_state.current_user.get("Looking For", [])
    bio = st.text_area("🗒️ Short Bio", st.session_state.current_user.get("Bio", ""))

    if intent == "School Course Help":
        st.subheader("🏫 Academic Details")

        # Select College
        college = st.selectbox("College (NOTE: AFTER SIGNING UP YOU CANT CHANGE THIS, DONT EVEN TRY)", list(college_to_departments.keys()), index=0 if not stored_college else list(college_to_departments.keys()).index(stored_college))

        # Department options based on selected college
        department_list = college_to_departments.get(college, [])
        department = st.selectbox("Department", department_list, index=0 if not stored_department else department_list.index(stored_department))

        options = course_options
    else:
        college, department = "", ""
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
            st.rerun()
        else:
            st.error("❌ Failed to save your profile. Please try again.")


def show_users():
    # Enhanced header with gradient background
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        '>
            <h1 style='
                text-align: center;
                color: white;
                margin: 0;
                font-size: 2.5rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            '>📋 Meet Other Students</h1>
            <p style='
                text-align: center;
                color: rgba(255,255,255,0.9);
                margin: 0.5rem 0 0 0;
                font-size: 1.1rem;
            '>Find fellow students to collaborate with based on what they know or need help with</p>
        </div>
    """, unsafe_allow_html=True)

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

    # Custom CSS for enhanced cards
    st.markdown("""
        <style>
        .user-card {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 
                0 10px 30px rgba(0,0,0,0.1),
                0 1px 8px rgba(0,0,0,0.06),
                inset 0 1px 0 rgba(255,255,255,0.8);
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        .user-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: left 0.5s;
        }
        .user-card:hover::before {
            left: 100%;
        }
        .user-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 
                0 20px 40px rgba(0,0,0,0.15),
                0 8px 16px rgba(0,0,0,0.1),
                inset 0 1px 0 rgba(255,255,255,0.9);
        }
        .user-name {
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb, #f5576c);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
            animation: glow 3s ease-in-out infinite alternate;
            text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
            position: relative;
        }
        @keyframes glow {
            0% {
                background-position: 0% 50%;
                filter: brightness(1) drop-shadow(0 0 5px rgba(102, 126, 234, 0.3));
            }
            50% {
                background-position: 100% 50%;
                filter: brightness(1.2) drop-shadow(0 0 15px rgba(118, 75, 162, 0.5));
            }
            100% {
                background-position: 200% 50%;
                filter: brightness(1) drop-shadow(0 0 10px rgba(245, 87, 108, 0.4));
            }
        }
        .user-detail {
            margin: 0.5rem 0;
            font-size: 1rem;
            color: #2c3e50;
            font-weight: 500;
        }
        .knows-tag {
            background: linear-gradient(135deg, #a8e6cf, #88d8a3, #dcedc1);
            color: #2d5016;
            padding: 0.4rem 1rem;
            border-radius: 25px;
            font-size: 0.85rem;
            margin: 0.2rem;
            display: inline-block;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(168, 230, 207, 0.4);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .knows-tag:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(168, 230, 207, 0.6);
        }
        .looking-tag {
            background: linear-gradient(135deg, #ffd3a5, #fd9853, #ffa726);
            color: #8b4513;
            padding: 0.4rem 1rem;
            border-radius: 25px;
            font-size: 0.85rem;
            margin: 0.2rem;
            display: inline-block;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(255, 211, 165, 0.4);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .looking-tag:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 211, 165, 0.6);
        }
        .bio-text {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 1.2rem;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            font-style: italic;
            color: #495057;
            margin-top: 1rem;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
            font-size: 0.95rem;
            line-height: 1.6;
        }
        .section-title {
            color: #2c3e50;
            font-weight: 600;
            margin: 1rem 0 0.5rem 0;
            font-size: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    users = fetch_users()
    
    # Show total count
    st.markdown(f"""
        <div style='
            text-align: center;
            background: #f8f9fa;
            padding: 0.8rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            border: 2px dashed #dee2e6;
        '>
            <span style='font-size: 1.1rem; color: #495057;'>
                🎓 <strong>{len(users)}</strong> students ready to collaborate
            </span>
        </div>
    """, unsafe_allow_html=True)

    for r in users:
        f = r["fields"]
        requester_name = f.get("Name", "Unknown")

        # Start card container
        st.markdown('<div class="user-card">', unsafe_allow_html=True)
        
        # Layout card container
        with st.container():
            card_col1, card_col2 = st.columns([1, 4])

            # Left column: Chat button with enhanced styling
            with card_col1:
                st.markdown("<br><br>", unsafe_allow_html=True)  # Add some spacing
                # Custom styled button
                st.markdown(f"""
                    <style>
                    .chat-btn-{r['id']} {{
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        color: white;
                        border: none;
                        padding: 0.8rem 1.5rem;
                        border-radius: 25px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                        width: 100%;
                        font-size: 0.9rem;
                    }}
                    .chat-btn-{r['id']}:hover {{
                        transform: translateY(-3px);
                        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
                        background: linear-gradient(135deg, #764ba2, #667eea);
                    }}
                    </style>
                """, unsafe_allow_html=True)
                
                if st.button(
                    "💬 Chat Me", 
                    key=f"chat_{r['id']}",
                    help=f"Start a conversation with {requester_name}",
                    use_container_width=True
                ):
                    st.session_state.selected_contact = requester_name
                    st.session_state.page = "chat"
                    st.rerun()

            # Right column: User details with enhanced formatting
            with card_col2:
                # User name with glowing effect
                st.markdown(f'<div class="user-name">👤 {requester_name}</div>', unsafe_allow_html=True)
                
                # Email with privacy masking
                email = f.get('Email', 'N/A')
                if email != 'N/A' and '@' in email:
                    username, domain = email.split('@', 1)
                    if len(username) > 2:
                        masked_email = username[:2] + '*' * (len(username) - 2) + '@' + domain
                    else:
                        masked_email = username[0] + '*' * (len(username) - 1) + '@' + domain
                else:
                    masked_email = email
                st.markdown(f'<div class="user-detail">📧 <strong>Email:</strong> <span style="color: #667eea;">{masked_email}</span></div>', unsafe_allow_html=True)

                # What they know - as enhanced tags
                knows_list = f.get("What I know", [])
                if knows_list:
                    st.markdown('<div class="section-title">💡 <strong>Areas of Expertise:</strong></div>', unsafe_allow_html=True)
                    knows_tags = ''.join([f'<span class="knows-tag">🌟 {skill}</span>' for skill in knows_list])
                    st.markdown(f'<div style="margin: 0.5rem 0;">{knows_tags}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="user-detail">💡 <strong>Areas of Expertise:</strong> <em style="color: #6c757d;">Open to sharing knowledge</em></div>', unsafe_allow_html=True)

                # What they're looking for - as enhanced tags
                looking_list = f.get("Looking For", [])
                if looking_list:
                    st.markdown('<div class="section-title">🔎 <strong>Seeking Help With:</strong></div>', unsafe_allow_html=True)
                    looking_tags = ''.join([f'<span class="looking-tag">🎯 {need}</span>' for need in looking_list])
                    st.markdown(f'<div style="margin: 0.5rem 0;">{looking_tags}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="user-detail">🔎 <strong>Seeking Help With:</strong> <em style="color: #6c757d;">Open to learning anything</em></div>', unsafe_allow_html=True)

                # Bio in a styled box
                bio = f.get("Bio", "No bio provided.")
                st.markdown(f'<div class="bio-text">📝 <strong>About Me:</strong><br>{bio}</div>', unsafe_allow_html=True)

        # End card container
        st.markdown('</div>', unsafe_allow_html=True)

    # Add footer message if no users
    if not users:
        st.markdown("""
            <div style='
                text-align: center;
                padding: 3rem;
                color: #6c757d;
            '>
                <h3>🤔 No students found</h3>
                <p>Be the first to join the community!</p>
            </div>
        """, unsafe_allow_html=True)
        
        
        
def show_matches():
    def mask_email(email):
        """Mask email address for privacy - shows first 2 chars + *** + domain"""
        if not email or '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = local[0] + '*' * (len(local) - 1) if len(local) > 1 else local
        else:
            masked_local = local[:2] + '***'
        
        return f"{masked_local}@{domain}"

    # Enhanced hero section
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 3rem 2rem;
            border-radius: 25px;
            margin-bottom: 2rem;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
            position: relative;
            overflow: hidden;
        '>
            <div style='
                position: absolute;
                top: -50%;
                right: -20%;
                width: 300px;
                height: 300px;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                border-radius: 50%;
            '></div>
            <h1 style='
                text-align: center;
                color: white;
                margin: 0;
                font-size: 3rem;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
                animation: pulse 2s ease-in-out infinite alternate;
            '>🤝 Match Finder Zone</h1>
            <p style='
                text-align: center;
                color: rgba(255,255,255,0.9);
                margin: 1rem 0 0 0;
                font-size: 1.2rem;
                font-weight: 300;
            '>Discover your perfect study partners and collaboration opportunities</p>
        </div>
        <style>
        @keyframes pulse {
            0% { transform: scale(1); }
            100% { transform: scale(1.02); }
        }
        </style>
    """, unsafe_allow_html=True)

    current = st.session_state.current_user
    users = fetch_users()
    you_know = set(current.get("What I know", []))
    you_need = set(current.get("Looking For", []))

    # Enhanced explanation section
    st.markdown("""
        <style>
        .explanation-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            border: 2px solid #dee2e6;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
            position: relative;
        }
        .match-type-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 5px solid;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .match-type-card:hover {
            transform: translateX(5px);
        }
        .two-way { border-left-color: #28a745; }
        .one-way { border-left-color: #ffc107; }
        .tip { border-left-color: #17a2b8; }
        </style>
    """, unsafe_allow_html=True)

    with st.expander("❓ How Our Smart Matching Works", expanded=False):
        st.markdown("### 🧠 Intelligent Match Algorithm")
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 5px solid #28a745;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.1);
        ">
            <h4 style="color: #28a745; margin: 0 0 0.5rem 0;">🔁 Two-Way Match (Perfect Partners)</h4>
            <p style="margin: 0; color: #2d5016;">You need something they know <strong>AND</strong> they need something you know. Perfect collaboration!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 5px solid #ffc107;
            box-shadow: 0 4px 15px rgba(255, 193, 7, 0.1);
        ">
            <h4 style="color: #b8860b; margin: 0 0 0.5rem 0;">➡️ One-Way Match (You Learn)</h4>
            <p style="margin: 0; color: #8b6914;">You need something they know, but they don't need your expertise right now.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #d1ecf1, #bee5eb);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 5px solid #17a2b8;
            box-shadow: 0 4px 15px rgba(23, 162, 184, 0.1);
        ">
            <h4 style="color: #17a2b8; margin: 0 0 0.5rem 0;">💡 Pro Tip</h4>
            <p style="margin: 0; color: #0c5460;">Start with Two-Way matches for fair knowledge exchange. One-Way matches are perfect when you just need help!</p>
        </div>
        """, unsafe_allow_html=True)

    # Enhanced filter section
    st.markdown("""
        <div style='
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1.5rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #e9ecef;
        '>
            <h3 style='color: #2c3e50; margin-bottom: 1rem;'>🔍 Filter Your Matches</h3>
        </div>
    """, unsafe_allow_html=True)
    
    match_type = st.radio(
        "Choose match type:", 
        ["All Matches", "Only Two-Way Matches", "Only One-Way Matches"],
        horizontal=True,
        help="Filter matches based on collaboration type"
    )

    # Enhanced CSS for match cards
    st.markdown("""
        <style>
        .match-card {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        .match-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: left 0.5s;
        }
        .match-card:hover::before {
            left: 100%;
        }
        .match-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        }
        .match-card.two-way {
            box-shadow: 0 8px 30px rgba(40, 167, 69, 0.2);
            border-left: 6px solid #28a745;
        }
        .match-card.one-way {
            box-shadow: 0 8px 30px rgba(255, 193, 7, 0.2);
            border-left: 6px solid #ffc107;
        }
        .match-name {
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 1rem;
            animation: nameGlow 3s ease-in-out infinite alternate;
        }
        @keyframes nameGlow {
            0% { background-position: 0% 50%; }
            100% { background-position: 100% 50%; }
        }
        .match-badge {
            display: inline-block;
            padding: 0.3rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .badge-two-way {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
        }
        .badge-one-way {
            background: linear-gradient(135deg, #ffc107, #fd7e14);
            color: #212529;
            box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
        }
        .skill-tag {
            display: inline-block;
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            color: #1565c0;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.85rem;
            margin: 0.2rem;
            font-weight: 500;
            box-shadow: 0 2px 5px rgba(21, 101, 192, 0.2);
        }
        .mutual-skill-tag {
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
            color: #2e7d32;
            box-shadow: 0 2px 5px rgba(46, 125, 50, 0.2);
        }
        .match-stats {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #667eea;
        }
        </style>
    """, unsafe_allow_html=True)

    match_found = False
    two_way_count = 0
    one_way_count = 0

    # Count matches for stats
    for record in users:
        f = record.get("fields", {})
        if f.get("Email") == current.get("Email"):
            continue
        they_know = set(f.get("What I know", []))
        they_need = set(f.get("Looking For", []))
        one_way = you_need & they_know
        mutual = one_way & (they_need & you_know)
        
        if one_way and mutual:
            two_way_count += 1
        elif one_way:
            one_way_count += 1

    # Display match stats
    if two_way_count > 0 or one_way_count > 0:
        st.markdown(f"""
            <div class="match-stats">
                <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">📊 Your Match Statistics</h4>
                <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; font-weight: bold; color: #28a745;">{two_way_count}</div>
                        <div style="color: #6c757d;">Two-Way Matches</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; font-weight: bold; color: #ffc107;">{one_way_count}</div>
                        <div style="color: #6c757d;">One-Way Matches</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; font-weight: bold; color: #667eea;">{two_way_count + one_way_count}</div>
                        <div style="color: #6c757d;">Total Matches</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Process and display matches
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
        is_two_way = bool(mutual)
        
        if match_type == "All Matches" and one_way:
            show = True
        elif match_type == "Only One-Way Matches" and one_way and not mutual:
            show = True
        elif match_type == "Only Two-Way Matches" and mutual:
            show = True
            
        if show:
            match_found = True
            
            # Determine card class and badge
            card_class = "two-way" if is_two_way else "one-way"
            badge_class = "badge-two-way" if is_two_way else "badge-one-way"
            badge_text = "🔁 Perfect Match" if is_two_way else "➡️ Learning Opportunity"
            
            st.markdown(f'<div class="match-card {card_class}">', unsafe_allow_html=True)
            
            # Match badge
            st.markdown(f'<div class="match-badge {badge_class}">{badge_text}</div>', unsafe_allow_html=True)
            
            # User name with glow effect
            st.markdown(f'<div class="match-name">👤 {requester_name}</div>', unsafe_allow_html=True)
            
            # Create columns for layout
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Email with masking
                email = f.get('Email', 'No email')
                masked_email = mask_email(email)
                st.markdown(f'<p style="color: #6c757d; margin-bottom: 1rem;">📧 <strong>{masked_email}</strong></p>', unsafe_allow_html=True)
                
                # What they can help you with
                if one_way:
                    st.markdown('<p style="color: #2c3e50; font-weight: 600; margin-bottom: 0.5rem;">💡 They can help you with:</p>', unsafe_allow_html=True)
                    help_tags = ''.join([f'<span class="skill-tag">🌟 {skill}</span>' for skill in one_way])
                    st.markdown(f'<div style="margin-bottom: 1rem;">{help_tags}</div>', unsafe_allow_html=True)
                
                # What you can help them with (mutual)
                if mutual:
                    st.markdown('<p style="color: #2c3e50; font-weight: 600; margin-bottom: 0.5rem;">🔁 You can help them with:</p>', unsafe_allow_html=True)
                    mutual_tags = ''.join([f'<span class="skill-tag mutual-skill-tag">🤝 {skill}</span>' for skill in mutual])
                    st.markdown(f'<div style="margin-bottom: 1rem;">{mutual_tags}</div>', unsafe_allow_html=True)
                
                # Bio if available
                bio = f.get("Bio", "")
                if bio and bio != "No bio provided.":
                    st.markdown(f"""
                        <div style="
                            background: #f8f9fa;
                            padding: 1rem;
                            border-radius: 10px;
                            border-left: 4px solid #667eea;
                            margin-top: 1rem;
                        ">
                            <strong>About {requester_name}:</strong><br>
                            <em style="color: #6c757d;">{bio}</em>
                        </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button(
                    "💬 Start Chat", 
                    key=f"chat_{record['id']}",
                    help=f"Begin conversation with {requester_name}",
                    use_container_width=True
                ):
                    st.session_state.selected_contact = requester_name
                    st.session_state.page = "chat"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced no matches found message
    if not match_found:
        st.markdown("""
            <div style='
                text-align: center;
                padding: 4rem 2rem;
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                border-radius: 20px;
                margin: 2rem 0;
                border: 2px dashed #dee2e6;
            '>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>🔍</div>
                <h3 style='color: #495057; margin-bottom: 1rem;'>No Matches Found</h3>
                <p style='color: #6c757d; font-size: 1.1rem; max-width: 500px; margin: 0 auto;'>
                    Don't worry! Try updating your skills or interests in your profile, 
                    or check back later as new students join the community.
                </p>
                <div style='margin-top: 2rem;'>
                    <p style='color: #667eea; font-weight: 600;'>💡 Tips to get more matches:</p>
                    <ul style='list-style: none; padding: 0; color: #6c757d;'>
                        <li>• Add more skills you know</li>
                        <li>• Specify what you're looking to learn</li>
                        <li>• Write a compelling bio</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)

# handle chat interface
def show_chats():
    # Automatically refresh the chat page every 90 seconds
    count = st_autorefresh(interval=90000, key="chatrefresh")  # 5000 ms = 5 seconds

    if "selected_contact" not in st.session_state:
        st.session_state.selected_contact = None

    # Enhanced header with better styling
    st.markdown("""
    <div style='text-align: center; padding: 20px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            💬 Messages
        </h1>
        <p style='color: rgba(255,255,255,0.8); margin: 5px 0 0 0; font-size: 1.1rem;'>
            Connect and communicate with your network
        </p>
    </div>
    """, unsafe_allow_html=True)
    
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

    # Enhanced new messages section
    if senders:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ff6b6b, #ffa726); padding: 20px; border-radius: 12px; 
                    margin-bottom: 25px; box-shadow: 0 4px 12px rgba(255,107,107,0.3);'>
            <h3 style='color: white; margin: 0 0 15px 0; font-size: 1.4rem; font-weight: 600;'>
                🔔 New Messages
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        for sender in senders:
            st.markdown(f"""
            <div style='background: white; border-left: 4px solid #ff6b6b; padding: 15px; margin: 10px 0; 
                        border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                        transition: transform 0.2s ease, box-shadow 0.2s ease;'>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <div style='display: flex; align-items: center;'>
                        <div style='width: 40px; height: 40px; background: linear-gradient(135deg, #667eea, #764ba2); 
                                    border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                    margin-right: 12px; font-size: 1.2rem; color: white; font-weight: bold;'>
                            {sender[0].upper()}
                        </div>
                        <div>
                            <div style='font-weight: 600; color: #333; font-size: 1.1rem;'>{sender}</div>
                            <div style='color: #666; font-size: 0.9rem;'>sent you a new message</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("💬 Open Chat", key=f"chat_{sender}", type="primary"):
                    st.session_state.selected_contact = sender
                    st.rerun()
    else:
        # Enhanced no messages state
        st.markdown("""
        <div style='text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                    border-radius: 15px; margin: 20px 0; border: 2px dashed #dee2e6;'>
            <div style='font-size: 4rem; margin-bottom: 15px; opacity: 0.5;'>📭</div>
            <h3 style='color: #6c757d; margin-bottom: 10px;'>No new messages</h3>
            <p style='color: #868e96; margin-bottom: 20px;'>Your inbox is all caught up!</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📂 Show Chat History", type="secondary"):
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
                    st.markdown("""
                    <div style='background: white; padding: 20px; border-radius: 12px; margin: 15px 0; 
                                box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                        <h4 style='color: #495057; margin-bottom: 15px; font-size: 1.2rem;'>
                            💬 Previous Conversations
                        </h4>
                    </div>
                    """, unsafe_allow_html=True)
                    for contact in sorted(unique_contacts):
                        st.markdown(f"""
                        <div style='display: flex; align-items: center; padding: 10px; margin: 5px 0; 
                                    background: #f8f9fa; border-radius: 8px; border-left: 3px solid #28a745;'>
                            <div style='width: 30px; height: 30px; background: #28a745; border-radius: 50%; 
                                        display: flex; align-items: center; justify-content: center; 
                                        margin-right: 10px; color: white; font-weight: bold; font-size: 0.9rem;'>
                                {contact[0].upper()}
                            </div>
                            <span style='color: #495057; font-weight: 500;'>{contact}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("You haven't chatted with anyone yet.")
            else:
                st.error("Failed to fetch chat history.")

            # Enhanced contact selection
    st.markdown("### 👥 Start a Conversation")
    
    default_contact = st.session_state.selected_contact
    if default_contact not in contacts:
        default_contact = None

    selected_contact = st.selectbox("Select a contact to chat with", contacts, index=contacts.index(default_contact) if default_contact else 0)
    st.session_state.selected_contact = selected_contact

    # --- Enhanced Chat Interface ---
    if selected_contact:
        # Enhanced navigation buttons        
        colA, colB, colC = st.columns(3)
        with colA:
            if st.button("⬅️ Back to Requests", type="secondary"):
                st.session_state.page = "post_request"
                st.rerun()
        with colB:
            if st.button("⬅️ Back to Talents", type="secondary"):
                st.session_state.page = "Talents"
                st.rerun()
        with colC:
            if st.button("⬅️ Back to Match Finder", type="secondary"):
                st.session_state.page = "Match"
                st.rerun()

        # Enhanced chat header
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; 
                    border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 12px rgba(79,172,254,0.3);'>
            <div style='display: flex; align-items: center;'>
                <div style='width: 50px; height: 50px; background: rgba(255,255,255,0.2); border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; margin-right: 15px; 
                            color: white; font-weight: bold; font-size: 1.3rem; backdrop-filter: blur(10px);'>
                    {selected_contact[0].upper()}
                </div>
                <div>
                    <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 600;'>{selected_contact}</h2>
                    <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>Active conversation</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Chat messages container with enhanced styling
        st.markdown("""
        <div style='background: #fafafa; padding: 20px; border-radius: 12px; margin: 20px 0; 
                    min-height: 400px; max-height: 500px; overflow-y: auto; 
                    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)

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
            
            # Enhanced message bubbles
            if is_me:
                bubble_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                text_color = "white"
                avatar_bg = "#667eea"
            else:
                bubble_bg = "white"
                text_color = "#333"
                avatar_bg = "#28a745"
                
            tick = "✔✔" if is_me and read else "✔" if is_me else ""
            tick_color = "#00ff88" if tick == "✔✔" else "rgba(255,255,255,0.7)" if is_me else "gray"

            st.markdown(
                f"""
                <div style='width: 100%; display: flex; justify-content: {"flex-end" if is_me else "flex-start"}; 
                            margin: 15px 0; animation: fadeIn 0.3s ease-in;'>
                    <div style='display: flex; align-items: flex-end; max-width: 70%; 
                                flex-direction: {"row-reverse" if is_me else "row"};'>
                        <div style='width: 35px; height: 35px; background: {avatar_bg}; border-radius: 50%; 
                                    display: flex; align-items: center; justify-content: center; 
                                    margin: {"0 0 0 10px" if is_me else "0 10px 0 0"}; color: white; 
                                    font-weight: bold; font-size: 0.9rem; flex-shrink: 0;'>
                            {sender[0].upper()}
                        </div>
                        <div style='background: {bubble_bg}; padding: 12px 16px; border-radius: 18px; 
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.1); position: relative;
                                    border-bottom-{"right" if is_me else "left"}-radius: 4px;'>
                            <div style='color: {text_color}; font-size: 0.95rem; line-height: 1.4; word-wrap: break-word;'>
                                {content}
                            </div>
                            <div style='font-size: 0.75rem; text-align: right; margin-top: 5px; 
                                        color: {"rgba(255,255,255,0.7)" if is_me else "#999"}; display: flex; 
                                        align-items: center; justify-content: flex-end; gap: 5px;'>
                                <span>{time_display}</span>
                                <span style='color: {tick_color}; font-weight: bold;'>{tick}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

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

        # Enhanced message input form
        with st.form(key="chat_form", clear_on_submit=True):
            st.markdown("**✍️ Type your message:**")
            message = st.text_area("", key="chat_input", placeholder="Write your message here...", height=100)
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                send_btn = st.form_submit_button("📤 Send Message", type="primary", use_container_width=True)

            if send_btn and message.strip():
                send_message(current_user_name, selected_contact, message.strip())
                st.session_state.last_sent = datetime.utcnow().isoformat()
                st.session_state.last_check = time.time()
                st.success("✅ Message sent successfully!")
                st.rerun()
                
        if st.session_state.get("last_sent"):
            st.markdown(f"""
            <div style='text-align: center; color: #6c757d; font-size: 0.85rem; margin-top: 10px;'>
                📤 Last sent: {st.session_state.last_sent}
            </div>
            """, unsafe_allow_html=True)

    # Add CSS animations
    st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    div[data-testid="stButton"] > button {
        transition: all 0.3s ease;
    }
    
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e9ecef;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e9ecef;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.session_state.page = None

# Talent zone
def Talent_Zone():
    url = f"https://api.airtable.com/v0/{BASE_ID}/Talent"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    # Custom CSS for enhanced UI (keeping your existing styles)
    st.markdown("""
    <style>
    .talent-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .talent-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .talent-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .service-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .service-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    .service-title {
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 0.5rem;
    }
    
    .service-info {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .info-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .price-badge {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .contact-info {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2c3e50;
        color: #2c3e50;
        font-weight: 500;
    }
    
    .section-header {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 2rem 0 1rem 0;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .search-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .form-header {
        text-align: center;
        color: #2c3e50;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid #667eea;
    }
    
    .no-services {
        text-align: center;
        padding: 3rem;
        color: #6c757d;
        font-size: 1.2rem;
        background: #f8f9fa;
        border-radius: 12px;
        margin: 2rem 0;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        min-width: 120px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Rating and Review Styles */
    .rating-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .stars {
        color: #ffd700;
        font-size: 1.2rem;
    }
    
    .rating-text {
        color: #666;
        font-size: 0.9rem;
    }
    
    .review-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    .review-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 3px solid #667eea;
    }
    
    .review-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .reviewer-name {
        font-weight: 600;
        color: #2c3e50;
    }
    
    .review-text {
        color: #555;
        line-height: 1.5;
        margin: 0.5rem 0;
    }
    
    .review-form {
        background: #e8f4fd;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #bee5eb;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header Section
    st.markdown("""
    <div class="talent-header">
        <h1>🎯 Connect</h1>
        <p>Connect, Create, and Collaborate with Amazing Talents</p>
    </div>
    """, unsafe_allow_html=True)

    # Service Posting Section (keeping your existing logic unchanged)
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">📝 Post Your Service</div>', unsafe_allow_html=True)
    
    with st.form("post_service"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Full Name", placeholder="Enter your full name (same as signup)")
            title = st.text_input("🎨 Service Title", placeholder="e.g., 'Logo Design', 'Web Development'")
            price = st.number_input("💸 Price (₦)", min_value=0, help="Set your service price")
        with col2:
            contact_pref = st.radio("📞 Preferred Contact Method", ["In-App Chat", "Phone/Email"])
            contact = st.text_input("📧 Contact Info", placeholder="Your email or phone (if using Phone/Email)")
            uploaded_files = st.file_uploader("📷 Upload Work Samples/Products", accept_multiple_files=True, type=["png", "jpg", "jpeg"], help="Upload images to showcase your work")

        description = st.text_area("🛠️ Describe Your Service", placeholder="Tell potential clients about your service, experience, and what makes you unique...")

        submit = st.form_submit_button("📤 Post Service", use_container_width=True)

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
                    "Works": "\n".join(img_urls),
                    "Reviews_Data": "[]",  # Initialize empty reviews
                    "Total_Rating": 0,
                    "Review_Count": 0
                }
            }

            try:
                response = requests.post(url, headers=headers, json=user_data)
                response.raise_for_status()
                st.success("🎉 Your service has been posted successfully!")
                st.balloons()
            except requests.exceptions.RequestException as e:
                st.error("❌ Failed to post service.")
                st.exception(e)
                st.code(response.text if 'response' in locals() else 'No response body')

    st.markdown('</div>', unsafe_allow_html=True)

    # Display Existing Services
    st.markdown('<div class="section-header">🔍 Explore Available Services</div>', unsafe_allow_html=True)

    try:
        list_response = requests.get(url, headers=headers)
        list_response.raise_for_status()
        records = list_response.json().get("records", [])

        # Stats Section (keeping your existing logic)
        if records:
            total_services = len(records)
            avg_price = sum([r["fields"].get("Price", 0) for r in records]) / len(records) if records else 0
            unique_categories = len(set([r["fields"].get("Title", "Others") for r in records]))
            
            st.markdown(f"""
            <div class="stats-container">
                <div class="stat-card">
                    <span class="stat-number">{total_services}</span>
                    <span class="stat-label">Total Services</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">₦{avg_price:,.0f}</span>
                    <span class="stat-label">Avg Price</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{unique_categories}</span>
                    <span class="stat-label">Categories</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Search and Filter Section (keeping your existing logic)
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        st.markdown("### 🔎 Search & Filter Services")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_query = st.text_input("🔍 Search by keyword", placeholder="e.g., 'design', 'development'").lower()
        with col2:
            all_titles = sorted(set([r["fields"].get("Title", "Others") for r in records]))
            selected_title = st.selectbox("🎯 Filter by Category", options=["All"] + all_titles)
        with col3:
            sort_order = st.radio("💰 Sort by", ["None", "Price: Low to High", "Price: High to Low", "Highest Rated"])
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Apply filters (keeping your existing logic with rating sort added)
        if search_query:
            records = [
                r for r in records
                if search_query in r["fields"].get("Title", "").lower()
                or search_query in r["fields"].get("Description", "").lower()
            ]

        if selected_title != "All":
            records = [r for r in records if r["fields"].get("Title") == selected_title]

        if sort_order == "Price: Low to High":
            records.sort(key=lambda r: r["fields"].get("Price", 0))
        elif sort_order == "Price: High to Low":
            records.sort(key=lambda r: r["fields"].get("Price", 0), reverse=True)
        elif sort_order == "Highest Rated":
            records.sort(key=lambda r: calculate_average_rating(r["fields"]), reverse=True)

        if not records:
            st.markdown("""
            <div class="no-services">
                <h3>🤷‍♂️ No Services Found</h3>
                <p>Try adjusting your search criteria or be the first to post a service!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h3 style='color: #2c3e50; margin: 2rem 0 1rem 0;'>📋 Found {len(records)} Service(s)</h3>", unsafe_allow_html=True)
            
            for record in records:
                fields = record.get("fields", {})
                requester = fields.get("Name", "Unknown")
                title = fields.get("Title", "No Title")
                description = fields.get("Description", "No description")
                price = fields.get("Price", 0)
                contact_pref = fields.get("Contact_pref", "Not specified")
                contact = fields.get("Contact", "Not provided")
                record_id = record["id"]

                # Calculate rating info
                avg_rating = calculate_average_rating(fields)
                review_count = fields.get("Review_Count", 0)

                # Generate star display
                if avg_rating > 0:
                    stars = "⭐" * int(round(avg_rating)) + "☆" * (5 - int(round(avg_rating)))
                    rating_text = f"({avg_rating:.1f}/5 • {review_count} reviews)"
                else:
                    stars = "☆☆☆☆☆"
                    rating_text = "(No reviews yet)"

                st.markdown(f"""
                <div class="service-card">
                    <div class="service-title">{title}</div>
                    <div class="service-info">
                        <div class="info-badge">👤 {requester}</div>
                        <div class="info-badge">📞 {contact_pref}</div>
                    </div>
                    <div class="rating-container">
                        <span class="stars">{stars}</span>
                        <span class="rating-text">{rating_text}</span>
                    </div>
                    <div class="price-badge">💸 ₦{price:,}</div>
                    <p style="color: #555; line-height: 1.6; margin: 1rem 0;">{description}</p>
                    <div class="contact-info">
                        <strong>📲 Contact:</strong> {contact if contact else "Available via " + contact_pref}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💬 Start Chat", key=f"chat_{record_id}", use_container_width=True):
                        st.session_state.selected_contact = requester
                        st.session_state.page = "chat"
                        st.rerun()
                with col2:
                    if st.button("👁 View Profile", key=f"profile_{record_id}", use_container_width=True):
                        st.session_state.selected_talent = record
                        st.session_state.page = "view_talent"
                        st.rerun()
                with col3:
                    # Toggle review form
                    review_key = f"show_review_{record_id}"
                    if st.button("⭐ Rate & Review", key=f"review_{record_id}", use_container_width=True):
                        if review_key not in st.session_state:
                            st.session_state[review_key] = False
                        st.session_state[review_key] = not st.session_state[review_key]
                        st.rerun()

                # Show review form if toggled
                if st.session_state.get(f"show_review_{record_id}", False):
                    st.markdown('<div class="review-form">', unsafe_allow_html=True)
                    st.markdown("### ⭐ Leave a Review")
                    
                    with st.form(f"review_form_{record_id}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            reviewer_name = st.text_input("Your Name", placeholder="Enter your name")
                            rating = st.selectbox("Rating", [5, 4, 3, 2, 1], format_func=lambda x: "⭐" * x + f" ({x}/5)")
                        with col2:
                            review_text = st.text_area("Your Review", placeholder="Share your experience...")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Submit Review", use_container_width=True):
                                if reviewer_name and review_text:
                                    success = add_review(record_id, reviewer_name, rating, review_text, headers, url)
                                    if success:
                                        st.success("✅ Review submitted successfully!")
                                        st.session_state[f"show_review_{record_id}"] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to submit review. Please try again.")
                                else:
                                    st.error("Please fill in all fields.")
                        with col2:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                st.session_state[f"show_review_{record_id}"] = False
                                st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)

                # Customer Reviews Section as Dropdown
                reviews_dropdown_key = f"show_reviews_{record_id}"
                reviews = get_reviews(fields)
                
                # Create expander for reviews
                with st.expander(f"💬 Customer Reviews ({len(reviews)} review{'s' if len(reviews) != 1 else ''})", expanded=False):
                    if reviews:
                        for review in reviews:
                            st.markdown(f"""
                            <div class="review-item">
                                <div class="review-header">
                                    <span class="reviewer-name">{review['name']}</span>
                                    <span style="color: #6c757d; font-size: 0.8rem;">{review['date']}</span>
                                </div>
                                <div class="stars">{"⭐" * review['rating']}</div>
                                <div class="review-text">{review['text']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="review-item">
                            <div style="text-align: center; color: #6c757d; padding: 1rem;">
                                <p>🤷‍♂️ No reviews yet</p>
                                <p>Be the first to leave a review for this service!</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    except requests.exceptions.RequestException as e:
        st.error("❌ Could not fetch services.")
        st.exception(e)

# Helper Functions
def calculate_average_rating(fields):
    """Calculate average rating from stored data"""
    total_rating = fields.get("Total_Rating", 0)
    review_count = fields.get("Review_Count", 0)
    if review_count > 0:
        return total_rating / review_count
    return 0

def get_reviews(fields):
    """Get reviews from stored JSON data"""
    import json
    try:
        reviews_data = fields.get("Reviews_Data", "[]")
        if not reviews_data:
            reviews_data = "[]"
        reviews = json.loads(reviews_data)
        return reviews
    except:
        return []

def add_review(record_id, reviewer_name, rating, review_text, headers, url):
    """Add a new review to the service"""
    import json
    from datetime import datetime
    
    try:
        # Get current record
        response = requests.get(f"{url}/{record_id}", headers=headers)
        response.raise_for_status()
        current_data = response.json()
        fields = current_data.get("fields", {})
        
        # Get current reviews
        current_reviews = get_reviews(fields)
        
        # Add new review
        new_review = {
            "name": reviewer_name,
            "rating": rating,
            "text": review_text,
            "date": datetime.now().strftime("%B %d, %Y")
        }
        current_reviews.append(new_review)
        
        # Update totals
        current_total = fields.get("Total_Rating", 0)
        current_count = fields.get("Review_Count", 0)
        
        new_total = current_total + rating
        new_count = current_count + 1
        
        # Update record
        update_data = {
            "fields": {
                "Reviews_Data": json.dumps(current_reviews),
                "Total_Rating": new_total,
                "Review_Count": new_count
            }
        }
        
        update_response = requests.patch(f"{url}/{record_id}", headers=headers, json=update_data)
        update_response.raise_for_status()
        return True
        
    except Exception as e:
        print(f"Error adding review: {e}")
        return False

#Profile in talent zone
def view_talent_profile():
    # Back button with improved styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Back to Talent Zone", type="secondary", use_container_width=True):
            st.session_state.page = "Talent zone"
            st.rerun()
    
    talent = st.session_state.get("selected_talent")
    if not talent:
        st.error("⚠️ No talent selected. Please return to the talent zone and select a profile.")
        return
    
    # Extract data
    fields = talent.get("fields", {})
    name = fields.get("Name", "No Name")
    title = fields.get("Title", "No Title")
    description = fields.get("Description", "No description")
    price = fields.get("Price", 0)
    contact_pref = fields.get("Contact_pref", "Not specified")
    contact = fields.get("Contact", "Not provided")
    works_raw = fields.get("Works", "")
    
    # Header section with enhanced styling
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        ">
            <div style="
                width: 80px;
                height: 80px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                margin: 0 auto 1rem auto;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                backdrop-filter: blur(10px);
            ">👤</div>
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">{name}</h1>
            <h3 style="margin: 0.5rem 0 0 0; opacity: 0.9; font-weight: 400;">{title}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Main content in two columns
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        # Description section
        st.markdown(
            f"""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border-left: 4px solid #667eea;
                margin-bottom: 1.5rem;
            ">
                <h4 style="color: #333; margin-bottom: 1rem; display: flex; align-items: center;">
                    <span style="margin-right: 0.5rem;">📝</span>About
                </h4>
                <p style="color: #666; line-height: 1.6; margin: 0;">{description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Portfolio section
        st.markdown(
            """
            <div style="margin-bottom: 1rem;">
                <h4 style="color: #333; display: flex; align-items: center; margin-bottom: 1rem;">
                    <span style="margin-right: 0.5rem;">🎨</span>Portfolio & Work Samples
                </h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if works_raw:
            urls = [u.strip() for u in works_raw.split("\n") if u.strip()]
            if urls:
                # Create a responsive grid for images
                num_cols = min(len(urls), 3) if len(urls) > 2 else 2
                cols = st.columns(num_cols, gap="medium")
                
                for i, url in enumerate(urls):
                    with cols[i % num_cols]:
                        st.markdown(
                            f"""
                            <div style="
                                background: white;
                                border-radius: 12px;
                                overflow: hidden;
                                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                                transition: transform 0.3s ease;
                                margin-bottom: 1rem;
                            ">
                            """,
                            unsafe_allow_html=True
                        )
                        try:
                            st.image(url, use_container_width=True)
                        except:
                            st.markdown(
                                f"""
                                <div style="
                                    padding: 2rem;
                                    text-align: center;
                                    color: #999;
                                    background: #f8f9fa;
                                ">
                                    <p>🖼️ Image unavailable</p>
                                    <small>{url[:50]}...</small>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    """
                    <div style="
                        background: #f8f9fa;
                        padding: 2rem;
                        border-radius: 12px;
                        text-align: center;
                        color: #666;
                        border: 2px dashed #ddd;
                    ">
                        <h5>📁 No work samples available</h5>
                        <p>This talent hasn't uploaded any portfolio items yet.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div style="
                    background: #f8f9fa;
                    padding: 2rem;
                    border-radius: 12px;
                    text-align: center;
                    color: #666;
                    border: 2px dashed #ddd;
                ">
                    <h5>📁 No work samples available</h5>
                    <p>This talent hasn't uploaded any portfolio items yet.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with col2:
        # Pricing card
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
                margin-bottom: 1.5rem;
            ">
                <h4 style="margin: 0 0 0.5rem 0; opacity: 0.9;">Starting Price</h4>
                <h2 style="margin: 0; font-size: 2rem; font-weight: 700;">₦{price:,}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Contact information card
        st.markdown(
            f"""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                margin-bottom: 1.5rem;
            ">
                <h4 style="color: #333; margin-bottom: 1rem; display: flex; align-items: center;">
                    <span style="margin-right: 0.5rem;">📞</span>Contact Information
                </h4>
                <div style="
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 1rem;
                ">
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">Preferred Method</p>
                    <p style="margin: 0.25rem 0 0 0; color: #333; font-weight: 600;">{contact_pref}</p>
                </div>
            """,
            unsafe_allow_html=True
        )
        
        # Show contact details if phone/email is preferred
        if contact_pref == "Phone/Email" and contact != "Not provided":
            st.markdown(
                f"""
                <div style="
                    background: #e3f2fd;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid #2196F3;
                ">
                    <p style="margin: 0; color: #1976D2; font-weight: 600;">📧 {contact}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Clear page state after loading profile
    st.session_state.page = None

def update_profile():
    st.title("⚙️ Update Your Talent Profile")

    current_user = st.session_state.get("current_user")
    if not current_user:
        st.error("You gotta be logged in to update your profile.")
        return

    user_name = current_user.get("Name")

    url = f"https://api.airtable.com/v0/{BASE_ID}/Talent"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params={"filterByFormula": f"Name='{user_name}'"})
    if not response.ok:
        st.error("Failed to load profile data.")
        return

    records = response.json().get("records", [])
    if not records:
        st.error("User profile not found.")
        return

    user_record = records[0]
    record_id = user_record["id"]
    fields = user_record.get("fields", {})
    


    # Pre-fill form fields
    with st.form("update_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("👤 Full Name", value=fields.get("Name", ""))
            new_Title = st.text_input("🎨 Service Title", value=fields.get("Title", ""))
            new_Price = st.number_input("💸 Price (₦)", min_value=0, value=fields.get("Price", 0))
        with col2:
            new_contact_pref = st.radio("📞 Preferred Contact Method(IMPORTANT)", ["In-App Chat", "Phone/Email"])
            new_contact = st.text_input("📧 Contact Info", value=fields.get("Contact", ""))
            new_uploaded_files = st.file_uploader("📷 Upload Work Samples", accept_multiple_files=True, type=["png", "jpg", "jpeg"])
            image_handling = st.radio("🖼️ What do you want to do with your work samples?", [
            "Keep existing and add new",
            "Replace all with new uploads",
            "Remove all images"
            ])


        new_description = st.text_area("🛠️ Describe Your Service", value=fields.get("Description", ""))

        submitted = st.form_submit_button("Save Changes")

        if submitted:
            # Step 1: Initialize image list and upload if any
            new_image_urls = []
            if new_uploaded_files:
                for file in new_uploaded_files:
                    try:
                        file_bytes = file.read()
                        image_url = upload_image_to_cloudinary(file_bytes, file.name)

                        if isinstance(image_url, str):
                            new_image_urls.append(image_url)
                            st.success(f"✅ Uploaded: {file.name}")
                        else:
                            st.warning(f"❌ Failed to get URL for {file.name}")
                    except Exception as e:
                        st.error(f"❌ Error uploading {file.name}")
                        st.exception(e)

            # Step 2: Handle image logic based on selected option
            if image_handling == "Keep existing and add new":
                old_urls = fields.get("Works", "").split("\n") if fields.get("Works") else []
                combined_urls = old_urls + new_image_urls
            elif image_handling == "Replace all with new uploads":
                combined_urls = new_image_urls
            elif image_handling == "Remove all images":
                combined_urls = []

            # Step 3: Build update payload
            update_data = {
                "fields": {
                    "Name": new_name,
                    "Title": new_Title,
                    "Description": new_description,
                    "Price": new_Price,
                    "Contact_pref": new_contact_pref,
                    "Contact": new_contact,
                    "Works": "\n".join(combined_urls) if combined_urls else None
                }
            }

            update_url = f"{url}/{record_id}"
            update_response = requests.patch(update_url, headers=headers, json=update_data)

            if update_response.ok:
                st.success("Profile updated successfully!")
                st.session_state.current_user = update_response.json().get("fields", {})
                st.rerun()
            else:
                st.error("Failed to update profile.")
                st.write(update_response.text)




# post requests
def post_request():
    url = f"https://api.airtable.com/v0/{BASE_ID}/Request"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    # Custom CSS for enhanced UI
    st.markdown("""
    <style>
    .request-hero {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 15px 35px rgba(255, 154, 158, 0.3);
    }
    
    .request-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .request-hero h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 2;
    }
    
    .request-hero p {
        font-size: 1.3rem;
        opacity: 0.95;
        margin: 0;
        position: relative;
        z-index: 2;
    }
    
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .info-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .info-card li {
        padding: 0.8rem 0;
        font-size: 1.1rem;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .info-card li:last-child {
        border-bottom: none;
    }
    
    .request-form-container {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid #f0f2f5;
        position: relative;
    }
    
    .request-form-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #ff9a9e, #fecfef, #667eea, #764ba2);
        border-radius: 20px 20px 0 0;
    }
    
    .form-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        position: relative;
    }
    
    .form-title::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #ff9a9e, #fecfef);
        border-radius: 2px;
    }
    
    .request-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border-left: 6px solid #ff9a9e;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .request-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, rgba(255,154,158,0.1) 0%, transparent 100%);
        border-radius: 0 0 0 100px;
    }
    
    .request-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
        border-left-color: #667eea;
    }
    
    .request-title {
        color: #2c3e50;
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 2;
    }
    
    .request-details {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .detail-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9a9e;
        position: relative;
        z-index: 2;
    }
    
    .detail-label {
        font-weight: 600;
        color: #495057;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .detail-value {
        color: #2c3e50;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .budget-highlight {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-size: 1.2rem;
        font-weight: 700;
        display: inline-block;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(17, 153, 142, 0.3);
    }
    
    .contact-section {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: #2d3436;
        position: relative;
        z-index: 2;
    }
    
    .contact-section h4 {
        margin: 0 0 1rem 0;
        font-weight: 600;
    }
    
    .section-header {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #2c3e50;
        padding: 2rem;
        border-radius: 15px;
        margin: 3rem 0 2rem 0;
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        box-shadow: 0 10px 25px rgba(168, 237, 234, 0.3);
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 15px solid transparent;
        border-right: 15px solid transparent;
        border-top: 15px solid #fed6e3;
    }
    
    .no-requests {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        margin: 2rem 0;
    }
    
    .no-requests h3 {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .no-requests p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .chat-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        position: relative;
        z-index: 2;
    }
    
    .chat-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-item {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(116, 185, 255, 0.3);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero Header
    st.markdown("""
    <div class="request-hero">
        <h1>✨ Request Zone</h1>
        <p>Need help? Post your request and connect with talented people!</p>
    </div>
    """, unsafe_allow_html=True)

    # Info Card
    st.markdown("""
        <div class='info-card'>
            <ul>
                <li>🙆‍♂️ <b>Need help in a task</b> – Find people who are skilled at the task</li>
                <li>🖊 <b>Just fill the form</b> – Wait for users to respond</li>
                <li>🔍 <b>Talent zone</b> – You can manually look for people with skills by going to the talent zone</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Request Form
    st.markdown('<div class="request-form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-title">📝 Post Your Request</div>', unsafe_allow_html=True)

    with st.form("post_request_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Full Name", placeholder="Make sure it's the same name you used to signup")
            request_title = st.text_input("🎯 What do you need?", placeholder="e.g., 'Help with video editing', 'Logo design needed'")
            budget = st.number_input("💸 Budget (₦)", min_value=0, help="How much are you willing to pay?")
        with col2:
            deadline = st.text_input("⏰ Deadline", placeholder="e.g., 'Next week', '3 days', 'ASAP'")
            contact_method = st.radio("📞 Preferred Contact Method", ["In-App Chat", "Phone/Email"])
            contact_info = st.text_input("📧 Contact Details", placeholder="Phone number or email (optional)")
        details = st.text_area("📋 Request Details", placeholder="Describe what you need in detail. Be specific about requirements, expectations, and any important information...")
                
        submit_request = st.form_submit_button("🚀 Post Request", use_container_width=True)

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
                st.success("✅ Your Request has been posted successfully!")
                st.balloons()
            except requests.exceptions.RequestException as e:
                st.error("❌ Failed to post Request.")
                st.exception(e)
                st.code(response.text if 'response' in locals() else 'No response body')

    st.markdown('</div>', unsafe_allow_html=True)

    # Browse Requests Section
    st.markdown('<div class="section-header">🔎 Browse Open Requests</div>', unsafe_allow_html=True)
    
    try:
        list_response = requests.get(url, headers=headers)
        list_response.raise_for_status()
        records = list_response.json().get("records", [])

        if not records:
            st.markdown("""
            <div class="no-requests">
                <h3>📭 No Requests Yet</h3>
                <p>Be the first to post a request and find the help you need!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Stats Section
            total_requests = len(records)
            total_budget = sum([r["fields"].get("Budget", 0) for r in records])
            avg_budget = total_budget / len(records) if records else 0
            urgent_requests = len([r for r in records if "asap" in r["fields"].get("Deadline", "").lower() or "urgent" in r["fields"].get("Details", "").lower()])
            
            st.markdown(f"""
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-number">{total_requests}</span>
                    <span class="stat-label">Active Requests</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">₦{avg_budget:,.0f}</span>
                    <span class="stat-label">Average Budget</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{urgent_requests}</span>
                    <span class="stat-label">Urgent Requests</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            for record in records:
                fields = record.get("fields", {})
                requester_name = fields.get("Name", "Unknown")
                request_title = fields.get('Request', 'No Title')
                details = fields.get('Details', 'No details')
                budget = fields.get('Budget', 0)
                deadline = fields.get('Deadline', 'Not specified')
                contact_pref = fields.get('Contact_pref', 'Not specified')
                contact = fields.get('Contact', 'N/A')

                st.markdown(f"""
                <div class="request-card">
                    <div class="request-title">{request_title}</div>
                    <div class="request-details">
                        <div class="detail-item">
                            <div class="detail-label">👤 Requester</div>
                            <div class="detail-value">{requester_name}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">📆 Deadline</div>
                            <div class="detail-value">{deadline}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">📞 Contact Method</div>
                            <div class="detail-value">{contact_pref}</div>
                        </div>
                    </div>
                    <div class="budget-highlight">💰 Budget: ₦{budget:,}</div>
                    <p style="color: #555; line-height: 1.7; margin: 1.5rem 0; font-size: 1.1rem;"><b>📝 Details:</b> {details}</p>
                    <div class="contact-section">
                        <h4>📱 Contact Information</h4>
                        <p><strong>Method:</strong> {contact_pref}</p>
                        <p><strong>Details:</strong> {contact if contact != 'N/A' else 'Available via ' + contact_pref}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("💬 Start Chat", key=f"chat_{record['id']}", use_container_width=True):
                        st.session_state.selected_contact = requester_name
                        st.session_state.page = "chat"
                        st.rerun()

    except requests.exceptions.RequestException as e:
        st.error("❌ Could not fetch requests.")
        st.exception(e)


# ------------------ Navigation ------------------
# Enhanced Navigation with improved UI/UX
import streamlit as st

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .nav-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .user-info {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        color: white;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .nav-section {
        margin-bottom: 1.5rem;
    }
    
    .nav-section-title {
        color: #4a5568;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        padding-left: 0.5rem;
        border-left: 3px solid #667eea;
    }
    
    .logout-warning {
        background-color: #fed7d7;
        border: 1px solid #fc8181;
        border-radius: 6px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        color: #742a2a;
    }
    
    .stRadio > div {
        gap: 0.5rem;
    }
    
    .stRadio > div > label {
        background-color: #2d3748;
        color: #e2e8f0 !important;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        border: 1px solid #4a5568;
        transition: all 0.2s ease;
    }
    
    .stRadio > div > label:hover {
        background-color: #4a5568;
        border-color: #667eea;
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .stRadio > div > label > div {
        color: #e2e8f0 !important;
    }
    
    .stRadio > div > label:hover > div {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Navigation Header
st.sidebar.markdown("""
<div class="nav-header">
    🔗 Navigation Hub
</div>
""", unsafe_allow_html=True)

# Enhanced User Info Display
if st.session_state.logged_in:
    user_name = st.session_state.current_user.get("Name", "Guest")
    st.sidebar.markdown(f"""
    <div class="user-info">
        👤 Welcome, {user_name}!
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class="user-info">
        👋 Welcome, Guest!
    </div>
    """, unsafe_allow_html=True)

# Navigation Logic with Enhanced Organization
if not st.session_state.logged_in:
    # Guest Navigation
    st.sidebar.markdown('<div class="nav-section-title">🌟 Get Started</div>', unsafe_allow_html=True)
    page = st.sidebar.radio("Choose your path:", ["🏠 Home", "🔐 Login", "✍️ Sign Up"], key="nav_guest")
else:
    # Authenticated User Navigation - Organized by Categories
    
    # Main Actions
    st.sidebar.markdown('<div class="nav-section-title">🎯 Main Hub</div>', unsafe_allow_html=True)
    main_options = ["🏠 Home","✍️ Update Profile", "🤝 Match Finder", "📋 View Students","💬 Chats"]
    
    # Profile & Management
    st.sidebar.markdown('<div class="nav-section-title">👤 Profile & Settings</div>', unsafe_allow_html=True)
    profile_options = [ "🔗 Connect", "📥 Service Requests","⚙️ Update Your Business/Service profile"]
    
    # Discovery & Connect
    st.sidebar.markdown('<div class="nav-section-title">🔍 Discover & Connect</div>', unsafe_allow_html=True)
    discover_options = []
    
    # Combine all options for radio
    all_options = main_options + profile_options + discover_options + ["🚪 Logout"]
    page = st.sidebar.radio("Navigate to:", all_options, key="nav_authenticated")
    
    # Handle special page redirects from session state
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

# Page Routing Logic (unchanged to preserve functionality)
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
    # Enhanced logout confirmation
    st.sidebar.markdown("""
    <div class="logout-warning">
        ⚠️ <strong>Logout Confirmation</strong><br>
        You're about to end your session.
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🔓 Confirm Logout", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = {}
        st.success("✅ Successfully logged out!")
        st.rerun()
        
elif page == "💬 Chats":
    show_chats()
elif page == "🛠 Talent Zone":
    Talent_Zone()
elif page == "📥 Service Requests":
    post_request()
elif page == "🔍 View Talent":
    view_talent_profile()
elif page == "post_request":
    post_request()
elif page == "Talents":
    Talent_Zone()
elif page == "Match":
    show_matches()
elif page == "🔗 Connect":
    Talent_Zone()
elif page == "⚙️ Update Your Business/Service profile":
    update_profile()