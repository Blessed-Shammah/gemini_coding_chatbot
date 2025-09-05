import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

from services.db_service import run_migrations
from services.auth_service import register_user, login_user
from services.title_service import title_from_first_message
from services.conversation_service import (
    get_user_conversations, create_conversation, 
    get_conversation_messages, add_message, update_conversation_title,
    delete_conversation
)

# ---------------------- App Config & Setup ----------------------
st.set_page_config(page_title="Gemini Coding Chatbot", page_icon="💻", layout="wide")
load_dotenv()

# Run DB migrations once on boot (idempotent)
try:
    run_migrations()
except Exception as e:
    st.sidebar.error(f"DB init error: {e}")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = (
    "You are a helpful coding assistant. Respond concisely to coding-related queries, "
    "generating code when appropriate. Use Markdown fenced code blocks with language hints "
    "(e.g., ```python) so users can copy code easily. For vague inputs like 'hi', ask for clarification."
)

# ---------------------- Session State ----------------------
if "user" not in st.session_state:
    st.session_state.user = None  # { id, email, display_name }
if "conversations" not in st.session_state:
    st.session_state.conversations = []  # list of conversation objects from DB
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "current_messages" not in st.session_state:
    st.session_state.current_messages = []
if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = False

# Session persistence - restore user from query params on first load
if not st.session_state.session_initialized:
    # Try to get user ID from URL params (simple approach)
    query_params = st.query_params
    if "user_id" in query_params:
        try:
            from services.auth_service import get_user_by_id
            user = get_user_by_id(query_params["user_id"])
            if user:
                st.session_state.user = user
                load_user_conversations()
        except:
            pass
    st.session_state.session_initialized = True

def load_user_conversations():
    """Load user's conversations from database"""
    if st.session_state.user:
        st.session_state.conversations = get_user_conversations(st.session_state.user["id"])
        # Set current conversation to most recent if none is selected
        if st.session_state.conversations and not st.session_state.current_conversation_id:
            st.session_state.current_conversation_id = st.session_state.conversations[0]["id"]
        # Clear current messages so they reload
        st.session_state.current_messages = []

def current_messages():
    """Get current conversation messages"""
    if st.session_state.current_conversation_id:
        if not st.session_state.current_messages:
            st.session_state.current_messages = get_conversation_messages(st.session_state.current_conversation_id)
    return st.session_state.current_messages

