# app.py
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from chatbot import preprocess, get_response
from data_pipeline import save_conversation, read_conversation
import os
import html

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="FloatChat 🌊",
    page_icon="🤖",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* App base */
.stApp {
    background-color: #0f1720;
    color: #e6eef0;
    font-family: Inter, system-ui, -apple-system, "Helvetica Neue", Arial;
}
[data-testid="stSidebar"] {
    background-color: #071021;
    color: #cfeef5;
}
.sidebar-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 8px;
    color: #10a37f;
}
/* Keep enough bottom padding so the fixed input won't cover content */
main .block-container { padding-bottom: 140px; }

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "input_box" not in st.session_state:
    st.session_state.input_box = ""

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("<p class='sidebar-title'>💬 Chat History</p>", unsafe_allow_html=True)

os.makedirs("chats", exist_ok=True)
chat_files = sorted([f for f in os.listdir("chats") if f.endswith('.txt')], reverse=True)
chat_options = [cf.replace('.txt', '') for cf in chat_files]

selected = None
if chat_options:
    selected = st.sidebar.selectbox("Open chat", ["-- New Chat --"] + chat_options, index=0)
    if selected and selected != "-- New Chat --":
        # When user selects a previous chat, load it
        if st.sidebar.button("Load chat"):
            messages = read_conversation(f"{selected}.txt")
            st.session_state.chat_history = messages
            st.session_state.current_chat = selected
    if st.sidebar.button("Clear history"):
        # simple clear: remove files from folder and reset session state
        for f in chat_files:
            try:
                os.remove(os.path.join("chats", f))
            except Exception:
                pass
        st.session_state.chat_history = []
        st.session_state.current_chat = None
else:
    st.sidebar.write("No chat history yet.")

if st.sidebar.button("Start new chat"):
    st.session_state.chat_history = []
    st.session_state.current_chat = None
    # Streamlit auto re-runs on interaction; no explicit rerun needed.

# ---------------- MAIN TITLE ----------------
st.markdown("<h2 style='text-align:center; color:#10a37f;'>🌊 FloatChat - Ocean Data Assistant</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#9fbfcc;'>Ask about ARGO float data, salinity, or ocean science.</p>", unsafe_allow_html=True)


# ---------------- CHAT DISPLAY ----------------
# Render chat area using components.html so we can control scroll and layout precisely
def render_chat(messages):
    # Build simple HTML with inline styles to ensure consistent rendering inside the component iframe
    chat_items = []
    for sender, msg in messages:
        safe_msg = html.escape(str(msg))
        if sender == "user":
            chat_items.append(f"<div class=\"user-msg\">🧑 {safe_msg}</div>")
        else:
            chat_items.append(f"<div class=\"bot-msg\">🤖 {safe_msg}</div>")

    chat_html = f"""
    <html>
    <head>
    <style>
    html,body {{ height:100%; margin:0; padding:0; background: #0f1720; color: #e6eef0; font-family: Inter, Arial, sans-serif; }}
    .chat-container {{ height:100%; overflow-y: auto; display:flex; flex-direction:column; gap:8px; padding:18px; box-sizing:border-box; }}
    .user-msg, .bot-msg {{ border-radius: 12px; padding: 12px 14px; max-width: 78%; line-height:1.4; word-wrap: break-word; }}
    .user-msg {{ align-self: flex-end; background: linear-gradient(90deg,#0ea37f,#0bb98c); color: #022; box-shadow: 0 2px 8px rgba(16,163,127,0.12); }}
    .bot-msg {{ align-self: flex-start; background: #0b2430; color: #cfeef5; border: 1px solid rgba(255,255,255,0.02); }}
    </style>
    </head>
    <body>
    <div class="chat-container" id="chat-box">
    {''.join(chat_items)}
    </div>
    <script>
      // Auto-scroll to bottom
      (function() {{
        var c = document.getElementById('chat-box');
        if (c) c.scrollTop = c.scrollHeight;
      }})();
    </script>
    </body>
    </html>
    """
    # Use a height that fills the main content area; Streamlit will place this above the fixed input
    components.html(chat_html, height=720)


# ---------------- MESSAGE HANDLER ----------------
def handle_user_message():
    """Handles message when Enter or Send is pressed"""
    user_text = st.session_state.input_box.strip()
    if not user_text:
        return
    processed = preprocess(user_text)
    bot_reply = get_response(processed)

    # Append to history and persist
    st.session_state.chat_history.append(("user", user_text))
    st.session_state.chat_history.append(("bot", bot_reply))

    chat_name = st.session_state.current_chat or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    try:
        save_conversation(user_text, bot_reply, filename=f"chats/{chat_name}.txt")
    except Exception:
        # Non-fatal: if saving fails, continue
        pass
    st.session_state.current_chat = chat_name

    # Clear input
    st.session_state.input_box = ""


# ---------------- MESSAGE HANDLER ----------------




# ---------------- MESSAGE HANDLER ----------------



# Decide layout: if no chat history, show a centered welcome prompt and centered input; otherwise show chat + fixed bottom input
if not st.session_state.chat_history:
    # center prompt and input
    st.markdown("""
    <div style='height:60vh; display:flex; align-items:center; justify-content:center; flex-direction:column;'>
      <h3 style='color:#cfeef5;'>What's on the agenda today?</h3>
      <p style='color:#94bfb1; max-width:700px; text-align:center;'>Ask FloatChat about ARGO float data, salinity, or ocean science — type below and press Enter.</p>
    </div>
    """, unsafe_allow_html=True)

    # Centered input (not fixed)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.text_input("", key="input_box", placeholder="Ask anything — press Enter to send...", on_change=handle_user_message)
else:
    # Render the chat area and show fixed bottom input
    render_chat(st.session_state.chat_history)

# (message handler is defined above so callbacks can reference it)

# ---------------- INPUT BAR ----------------
# Fixed input bar at bottom of the screen (only when there is chat history)
if st.session_state.chat_history:
    st.markdown("""
    <div style='position:fixed; left:18%; bottom:18px; width:65%; z-index:9999;'>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([9, 1])
    with col1:
        st.text_input(
            "",
            key="input_box",
            label_visibility="collapsed",
            placeholder="Type a message and press Enter or click Send...",
            on_change=handle_user_message,
        )

    with col2:
        if st.button("Send"):
            handle_user_message()

    st.markdown("</div>", unsafe_allow_html=True)

# Note: Streamlit re-runs the script automatically on user interaction so explicit reruns are unnecessary.
