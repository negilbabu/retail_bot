import streamlit as st
import requests
import json
import uuid

# Your Rasa server's webhook URL
rasa_endpoint = "http://localhost:5005/webhooks/rest/webhook"

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="MobiAssist", layout="wide")
st.title("MobiAssist 🤖")

# --- Initialize Session State ---
# This ensures Streamlit remembers the conversation history and user ID across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sender_id" not in st.session_state:
    st.session_state.sender_id = str(uuid.uuid4())
# This will hold the buttons from the bot's last message
if "buttons" not in st.session_state:
    st.session_state.buttons = []

# --- Display Past Chat Messages ---
# This loop runs every time the script reruns, showing the full conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Text Input ---
# This block only runs when the user types a message in the chat box and presses Enter.
if prompt := st.chat_input("Ask me about phones or file a complaint..."):
    # Add the user's typed message to the history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the message to the Rasa server
    payload = {
        "sender": st.session_state.sender_id,
        "message": prompt
    }
    try:
        response = requests.post(rasa_endpoint, json=payload)
        response.raise_for_status()
        rasa_response = response.json()

        # Clear any buttons from the previous turn
        st.session_state.buttons = []
        
        # Process and display the bot's response(s)
        for resp in rasa_response:
            bot_message = resp.get("text")
            if bot_message:
                st.session_state.messages.append({"role": "assistant", "content": bot_message})
                with st.chat_message("assistant"):
                    st.markdown(bot_message)
            
            # If the response contains buttons, save them to be displayed later
            if resp.get("buttons"):
                st.session_state.buttons.extend(resp["buttons"])

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to Rasa server: {e}")

# --- Handle and Display Buttons ---
# This block runs every time, checking if there are buttons that need to be displayed.
if st.session_state.buttons:
    # Use columns to lay out the buttons horizontally
    cols = st.columns(len(st.session_state.buttons))
    for i, button in enumerate(st.session_state.buttons):
        with cols[i]:
            # Each button is created here. When a user clicks one, st.button() returns True.
            if st.button(button["title"], key=f"button_{i}"):
                # When a button is clicked:
                # 1. Add the button's title to the chat history to show the user's choice
                st.session_state.messages.append({"role": "user", "content": button["title"]})
                
                # 2. Send the button's payload to Rasa
                payload = {
                    "sender": st.session_state.sender_id,
                    "message": button["payload"]
                }
                try:
                    response = requests.post(rasa_endpoint, json=payload)
                    response.raise_for_status()
                    rasa_response = response.json()
                    
                    # 3. Clear the buttons so they disappear after being clicked
                    st.session_state.buttons = []
                    
                    # 4. Process the new response from Rasa
                    for resp in rasa_response:
                        bot_message = resp.get("text")
                        if bot_message:
                            st.session_state.messages.append({"role": "assistant", "content": bot_message})
                        if resp.get("buttons"):
                            st.session_state.buttons.extend(resp["buttons"])

                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to Rasa server: {e}")

                # 5. Rerun the script to immediately display the new messages
                st.rerun()