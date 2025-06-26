import streamlit as st
import requests
import uuid

st.set_page_config(page_title="Chat with Bot", page_icon="🤖")
st.title("📱MobiAssist 🤖")
st.subheader("Your virtual assistant")
# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sender_id" not in st.session_state:
    st.session_state.sender_id = str(uuid.uuid4())
if "show_buttons" not in st.session_state:
    st.session_state.show_buttons = True
if "dynamic_buttons" not in st.session_state:
    st.session_state.dynamic_buttons = []

# --- Rasa Endpoint ---
rasa_endpoint = "http://localhost:5005/webhooks/rest/webhook"

# --- Display Previous Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Static Buttons (First Load Only) ---
if st.session_state.show_buttons:
    static_buttons = [
        {"title": "Browse Products", "payload": "what all devices do you have?"},
        {"title": "File Complaint", "payload": "I want to make a complaint"},
        {"title": "Track Orders", "payload": "show my order history"}
    ]
    cols = st.columns(len(static_buttons))
    for i, button in enumerate(static_buttons):
        with cols[i]:
            if st.button(button["title"], key=f"static_button_{i}"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": button["title"]
                })

                try:
                    response = requests.post(rasa_endpoint, json={
                        "sender": st.session_state.sender_id,
                        "message": button["payload"]
                    })
                    response.raise_for_status()
                    bot_responses = response.json()
                    for resp in bot_responses:
                        if "text" in resp:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": resp["text"]
                            })
                        if resp.get("buttons"):
                            st.session_state.dynamic_buttons = resp["buttons"]
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {e}")

                st.session_state.show_buttons = False
                st.rerun()

# --- Dynamic Buttons from Bot Response ---
if st.session_state.dynamic_buttons:
    dyn_cols = st.columns(len(st.session_state.dynamic_buttons))
    for i, button in enumerate(st.session_state.dynamic_buttons):
        with dyn_cols[i]:
            if st.button(button["title"], key=f"dynamic_button_{i}"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": button["title"]
                })

                try:
                    response = requests.post(rasa_endpoint, json={
                        "sender": st.session_state.sender_id,
                        "message": button["payload"]
                    })
                    response.raise_for_status()
                    bot_responses = response.json()
                    for resp in bot_responses:
                        if "text" in resp:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": resp["text"]
                            })
                        if resp.get("buttons"):
                            st.session_state.dynamic_buttons = resp["buttons"]
                        else:
                            st.session_state.dynamic_buttons = []  # Clear if no buttons returned
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {e}")

                st.rerun()

# --- Chat Input ---
prompt = st.chat_input("Message MobiAssist...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(rasa_endpoint, json={
            "sender": st.session_state.sender_id,
            "message": prompt
        })
        response.raise_for_status()
        bot_responses = response.json()
        for resp in bot_responses:
            if "text" in resp:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": resp["text"]
                })
            if resp.get("buttons"):
                st.session_state.dynamic_buttons = resp["buttons"]
            else:
                st.session_state.dynamic_buttons = []  # Clear if no buttons
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

    st.session_state.show_buttons = False
    st.rerun()

# --- Initial Greeting ---
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! How can I help you with our products today?"
    })
    st.session_state.show_buttons = True
    st.rerun()
