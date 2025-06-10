import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("FASTAPI_URL")
if not API_URL:
    st.error("❌ FASTAPI_URL is not set! Please check your environment variables.")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
if "user_input_key_num" not in st.session_state:
    st.session_state.user_input_key_num = 0
if "user_input_key" not in st.session_state:
    st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

st.title("🧠 Chatbot (Streaming + Calculation Detection)")

# UI
reply_box = st.empty()

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.write(f"🧑‍💻 **You:** {msg['content']}")
    elif msg["role"] == "assistant":
        if i == len(st.session_state.messages) - 1 and st.session_state.get("streaming", False):
            reply_box.markdown(f"🤖 **Bot:** {msg['content']}")
        else:
            st.markdown(f"🤖 **Bot:** {msg['content']}")


# Input
user_input = st.text_area("Your message:", height=100, key=st.session_state.user_input_key)

# ✅ Trigger keywords for calculation
calc_keywords = ["합", "곱", "피보나치", "product of primes", "sum of primes", "fibonacci", "+", "-", "*", "/"]

# Unified Send (auto detection)
if st.button("Send (Streaming)"):
    user_input_value = st.session_state.get(st.session_state.user_input_key, "").strip()

    if user_input_value:
        # Append user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input_value
        })

        # Update input key
        st.session_state.user_input_key_num += 1
        st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

        # Prepare assistant message slot
        st.session_state.messages.append({"role": "assistant", "content": ""})
        st.session_state.streaming = True

        # ✅ Decide endpoint
        if any(keyword in user_input_value for keyword in calc_keywords):
            with st.spinner("Calculating..."):
                response = requests.post(
                    API_URL + "/chat",
                    json={"messages": st.session_state.messages}
                )
                if response.status_code == 200:
                    try:
                        resp_json = response.json()
                        if "response" in resp_json:
                            st.session_state.messages[-1]["content"] = resp_json["response"]
                        else:
                            st.error("❌ Invalid response format.")
                    except Exception as e:
                        st.error(f"❌ JSON decode error: {e}")
                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")
        else:
            with st.spinner("Streaming..."):
                response = requests.post(
                    API_URL + "/chat_stream",
                    json={"messages": st.session_state.messages},
                    stream=True
                )
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        st.session_state.messages[-1]["content"] += line
                        reply_box.markdown(st.session_state.messages[-1]["content"])

        st.session_state.streaming = False
        st.rerun()

# Clear Chat
if st.button("Clear Chat"):
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
    st.session_state.user_input_key_num += 1
    st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"
    st.rerun()
