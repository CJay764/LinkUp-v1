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
        <h3>Skill Connect</h3>
        <p>Showcase your abilities and discover amazing student skills:</p>
        <ul>
            <li><strong>Portfolio showcase</strong> - Display your best work</li>
            <li><strong>Skill sharing</strong> - Help others with your expertise</li>
            <li><strong>Creative discovery</strong> - Find talented peers</li>
            <li><strong>Knowledge exchange</strong> - Learn from each other</li>
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
                <strong style="color: #4A5568; font-size: 1.1rem;">Sign Up</strong><br>
                <small style="color: #718096; font-size: 0.9rem;">Create your profile with skills and learning needs</small>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">2️⃣</div>
                <strong style="color: #4A5568; font-size: 1.1rem;">Get Matched</strong><br>
                <small style="color: #718096; font-size: 0.9rem;">Our algorithm finds your perfect study partners</small>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">3️⃣</div>
                <strong style="color: #4A5568; font-size: 1.1rem;">Connect & Learn</strong><br>
                <small style="color: #718096; font-size: 0.9rem;">Chat, collaborate, and grow together</small>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">4️⃣</div>
                <strong style="color: #4A5568; font-size: 1.1rem;">Succeed</strong><br>
                <small style="color: #718096; font-size: 0.9rem;">Achieve academic goals through peer support</small>
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
            <p>"I discovered amazing graphic designers through skill connect. Now I have a team for my startup!"</p>
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
            📱 Use the sidebar to start matching, posting requests, or showcasing your Businesses<br>
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
    # Modern CSS styling (keep your existing CSS)
    st.markdown("""
    <style>
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
    }
    .login-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
        position: relative;
        overflow: hidden;
    }
    .login-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    .login-header h1 {
        color: white;
        font-size: 2.8rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    .login-header p {
        color: rgba(255,255,255,0.95);
        font-size: 1.2rem;
        margin: 1rem 0 0 0;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    .login-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
        position: relative;
    }
    .login-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        border-radius: 20px 20px 0 0;
    }
    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f8f9fa;
    }
    .card-header h3 {
        margin: 0;
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .card-icon {
        font-size: 1.8rem;
        margin-right: 0.8rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .admin-selector {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border-left: 4px solid #f39c12;
    }
    .stTextInput > div > div > input {
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #f8f9fa;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: white;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    .welcome-back {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #b8dacc;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f1b0b7 100%);
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Modern header with animation
    st.markdown("""
    <div class="login-header">
        <h1>🔐 Welcome Back</h1>
        <p>Sign in to continue your learning journey</p>
    </div>
    """, unsafe_allow_html=True)

    # Login card
    st.markdown("""
    <div class="login-card">
        <div class="card-header">
            <span class="card-icon">👤</span>
            <h3>Account Login</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Admin/User selector
    st.markdown("""
    <div class="admin-selector">
        <h4>⚙️ Login Type</h4>
        <p>Select your login type (Admin features will be available if your account has admin privileges)</p>
    </div>
    """, unsafe_allow_html=True)
    
    login_type = st.radio("", ["👤 Normal User", "⚙️ Admin"], horizontal=True)
    
    # Login form inputs
    email = st.text_input("📧 Email Address", 
                         placeholder="yourname@gmail.com",
                         help="Enter the email address you used to sign up")
    
    password = st.text_input("🔑 Password", 
                           placeholder="Enter your password", 
                           type="password", 
                           help="Manually type your password. Avoid browser auto-fill here.")

    # Login button
    login_col1, login_col2 = st.columns([1, 2])
    with login_col1:
        login_clicked = st.button("🚪 Sign In")
    
    # Login logic
    if login_clicked:
        user = find_user(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.session_state.selected_login_type = login_type

            st.markdown(f"""
            <div class="welcome-back">
                ✅ <strong>Welcome back, {user['Name']}!</strong><br>
                You're being redirected to your dashboard...
            </div>
            """, unsafe_allow_html=True)
            st.rerun()
            
        else:
            st.markdown("""
            <div class="error-message">
                ❌ <strong>Invalid credentials</strong><br>
                Please check your email and password and try again.
            </div>
            """, unsafe_allow_html=True)

    # Stylish divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Forgot password section
    st.markdown("""
    <div class="forgot-section">
        <div class="forgot-header">
            <span class="forgot-icon">🔄</span>
            <h4>Forgot Your Password?</h4>
        </div>
        <p class="info-text">
            No worries! Enter your email address below and we'll send your password to your inbox.
        </p>
    </div>
    """, unsafe_allow_html=True)

    forgot_email = st.text_input("📨 Email for password reset", 
                               key="forgot_email",
                               placeholder="Enter your registered email",
                               help="We'll send your password to this email address")
    
    if st.button("📬 Send My Password"):
        user = next((u["fields"] for u in fetch_users() if u["fields"].get("Email") == forgot_email), None)
        if user:
            sent = send_password_email(forgot_email, user["Password"])
            if sent:
                st.success("✅ Password sent! Please check your email inbox.")
            else:
                st.warning("⚠️ Could not send the email. Please try again later.")
        else:
            st.warning("⚠️ No account found with that email address.")

    st.markdown('</div>', unsafe_allow_html=True)

def show_sign_up_or_update():
    # Custom CSS for modern styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    .section-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
    }
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f2f6;
    }
    .section-header h3 {
        margin: 0;
        color: #2c3e50;
        font-size: 1.4rem;
        font-weight: 600;
    }
    .section-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    .skill-info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #2196f3;
    }
    .intent-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    .intent-card {
        flex: 1;
        padding: 1.5rem;
        border: 2px solid #e0e6ed;
        border-radius: 12px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        background: white;
    }
    .intent-card:hover {
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
    }
    .intent-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea10, #764ba210);
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border: 1px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
        color: #856404;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    .skill-tag {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .user-type-card {
        flex: 1;
        padding: 2rem;
        border: 2px solid #e0e6ed;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        background: white;
        margin: 0 0.5rem;
    }
    .user-type-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        transform: translateY(-3px);
    }
    .user-type-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea15, #764ba215);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    .user-type-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .user-type-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .user-type-desc {
        color: #6b7280;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)

    # Modern header
    st.markdown(f"""
    <div class="main-header">
        <h1>✨ {"Update Your Profile" if st.session_state.logged_in else "Join Our Community"}</h1>
        <p>{"Enhance your profile to get even better matches!" if st.session_state.logged_in else "Connect with peers and level up your skills together!"}</p>
    </div>
    """, unsafe_allow_html=True)

    # User Type Selection Section
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <span class="section-icon">🎭</span>
            <h3>What type of user are you?</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # User type selection with cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎓", key="student_type", help="Student"):
            st.session_state.user_type = "Student"
    
    with col2:
        if st.button("💼", key="business_type", help="Business"):
            st.session_state.user_type = "Business"
    
    with col3:
        if st.button("🎯", key="both_type", help="Both"):
            st.session_state.user_type = "Both"

    # Initialize user_type if not set
    if 'user_type' not in st.session_state:
        st.session_state.user_type = "Student"
    
    # Display selected user type
    user_type_options = ["Student", "Business", "Both"]
    user_type = st.radio("Select your user type:", user_type_options, 
                        index=user_type_options.index(st.session_state.user_type),
                        help="Choose how you plan to use our platform")
    
    # Update session state
    st.session_state.user_type = user_type

    # Personal Information Section
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <span class="section-icon">👤</span>
            <h3>Personal Information</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", st.session_state.current_user.get("Name", ""), 
                           help="Your full name as you'd like others to see it")
    with col2:
        email = st.text_input("Email Address *", st.session_state.current_user.get("Email", ""),
                            help="We'll use this to send you match notifications")
    
    password = st.text_input("Password *", type="password", 
                           help="Choose a strong password to secure your account")

    # Conditional sections based on user type
    if user_type == "Business":
        # For business users, skip intent and academic sections
        intent = "Business"
        college = ""
        department = ""
        what_i_know = "Business Services"
        looking_for = "Business Opportunities"
    else:
        # Intent Selection with modern cards (for Student and Both)
        st.markdown("""
        <div class="section-card">
            <div class="section-header">
                <span class="section-icon">🎯</span>
                <h3>What brings you here?</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        intent = st.radio("Select your primary goal:", ["School Course Help", "Skills"], 
                         help="Choose the main reason you're joining our platform")

        # College → Departments mapping (unchanged)
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

        # Expanded course options
        course_options = [
            "TMC121", "MTH122", "GST123", "PHY121", "PHY123", "ENT121", "CHM122", 
            "CIT141", "MTH123", "CIT121", "GET121", "ENG101", "ENG102", "MTH101",
            "CHM101", "PHY101", "BIO101", "CSC101", "ECO101", "ACC101", "MGT101",
            "POL101", "PSY101", "SOC101", "HIS101", "GEO101", "ART101", "MUS101",
            "PE101", "REL101", "PHI101", "STA101", "FRE101", "GER101", "SPA101"
        ]
        
        # Significantly expanded skill options
        skill_options = [
            # Programming & Development
            "Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go", "Rust", "Swift",
            "Kotlin", "TypeScript", "Dart", "Scala", "R", "MATLAB", "Assembly", "Perl", "Lua",
            
            # Web Development
            "HTML", "CSS", "React", "Vue.js", "Angular", "Node.js", "Express.js", "Django",
            "Flask", "FastAPI", "Next.js", "Nuxt.js", "Svelte", "jQuery", "Bootstrap",
            "Tailwind CSS", "SASS", "LESS", "Webpack", "Vite", "Gatsby", "GraphQL",
            
            # Mobile Development
            "React Native", "Flutter", "Android Development", "iOS Development", "Xamarin",
            "Ionic", "PhoneGap", "Unity Mobile", "Progressive Web Apps",
            
            # Backend & Database
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
            "Firebase", "Supabase", "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes",
            "Microservices", "API Development", "REST APIs", "GraphQL APIs",
            
            # Data Science & AI
            "Machine Learning", "Deep Learning", "Data Analysis", "Pandas", "NumPy",
            "Scikit-learn", "TensorFlow", "PyTorch", "Jupyter", "Tableau", "Power BI",
            "Data Visualization", "Statistics", "Big Data", "Hadoop", "Spark",
            "Natural Language Processing", "Computer Vision", "Neural Networks",
            
            # Design & Creative
            "Graphics Design", "UI/UX Design", "Adobe Photoshop", "Adobe Illustrator",
            "Adobe InDesign", "Figma", "Sketch", "Canva", "Blender", "3D Modeling",
            "Animation", "Video Editing", "Adobe After Effects", "Adobe Premiere Pro",
            "Photography", "Digital Art", "Logo Design", "Brand Design", "Web Design",
            
            # Business & Marketing
            "Digital Marketing", "Social Media Marketing", "SEO", "Content Marketing",
            "Email Marketing", "Google Analytics", "Facebook Ads", "Google Ads",
            "Copywriting", "Business Analysis", "Project Management", "Agile", "Scrum",
            "Leadership", "Sales", "Customer Service", "Public Speaking", "Presentation Skills",
            
            # Audio & Music
            "Musical Instrument Help", "Guitar", "Piano", "Drums", "Violin", "Singing",
            "Music Production", "Audio Engineering", "Logic Pro", "Pro Tools", "Ableton Live",
            "FL Studio", "Sound Design", "Mixing", "Mastering", "Songwriting", "Music Theory",
            
            # Gaming & Entertainment
            "How to play COD", "Game Development", "Unity", "Unreal Engine", "Game Design",
            "Streaming", "Content Creation", "YouTube", "Twitch", "Video Production",
            "Podcast Production", "Voice Acting", "Stand-up Comedy", "Writing", "Storytelling",
            
            # Languages
            "English", "Spanish", "French", "German", "Italian", "Portuguese", "Mandarin",
            "Japanese", "Korean", "Arabic", "Hindi", "Russian", "Dutch", "Swedish",
            "Norwegian", "Polish", "Turkish", "Hebrew", "Swahili", "Sign Language",
            
            # Fitness & Health
            "Personal Training", "Yoga", "Pilates", "Meditation", "Nutrition", "Cooking",
            "Baking", "Weight Training", "Cardio", "Running", "Swimming", "Cycling",
            "Martial Arts", "Boxing", "Dance", "Zumba", "CrossFit", "Rock Climbing",
            
            # Academic Subjects
            "Mathematics", "Physics", "Chemistry", "Biology", "History", "Geography",
            "Literature", "Philosophy", "Psychology", "Sociology", "Economics", "Accounting",
            "Finance", "Law", "Medicine", "Engineering", "Architecture", "Environmental Science",
            
            # Life Skills
            "Time Management", "Study Skills", "Note Taking", "Speed Reading", "Memory Techniques",
            "Critical Thinking", "Problem Solving", "Networking", "Interview Skills",
            "Resume Writing", "Financial Planning", "Budgeting", "Investing", "Real Estate",
            "Home Improvement", "Gardening", "Car Maintenance", "First Aid", "CPR",
            
            # Technology & Tools
            "Microsoft Office", "Excel", "PowerPoint", "Word", "Google Workspace",
            "Slack", "Zoom", "Teams", "Notion", "Trello", "Asana", "Jira", "Git",
            "GitHub", "Linux", "Windows", "macOS", "Cybersecurity", "Networking",
            "Hardware Troubleshooting", "3D Printing", "Arduino", "Raspberry Pi",
            
            # Arts & Crafts
            "Drawing", "Painting", "Sculpture", "Pottery", "Jewelry Making", "Knitting",
            "Crocheting", "Sewing", "Embroidery", "Woodworking", "Metalworking",
            "Leatherworking", "Calligraphy", "Origami", "Scrapbooking", "Card Making"
        ]

        stored_college = st.session_state.current_user.get("College", "")
        stored_department = st.session_state.current_user.get("Department", "")
        stored_know = st.session_state.current_user.get("What I know", [])
        stored_need = st.session_state.current_user.get("Looking For", [])

        if intent == "School Course Help":
            st.markdown("""
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">🏫</span>
                    <h3>Academic Details</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Warning box for college selection
            st.markdown("""
            <div class="warning-box">
                ⚠️ <strong>Important:</strong> After signing up, you cannot change your college selection. Please choose carefully!
            </div>
            """, unsafe_allow_html=True)

            # Select College
            college = st.selectbox("Select Your College", list(college_to_departments.keys()), 
                                 index=0 if not stored_college else list(college_to_departments.keys()).index(stored_college))

            # Department options based on selected college
            department_list = college_to_departments.get(college, [])
            department = st.selectbox("Select Your Department", department_list, 
                                    index=0 if not stored_department else department_list.index(stored_department))

            options = course_options
        else:
            college, department = "", ""
            options = skill_options

        # Bio section
        st.markdown("""
        <div class="section-card">
            <div class="section-header">
                <span class="section-icon">✍️</span>
                <h3>Tell us about yourself</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        bio = st.text_area("Short Bio", st.session_state.current_user.get("Bio", ""), 
                          help="Write a brief introduction about yourself, your interests, and what you're passionate about",
                          placeholder="Hi! I'm a passionate learner who loves technology and helping others. I enjoy coding, playing guitar, and exploring new ideas...")

        # Filter existing skills/courses so they're valid for current intent
        filtered_know = [x for x in stored_know if x in options]
        filtered_need = [x for x in stored_need if x in options]

        # Skill Matching Section
        st.markdown("""
        <div class="section-card">
            <div class="section-header">
                <span class="section-icon">🎯</span>
                <h3>Skill Matching</h3>
            </div>
            <div class="skill-info-box">
                <h4>🤝 How it works:</h4>
                <p><strong>✅ What I know:</strong> Skills or topics you can teach and help others with</p>
                <p><strong>❓ Looking For:</strong> Skills or topics you want to learn and need help with</p>
                <p>We'll match you with people who complement your skills and learning goals!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            # Handle default selection for single skill
            default_know_index = 0
            if filtered_know and len(filtered_know) > 0 and filtered_know[0] in options:
                default_know_index = options.index(filtered_know[0])
            
            what_i_know = st.selectbox("✅ What I can teach", options, 
                                     index=default_know_index,
                                     help="Select one skill you're most confident in and can help others learn")
        with col2:
            # Handle default selection for single skill
            default_need_index = 0
            if filtered_need and len(filtered_need) > 0 and filtered_need[0] in options:
                default_need_index = options.index(filtered_need[0])
                
            looking_for = st.selectbox("🎯 What I want to learn", options, 
                                     index=default_need_index,
                                     help="Select one skill you're most interested in learning")

    # For business users, add bio section
    if user_type == "Business":
        st.markdown("""
        <div class="section-card">
            <div class="section-header">
                <span class="section-icon">✍️</span>
                <h3>Tell us about your business</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        bio = st.text_area("Business Description", st.session_state.current_user.get("Bio", ""), 
                          help="Describe your business, services offered, and what makes you unique",
                          placeholder="We are a professional service provider specializing in...")

    # Submit button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 " + ("Update Profile" if st.session_state.logged_in else "Create My Profile")):
        if not name or not email or not password:
            st.warning("⚠️ Please fill in all required fields (Name, Email, Password).")
            return

        user_data = {
            "Name": name,
            "Email": email,
            "Password": password,
            "User_Type": user_type,
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
            st.balloons()  # Add celebration effect
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

                # What they know - handle both single string and list
                knows_data = f.get("What I know", "")
                if knows_data:
                    # Handle both string and list cases
                    if isinstance(knows_data, list):
                        knows_list = knows_data
                    else:
                        knows_list = [knows_data] if knows_data else []
                    
                    if knows_list:
                        st.markdown('<div class="section-title">💡 <strong>Areas of Expertise:</strong></div>', unsafe_allow_html=True)
                        knows_tags = ''.join([f'<span class="knows-tag">🌟 {skill}</span>' for skill in knows_list])
                        st.markdown(f'<div style="margin: 0.5rem 0;">{knows_tags}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="user-detail">💡 <strong>Areas of Expertise:</strong> <em style="color: #6c757d;">Open to sharing knowledge</em></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="user-detail">💡 <strong>Areas of Expertise:</strong> <em style="color: #6c757d;">Open to sharing knowledge</em></div>', unsafe_allow_html=True)

                # What they're looking for - handle both single string and list
                looking_data = f.get("Looking For", "")
                if looking_data:
                    # Handle both string and list cases
                    if isinstance(looking_data, list):
                        looking_list = looking_data
                    else:
                        looking_list = [looking_data] if looking_data else []
                    
                    if looking_list:
                        st.markdown('<div class="section-title">🔎 <strong>Seeking Help With:</strong></div>', unsafe_allow_html=True)
                        looking_tags = ''.join([f'<span class="looking-tag">🎯 {need}</span>' for need in looking_list])
                        st.markdown(f'<div style="margin: 0.5rem 0;">{looking_tags}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="user-detail">🔎 <strong>Seeking Help With:</strong> <em style="color: #6c757d;">Open to learning anything</em></div>', unsafe_allow_html=True)
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
    
    # Handle both list and string formats for current user
    current_know = current.get("What I know", [])
    current_need = current.get("Looking For", [])
    
    # Convert to sets, handling both string and list formats
    if isinstance(current_know, str):
        you_know = {current_know} if current_know else set()
    else:
        you_know = set(current_know)
        
    if isinstance(current_need, str):
        you_need = {current_need} if current_need else set()
    else:
        you_need = set(current_need)

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
            
        # Handle both list and string formats for other users
        other_know = f.get("What I know", [])
        other_need = f.get("Looking For", [])
        
        if isinstance(other_know, str):
            they_know = {other_know} if other_know else set()
        else:
            they_know = set(other_know)
            
        if isinstance(other_need, str):
            they_need = {other_need} if other_need else set()
        else:
            they_need = set(other_need)
            
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
            
        # Handle both list and string formats for other users
        other_know = f.get("What I know", [])
        other_need = f.get("Looking For", [])
        
        if isinstance(other_know, str):
            they_know = {other_know} if other_know else set()
        else:
            they_know = set(other_know)
            
        if isinstance(other_need, str):
            they_need = {other_need} if other_need else set()
        else:
            they_need = set(other_need)
            
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
            if st.button("⬅️ Back to Connect", type="secondary"):
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
                time.sleep(0.5)
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
# Enhanced Talent Zone with Chat Navigation Popup
def Talent_Zone():
    url = f"https://api.airtable.com/v0/{BASE_ID}/Talent"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    # Custom CSS for enhanced UI (keeping your existing styles + new popup styles)
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

    /* CHAT NAVIGATION POPUP STYLES */
    .navigation-popup {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4);
        border: 3px solid #ffffff;
        animation: popup-bounce 0.6s ease-out;
    }
    
    @keyframes popup-bounce {
        0% { transform: scale(0.3) translateY(-50px); opacity: 0; }
        50% { transform: scale(1.05) translateY(-10px); opacity: 0.8; }
        100% { transform: scale(1) translateY(0); opacity: 1; }
    }
    
    .popup-header {
        font-size: 2.2rem;
        margin-bottom: 0.8rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .popup-message {
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .popup-instructions {
        background: rgba(255, 255, 255, 0.15);
        padding: 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .popup-instructions h4 {
        margin: 0 0 0.8rem 0;
        font-size: 1.2rem;
        color: #ffffff;
        font-weight: 600;
    }
    
    .popup-instructions p {
        margin: 0;
        font-size: 1rem;
        color: #ffffff;
        font-weight: 500;
    }
    
    .selected-user-info {
        background: rgba(255, 255, 255, 0.2);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #ffffff;
    }
    
    .selected-user-info strong {
        color: #ffffff;
        font-size: 1.1rem;
    }

    /* UPDATED DISCLAIMER STYLES FOR MAXIMUM READABILITY */
    .disclaimer-banner {
        background: #000000;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        animation: pulse-glow 3s infinite;
        border: 3px solid #ff0000;
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4); }
        50% { box-shadow: 0 8px 25px rgba(255, 0, 0, 0.6); }
    }
    
    .disclaimer-banner h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    
    .disclaimer-banner p {
        margin: 0;
        font-size: 1rem;
        color: #ffffff;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    .safety-modal-container {
        background: #000000;
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        color: #ffffff;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
        border: 4px solid #ff0000;
    }
    
    .modal-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .modal-header h2 {
        font-size: 2.8rem;
        margin: 0 0 0.5rem 0;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.7);
        color: #ffffff;
        font-weight: 800;
    }
    
    .modal-header p {
        margin: 0;
        font-size: 1.3rem;
        color: #ffffff;
        font-weight: 600;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
    }
    
    .safety-tips {
        background: #1a1a1a;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 6px solid #00ff00;
        border: 2px solid #333333;
    }
    
    .safety-tips h3 {
        color: #ffffff;
        margin: 0 0 1.5rem 0;
        font-size: 1.5rem;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    .safety-tips ul {
        margin: 0;
        padding-left: 1.5rem;
        line-height: 1.8;
    }
    
    .safety-tips li {
        margin: 0.8rem 0;
        color: #ffffff;
        font-weight: 600;
        font-size: 1rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    .warning-box {
        background: #cc0000;
        color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(204, 0, 0, 0.4);
        border: 3px solid #ffffff;
    }
    
    .warning-box h3 {
        margin: 0 0 0.8rem 0;
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    
    .warning-box p {
        margin: 0;
        font-size: 1.1rem;
        color: #ffffff;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    .pro-tip-box {
        background: #0066cc;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 6px solid #ffffff;
        margin: 1.5rem 0;
        border: 2px solid #ffffff;
    }
    
    .pro-tip-box p {
        margin: 0;
        color: #ffffff;
        font-weight: 600;
        font-size: 1rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    # Safety Modal - Show on first visit or when user wants to see it
    if 'talent_zone_disclaimer_accepted' not in st.session_state:
        st.session_state.talent_zone_disclaimer_accepted = False
    
    # Initialize chat popup state
    if 'show_chat_navigation_popup' not in st.session_state:
        st.session_state.show_chat_navigation_popup = False
    if 'selected_chat_user' not in st.session_state:
        st.session_state.selected_chat_user = None
    
    if not st.session_state.talent_zone_disclaimer_accepted:
        # Create the safety modal using Streamlit components
        st.markdown("""
        <div class="safety-modal-container">
            <div class="modal-header">
                <h2>🛡️ Safety First!</h2>
                <p>Important Information Before You Continue</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Warning box
        st.markdown("""
        <div class="warning-box">
            <h3>⚠️ PLATFORM LIABILITY DISCLAIMER</h3>
            <p>We are NOT liable for any scams, fraudulent activities, or disputes between users. Exercise caution in all transactions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Safety tips
        st.markdown("""
        <div class="safety-tips">
            <h3>🔒 Smart Transaction Guidelines</h3>
            <ul>
                <li><strong>💳 Payment Protection:</strong> Always pay AFTER receiving satisfactory service delivery</li>
                <li><strong>🔍 Verify First:</strong> Check reviews, ratings, and previous work samples before engaging</li>
                <li><strong>📞 Communicate Clearly:</strong> Use the platform's chat feature for transparent communication</li>
                <li><strong>📋 Document Everything:</strong> Keep records of agreements, payments, and delivered work</li>
                <li><strong>🚨 Report Issues:</strong> Flag suspicious activities or disputes immediately</li>
                <li><strong>🤝 Meet Safely:</strong> If meeting in person, choose public locations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Pro tip
        st.markdown("""
        <div class="pro-tip-box">
            <p><strong>💡 Pro Tip:</strong> Trust your instincts. If something feels too good to be true or seems suspicious, it probably is. Stay vigilant!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Modal action buttons using Streamlit
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            col_accept, col_decline = st.columns(2)
            with col_accept:
                if st.button("✅ I Understand & Accept", key="accept_disclaimer", use_container_width=True):
                    st.session_state.talent_zone_disclaimer_accepted = True
                    st.rerun()
            with col_decline:
                if st.button("❌ Go Back", key="decline_disclaimer", use_container_width=True):
                    st.session_state.page = "dashboard"  # or wherever you want to redirect
                    st.rerun()
        
        return  # Don't show the rest of the page until disclaimer is accepted

    # Show Chat Navigation Popup if triggered
    if st.session_state.show_chat_navigation_popup and st.session_state.selected_chat_user:
        st.markdown(f"""
        <div class="navigation-popup">
            <div class="popup-header">💬 Chat Navigation</div>
            <div class="popup-message">
                <strong>Don't attempt to chat the user on this page!</strong><br>
                Navigate manually to the chat section by going to the navigation located on your left.
            </div>
            <div class="popup-instructions">
                <h4>📍 How to Access Chat:</h4>
                <p>1. Look at the navigation panel on your left sidebar<br>
                2. Click on "💬 Chats" from the navigation menu<br>
                3. Your selected contact will be automatically available</p>
            </div>
            <div class="selected-user-info">
                <strong>🎯 Selected Contact: {st.session_state.selected_chat_user}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons for the popup
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💬 Go to Chats Now", key="go_to_chats", use_container_width=True, type="primary"):
                st.session_state.selected_contact = st.session_state.selected_chat_user
                st.session_state.page = "chat"
                st.session_state.show_chat_navigation_popup = False
                st.rerun()
        with col2:
            if st.button("❌ Dismiss", key="dismiss_popup", use_container_width=True):
                st.session_state.show_chat_navigation_popup = False
                st.session_state.selected_chat_user = None
                st.rerun()
        with col3:
            if st.button("🔄 Select Different User", key="select_different", use_container_width=True):
                st.session_state.show_chat_navigation_popup = False
                st.session_state.selected_chat_user = None
                st.rerun()

    # Header Section
    st.markdown("""
    <div class="talent-header">
        <h1>🎯 Connect</h1>
        <p>Connect, Create, and Collaborate with Amazing Talents</p>
    </div>
    """, unsafe_allow_html=True)

    # Safety Disclaimer Banner - Always visible after acceptance
    st.markdown("""
    <div class="disclaimer-banner">
        <h3>🛡️ Stay Safe & Smart</h3>
        <p><strong>Remember:</strong> Pay after service delivery • Verify before you trust • We're not liable for scams • Report suspicious activities</p>
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


    # Add a footer disclaimer section
    st.markdown("""
    <div style="margin: 3rem 0 2rem 0; padding: 1.5rem; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #dc3545;">
        <h4 style="color: #dc3545; margin: 0 0 1rem 0; font-size: 1.1rem;">
            🚨 Final Safety Reminder
        </h4>
        <p style="margin: 0; color: #6c757d; line-height: 1.5;">
            <strong>Platform Disclaimer:</strong> This platform serves as a connection hub only. We do not guarantee service quality, 
            mediate disputes, or accept liability for transactions between users. Always exercise due diligence, verify credentials, 
            and prioritize your safety in all dealings.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Option to review safety guidelines again
    if st.button("🔄 Review Safety Guidelines Again", key="review_safety_again"):
        st.session_state.talent_zone_disclaimer_accepted = False
        st.rerun()


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
        if st.button("← Back to Connect", type="secondary", use_container_width=True):
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
                        <p>This business hasn't uploaded any portfolio items yet.</p>
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
                    <p>This business hasn't uploaded any portfolio items yet.</p>
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


# Add these functions to your code

def is_admin_user():
    """Check if current user is admin"""
    if not st.session_state.logged_in:
        return False
    
    current_user = st.session_state.current_user
    return current_user.get("Is_Admin", False) and st.session_state.get("selected_login_type") == "⚙️ Admin"

def create_announcement(title, message, admin_name, image_url=None):
    """Create a new announcement with optional image"""
    try:
        from datetime import datetime
        
        data = {
            "fields": {
                "Title": title,
                "Message": message,
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Posted_By": admin_name,
                "Active": True
            }
        }
        
        # Add image URL if provided
        if image_url:
            data["fields"]["Image_URL"] = image_url
        
        url = f"https://api.airtable.com/v0/{BASE_ID}/Announcements"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_PAT}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error creating announcement: {e}")
        return False



def delete_announcement(record_id):
    """Delete an announcement by record ID"""
    try:
        url = f"https://api.airtable.com/v0/{BASE_ID}/Announcements/{record_id}"
        headers = {"Authorization": f"Bearer {AIRTABLE_PAT}"}
        
        response = requests.delete(url, headers=headers)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting announcement: {e}")
        return False


def fetch_announcements():
    """Fetch all active announcements"""
    try:
        url = f"https://api.airtable.com/v0/{BASE_ID}/Announcements"
        headers = {"Authorization": f"Bearer {AIRTABLE_PAT}"}
        
        params = {
            "filterByFormula": "Active = TRUE()",
            "sort[0][field]": "Date",
            "sort[0][direction]": "desc"
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get("records", [])
        return []
    except Exception as e:
        st.error(f"Error fetching announcements: {e}")
        return []

def show_admin_announcements():
    """Admin page to manage announcements"""
    st.markdown("""
    <style>
    .admin-header {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 8px 25px rgba(231, 76, 60, 0.3);
    }
    .admin-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border-top: 4px solid #e74c3c;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="admin-header">
        <h1>⚙️ Admin Dashboard</h1>
        <p>Manage School Announcements</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create new announcement

# Create new announcement
    st.markdown("""
    <div class="admin-card">
        <h3>📢 Create New Announcement</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.form("new_announcement"):
        admin_name = st.text_input("👤 Your Name", placeholder="Enter your name (e.g., Principal Smith)")
        title = st.text_input("📝 Announcement Title", placeholder="Enter announcement title")
        message = st.text_area("💬 Message", placeholder="Write your announcement message here...", height=150)
    
        # Image upload
        uploaded_image = st.file_uploader("🖼️ Upload Poster/Image (Optional)", 
                                        type=["png", "jpg", "jpeg"], 
                                        help="Upload a poster or image for your announcement")
    
        if st.form_submit_button("📤 Post Announcement", type="primary"):
            if title and message and admin_name:
                image_url = None
            
                # Handle image upload
                if uploaded_image:
                    try:
                        file_bytes = uploaded_image.read()
                        image_url = upload_image_to_cloudinary(file_bytes, uploaded_image.name)
                        st.success(f"✅ Image uploaded: {uploaded_image.name}")
                    except Exception as e:
                        st.error(f"❌ Failed to upload image: {uploaded_image.name}")
                        st.exception(e)
            
            # Create announcement
            if create_announcement(title, message, admin_name, image_url):
                st.success("✅ Announcement posted successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to post announcement")
        else:
            st.warning("⚠️ Please fill in all required fields (Name, Title, Message)")
    
    
    # Show existing announcements
    st.markdown("""
    <div class="admin-card">
        <h3>📋 Existing Announcements</h3>
    </div>
    """, unsafe_allow_html=True)

    announcements = fetch_announcements()
    if announcements:
        for announcement in announcements:
            fields = announcement["fields"]
            record_id = announcement["id"]
            image_url = fields.get('Image_URL', '')
        
            col1, col2 = st.columns([4, 1])
        
            with col1:
                if image_url:
                    # Show image preview
                    st.image(image_url, width=200)
            
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border-left: 4px solid #007bff;">
                    <h4 style="margin: 0; color: #2c3e50;">{fields.get('Title', 'No Title')}</h4>
                    <p style="margin: 0.5rem 0; color: #6c757d;">{fields.get('Message', 'No Message')}</p>
                    <small style="color: #6c757d;">Posted on: {fields.get('Date', 'Unknown Date')} • By {fields.get('Posted_By', 'Admin')}</small>
                    {f'<br><small style="color: #28a745;">📷 Image attached</small>' if image_url else ''}
                </div>
                """, unsafe_allow_html=True)
        
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{record_id}", type="secondary"):
                    if delete_announcement(record_id):
                        st.success("✅ Announcement deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete announcement")
    else:
        st.info("📭 No announcements yet")



def show_student_dashboard():
    """Student dashboard with announcements"""
    st.markdown("""
    <style>
    .dashboard-header {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 8px 25px rgba(52, 152, 219, 0.3);
    }
    .announcement-card {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 5px solid #007bff;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .announcement-card:hover {
        transform: translateY(-2px);
    }
    .announcement-title {
        color: #2c3e50;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .announcement-message {
        color: #5a6c7d;
        line-height: 1.5;
        margin-bottom: 0.5rem;
    }
    .announcement-date {
        color: #95a5a6;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="dashboard-header">
        <h1>🏫 School Dashboard</h1>
        <p>Stay updated with the latest announcements</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show announcements
    st.markdown("### 📢 Latest Announcements")

    announcements = fetch_announcements()
    if announcements:
        for announcement in announcements:
            fields = announcement["fields"]
            image_url = fields.get('Image_URL', '')
        
            # Clean the HTML tags from title and message
            title = fields.get('Title', 'No Title')
            message = fields.get('Message', 'No Message')
        
            # Remove HTML tags
            import re
            title = re.sub(r'<[^>]+>', '', title).strip()
            message = re.sub(r'<[^>]+>', '', message).strip()

            if image_url:
                # Add the modal HTML and script ONCE at the top
                if 'modal_added' not in st.session_state:
                    st.markdown("""
                    <div id="imageModal" style="display: none; position: fixed; z-index: 9999; left: 0; top: 0; 
                        width: 100%; height: 100%; background-color: rgba(0,0,0,0.9);" onclick="closeImageModal()">
                        <span style="position: absolute; top: 20px; right: 35px; color: white; font-size: 40px; 
                            cursor: pointer;" onclick="closeImageModal()">&times;</span>
                        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                            <img id="modalImage" src="" style="max-width: 90%; max-height: 90%; border-radius: 10px;">
                        </div>
                    </div>
                
                    <script>
                    function openImageModal(url) {
                        document.getElementById('imageModal').style.display = 'block';
                        document.getElementById('modalImage').src = url;
                    }
                    function closeImageModal() {
                        document.getElementById('imageModal').style.display = 'none';
                    }
                    document.addEventListener('keydown', function(e) {
                        if (e.key === 'Escape') closeImageModal();
                    });
                    </script>
                    """, unsafe_allow_html=True)
                    st.session_state.modal_added = True
            
                # Announcement with image - Image on top, text below
                st.markdown(f"""
                <div class="announcement-card" style="overflow: hidden; margin-bottom: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="width: 100%; height: 280px; background-image: url('{image_url}'); 
                        background-size: contain; background-repeat: no-repeat; background-position: center; 
                        background-color: #f8f9fa; border-radius: 12px 12px 0 0; position: relative; cursor: pointer;"
                        onclick="openImageModal('{image_url}')">
                        <div style="position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.7); 
                            color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem;">
                            📅 {fields.get('Date', 'Unknown Date')}
                        </div>
                        <div style="position: absolute; bottom: 15px; right: 15px; background: rgba(0,0,0,0.7); 
                            color: white; padding: 8px 12px; border-radius: 20px; font-size: 0.8rem;">
                            🔍 Click to expand
                        </div>
                    </div>
                    <div style="padding: 1.5rem; background: white; border-radius: 0 0 12px 12px;">
                        <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.8rem; color: #2c3e50;">
                            📌 {title}
                        </div>
                        <div style="font-size: 1.1rem; line-height: 1.6; color: #34495e; margin-bottom: 1rem;">
                            {message}
                        </div>
                        <div style="font-size: 0.9rem; color: #7f8c8d; display: flex; align-items: center; gap: 10px;">
                            <span>👤 {fields.get('Posted_By', 'Admin')}</span>
                            <span>•</span>
                            <span>📢 Announcement</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Regular announcement without image
                st.markdown(f"""
                <div class="announcement-card">
                    <div class="announcement-title">📌 {title}</div>
                    <div class="announcement-message">{message}</div>
                    <div class="announcement-date">📅 {fields.get('Date', 'Unknown Date')} • By {fields.get('Posted_By', 'Admin')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📭 No announcements at the moment. Check back later!")

    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

    # Test notification button
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📢 Announcements", len(announcements))
    with col2:
        st.metric("📅 Today", "Active")
    with col3:
        st.metric("👥 Community", "Online")
    with col4:
        if st.button("🔔 Test Notification"):
            st.markdown("""
            <script>
            sendAnnouncementNotification(
                '🎉 TEST NOTIFICATION 🎉', 
                'This is a test notification to show how awesome this feature is!', 
                new Date().toLocaleDateString()
            );
            </script>
            """, unsafe_allow_html=True)
            st.success("📱 Notification sent! Check your browser!")


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
    user_type = st.session_state.current_user.get("User_Type", "Student")
    st.sidebar.markdown(f"""
    <div class="user-info">
        👤 Welcome, {user_name}!<br>
        <small>{user_type} Account</small>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class="user-info">
        👋 Welcome, Guest!
    </div>
    """, unsafe_allow_html=True)

# Navigation Logic with Enhanced Organization
# Add this to your navigation logic (replace the logged-in user section)

if not st.session_state.logged_in:
    # Guest Navigation 
    st.sidebar.markdown('<div class="nav-section-title">🌟 Get Started</div>', unsafe_allow_html=True)
    page = st.sidebar.radio("Choose your path:", ["🏠 Home", "🔐 Login", "✍️ Sign Up"], key="nav_guest")
else:
    # Check if user is admin
    is_admin = is_admin_user()
    user_type = st.session_state.current_user.get("User_Type", "Student")
    
    if is_admin:
        # Admin Navigation
        st.sidebar.markdown('<div class="nav-section-title">⚙️ Admin Panel</div>', unsafe_allow_html=True)
        admin_options = ["🏠 Home", "📢 Manage Announcements"]
        
        st.sidebar.markdown('<div class="nav-section-title">👤 Account</div>', unsafe_allow_html=True)
        account_options = ["🚪 Logout"]
        
        all_options = admin_options + account_options
        page = st.sidebar.radio("Navigate to:", all_options, key="nav_admin")
        
    elif user_type == "Business":
        # Business User Navigation (unchanged)
        st.sidebar.markdown('<div class="nav-section-title">💼 Business Hub</div>', unsafe_allow_html=True)
        main_options = ["🏠 Home","💬 Chats", "🔗 Connect", "📥 Service Requests","⚙️ Update Your Business/Service profile"]
        
        all_options = main_options + ["🚪 Logout"]
        page = st.sidebar.radio("Navigate to:", all_options, key="nav_business")
        
    elif user_type == "Student":
        # Student User Navigation with Dashboard
        st.sidebar.markdown('<div class="nav-section-title">🎯 Main Hub</div>', unsafe_allow_html=True)
        main_options = ["🏠 Home", "🏫 School Dashboard", "✍️ Update Profile", "🤝 Match Finder", "📋 View Students","💬 Chats", "📥 Service Requests"]
        
        all_options = main_options + ["🚪 Logout"]
        page = st.sidebar.radio("Navigate to:", all_options, key="nav_student")
        
    else:  # user_type == "Both"
        # Both User Navigation with Dashboard
        st.sidebar.markdown('<div class="nav-section-title">🎯 Main Hub</div>', unsafe_allow_html=True)
        main_options = ["🏠 Home", "🏫 School Dashboard", "✍️ Update Profile", "🤝 Match Finder", "📋 View Students","💬 Chats"]
        
        st.sidebar.markdown('<div class="nav-section-title">👤 Profile & Settings</div>', unsafe_allow_html=True)
        profile_options = ["🔗 Connect", "📥 Service Requests","⚙️ Update Your Business/Service profile"]
        
        all_options = main_options + profile_options + ["🚪 Logout"]
        page = st.sidebar.radio("Navigate to:", all_options, key="nav_both")

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

elif page == "📢 Manage Announcements":
    if is_admin_user():
        show_admin_announcements()
    else:
        st.error("⚠️ Access denied. Admin privileges required.")
        
elif page == "🏫 School Dashboard":
    show_student_dashboard()