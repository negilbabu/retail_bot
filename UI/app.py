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

# --- Rasa Endpoint ---
rasa_endpoint = "http://localhost:5005/webhooks/rest/webhook"

# --- Display Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Show Buttons on First Load or Refresh ---
if st.session_state.show_buttons:
    buttons = [
        {"title": "Browse Products", "payload": "what all devices do you have?"},
        {"title": "File Complaint", "payload": "I want to make a complaint"},
        {"title": "Track Orders", "payload": "show my order history"}
    ]
    cols = st.columns(len(buttons))
    for i, button in enumerate(buttons):
        with cols[i]:
            if st.button(button["title"], key=f"button_{i}"):
                # Append user message
                st.session_state.messages.append({
                    "role": "user", 
                    "content": button["title"]
                })

                # Call Rasa
                try:
                    response = requests.post(rasa_endpoint, json={
                        "sender": st.session_state.sender_id,
                        "message": button["payload"]
                    })
                    response.raise_for_status()
                    for r in response.json():
                        if "text" in r:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": r["text"]
                            })
                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {e}")

                # Hide buttons after interaction
                st.session_state.show_buttons = False
                st.rerun()

# --- Chat Input ---
prompt = st.chat_input("Message CineBot...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(rasa_endpoint, json={
            "sender": st.session_state.sender_id,
            "message": prompt
        })
        response.raise_for_status()
        for r in response.json():
            if "text" in r:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": r["text"]
                })
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

    # Hide buttons after any user input
    st.session_state.show_buttons = False
    st.rerun()

# --- Initial Assistant Message (Only First Load) ---
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! How can I help you with our products today?"
    })
    st.session_state.show_buttons = True
    st.rerun()