# ---------------------- Modern Styling ----------------------
st.markdown("""
<style>
/* Global Variables */
:root {
    --primary-color: #10a37f;
    --secondary-color: #f7f7f8;
    --text-primary: #343541;
    --text-secondary: #8e8ea0;
    --border-color: #e5e5e5;
    --hover-color: #f5f5f5;
    --danger-color: #ef4444;
}

/* Main App Container */
.main .block-container {
    padding: 0;
    max-width: 100%;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] > div {
    background: var(--secondary-color);
    padding: 1rem;
}

section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background: white;
    color: var(--text-primary);
    font-weight: 500;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    transition: all 0.2s ease;
    text-align: left;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--hover-color);
    border-color: var(--primary-color);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(16, 163, 127, 0.1);
}

/* Primary Button Style for Current Chat */
section[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: var(--primary-color) !important;
    color: white !important;
    border-color: var(--primary-color) !important;
}

/* Delete Button Styling */
section[data-testid="stSidebar"] .stButton button[title="Delete conversation"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid transparent !important;
    padding: 0.5rem !important;
    margin-bottom: 0.5rem;
    font-size: 1.1em;
    transition: all 0.2s ease;
}

section[data-testid="stSidebar"] .stButton button[title="Delete conversation"]:hover {
    background: var(--danger-color) !important;
    color: white !important;
    border-color: var(--danger-color) !important;
    transform: none;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    margin: 1rem 0 !important;
    border: 1px solid var(--border-color);
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

[data-testid="stChatMessage"][data-testid*="user"] {
    background: #f0f9ff !important;
    border-color: #0ea5e9;
}

[data-testid="stChatMessage"][data-testid*="assistant"] {
    background: var(--secondary-color) !important;
    border-color: var(--border-color);
}

/* Chat Input */
.stChatInput > div {
    border-radius: 25px !important;
    border: 2px solid var(--border-color) !important;
    background: white !important;
}

.stChatInput > div:focus-within {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1) !important;
}

/* Code blocks */
pre, code {
    border-radius: 10px !important;
}

/* Hide Streamlit Elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar: Auth & Chats ----------------------
with st.sidebar:
    st.subheader("💬 Previous Chats")

    # If not logged in, show auth tabs
    if not st.session_state.user:
        tab_login, tab_signup = st.tabs(["Sign in", "Create account"])

        with tab_login:
            st.write("Sign in to access your chats.")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Sign in"):
                ok, msg, user = login_user(email, password)
                if ok:
                    st.session_state.user = user
                    load_user_conversations()
                    # Set URL parameter for session persistence
                    st.query_params["user_id"] = user["id"]
                    st.success("Signed in.")
                    st.rerun()
                else:
                    st.error(msg)
            
            if st.button("Forgot Password?"):
                st.session_state.show_reset = True
                st.rerun()
            
            # Password reset form
            if st.session_state.get("show_reset", False):
                st.write("### Reset Password")
                reset_email = st.text_input("Enter your email to reset password", key="reset_email")
                if st.button("Send Reset Link"):
                    from services.auth_service import request_password_reset
                    token = request_password_reset(reset_email)
                    if token:
                        st.success(f"Reset token: {token}")
                        st.info("In production, this would be sent via email.")
                    else:
                        st.error("Email not found")
                
                st.write("### Enter Reset Token")
                reset_token = st.text_input("Reset Token", key="reset_token")
                new_password = st.text_input("New Password", type="password", key="new_password")
                if st.button("Reset Password"):
                    from services.auth_service import reset_password
                    if reset_password(reset_token, new_password):
                        st.success("Password reset successfully!")
                        st.session_state.show_reset = False
                        st.rerun()
                    else:
                        st.error("Invalid or expired token")

        with tab_signup:
            st.write("Create an account.")
            su_email = st.text_input("Email", key="signup_email")
            su_display = st.text_input("Display name", key="signup_display")
            su_password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Create account"):
                ok, msg = register_user(su_email, su_password, su_display)
                if ok:
                    st.success("Account created. Please sign in.")
                else:
                    st.error(msg)
    else:
        # Logged-in controls
        st.caption(f"Signed in as **{st.session_state.user['display_name']}**")
        if st.button("➕ New Chat", use_container_width=True):
            new_conv = create_conversation(st.session_state.user["id"], "New Chat")
            st.session_state.conversations.insert(0, new_conv)
            st.session_state.current_conversation_id = new_conv["id"]
            st.session_state.current_messages = []
            st.rerun()

        # Load conversations if not already loaded
        if st.session_state.user and not st.session_state.conversations:
            load_user_conversations()

        # Show all conversations with delete functionality
        for conv in st.session_state.conversations:
            is_current = conv["id"] == st.session_state.current_conversation_id
            label = conv["title"] or f"Chat {conv['created_at'].strftime('%m/%d')}"
            
            # Create two columns: one for chat button, one for delete button
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if st.button(
                    label, 
                    key=f"chat_{conv['id']}", 
                    use_container_width=True,
                    type="primary" if is_current else "secondary"
                ):
                    st.session_state.current_conversation_id = conv["id"]
                    st.session_state.current_messages = []  # Will reload on next access
                    st.rerun()
            
            with col2:
                if st.button(
                    "🗑️", 
                    key=f"delete_{conv['id']}", 
                    help="Delete conversation",
                    use_container_width=True
                ):
                    # Delete the conversation
                    if delete_conversation(conv["id"]):
                        # Remove from session state
                        st.session_state.conversations = [c for c in st.session_state.conversations if c["id"] != conv["id"]]
                        # If this was the current conversation, clear it
                        if st.session_state.current_conversation_id == conv["id"]:
                            st.session_state.current_conversation_id = None
                            st.session_state.current_messages = []
                            # Set to first available conversation if any
                            if st.session_state.conversations:
                                st.session_state.current_conversation_id = st.session_state.conversations[0]["id"]
                        st.rerun()

        st.divider()
        if st.button("🚪 Sign out", use_container_width=True):
            st.session_state.user = None
            st.session_state.conversations = []
            st.session_state.current_conversation_id = None
            st.session_state.current_messages = []
            if "user_id" in st.query_params:
                del st.query_params["user_id"]
            st.rerun()

# ---------------------- Main Header ----------------------
st.title("💻 Gemini Coding Chatbot")
st.caption("Ask coding questions or anything else. Type **exit** to clear the current chat.")

# If not signed in, gently gate the chat
if not st.session_state.user:
    st.info("Sign in (left sidebar) to start chatting.")
    st.stop()

# ---------------------- Chat Window ----------------------
# Ensure user is logged in and has conversations loaded
if st.session_state.user and not st.session_state.conversations:
    load_user_conversations()

messages = current_messages()

# Render messages
for msg in messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"**You**: {msg['content']}")
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Input
user_input = st.chat_input("Type your message…")

# ---------------------- Chat Logic ----------------------
if user_input:
    q = user_input.strip()

    if q.lower() == "exit":
        # Clear current conversation messages in database would require delete_messages function
        # For now, just create a new conversation
        new_conv = create_conversation(st.session_state.user["id"], "New Chat")
        st.session_state.conversations.insert(0, new_conv)
        st.session_state.current_conversation_id = new_conv["id"]
        st.session_state.current_messages = []
        st.rerun()

    # Ensure we have a current conversation
    if not st.session_state.current_conversation_id:
        new_conv = create_conversation(st.session_state.user["id"], "New Chat")
        st.session_state.conversations.insert(0, new_conv)
        st.session_state.current_conversation_id = new_conv["id"]
        st.session_state.current_messages = []

    # Save user message to database
    add_message(st.session_state.current_conversation_id, "user", q)
    st.session_state.current_messages.append({"role": "user", "content": q})

    # Build prompt
    if q.lower() in {"hi", "hello", "hey"}:
        bot_text = ("Hey there! Could you provide a specific coding question or topic? "
                    "For example, ask me to write a Python function or explain recursion.")
    else:
        history = "\n".join(
            f"User: {m['content']}" if m["role"] == "user" else f"Assistant: {m['content']}"
            for m in st.session_state.current_messages
        )
        prompt = f"{SYSTEM_PROMPT}\n\n{history}"
        try:
            resp = model.generate_content(prompt)
            bot_text = (resp.text or "").strip() or "I couldn't generate a response."
        except Exception as e:
            bot_text = f"⚠️ Error: {e}"

    # Save assistant response to database
    add_message(st.session_state.current_conversation_id, "assistant", bot_text)
    st.session_state.current_messages.append({"role": "assistant", "content": bot_text})

    # Update conversation title based on first message if it's still "New Chat"
    current_conv = next((c for c in st.session_state.conversations if c["id"] == st.session_state.current_conversation_id), None)
    if current_conv and (not current_conv["title"] or current_conv["title"] == "New Chat"):
        title = title_from_first_message(q)
        update_conversation_title(st.session_state.current_conversation_id, title)
        current_conv["title"] = title

    st.rerun()

