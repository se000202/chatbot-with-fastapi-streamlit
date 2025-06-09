# ✅ app.py — Streamlit with Streaming + 개선된 reply_box 동기화

import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# API URL 설정
API_URL = os.getenv("FASTAPI_URL")
if not API_URL:
    st.error("❌ API_URL is not set! Please check your environment variables.")
    st.stop()

# messages 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# user_input_key_num 및 user_input_key 초기화
if "user_input_key_num" not in st.session_state:
    st.session_state.user_input_key_num = 0
if "user_input_key" not in st.session_state:
    st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

# UI 구성
st.title("🗨️ Chatbot with Streaming + Context (FastAPI + GPT)")

# 이전 대화 표시
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] != "system":
        if msg["role"] == "user":
            st.write(f"🧑‍💻 **You:** {msg['content']}")
        elif msg["role"] == "assistant":
            if i == len(st.session_state.messages) - 1 and st.session_state.get("streaming", False):
                # streaming 중인 마지막 메시지라면 빈 자리만 출력
                reply_box = st.empty()
            else:
                st.markdown(msg['content'])

# 사용자 입력
user_input = st.text_area("Your message:", height=100, key=st.session_state.user_input_key)

# 일반 Send 버튼
if st.button("Send"):
    user_input_value = st.session_state.get(st.session_state.user_input_key, "").strip()

    if user_input_value != "":
        st.session_state.messages.append({
            "role": "user",
            "content": user_input_value
        })

        # 입력창 초기화
        st.session_state.user_input_key_num += 1
        st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

        with st.spinner("Assistant is typing..."):
            response = requests.post(
                API_URL,
                json={"messages": st.session_state.messages}
            )

            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if "response" in resp_json:
                        bot_reply = resp_json["response"]
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    else:
                        st.error(f"❌ Invalid response format: {resp_json}")
                except Exception as e:
                    st.error(f"❌ Error parsing JSON: {str(e)}\nResponse text: {response.text}")
            else:
                st.error(f"❌ Error {response.status_code}: {response.text}")

        st.rerun()

# ⭐️ Streaming Send 버튼 개선: reply_box 동기화
if st.button("Send (Streaming)"):
    user_input_value = st.session_state.get(st.session_state.user_input_key, "").strip()

    if user_input_value != "":
        st.session_state.messages.append({
            "role": "user",
            "content": user_input_value
        })

        st.session_state.user_input_key_num += 1
        st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

        # 빈 assistant 메시지 미리 추가하고 streaming flag 설정
        st.session_state.messages.append({
            "role": "assistant",
            "content": ""
        })
        st.session_state.streaming = True

        # Streaming call
        with st.spinner("Assistant is streaming..."):
            response = requests.post(
                API_URL,
                json={"messages": st.session_state.messages},
                stream=True
            )

            reply_box = st.empty()

            for line in response.iter_lines(decode_unicode=True):
                if line:
                    st.session_state.messages[-1]["content"] += line
                    reply_box.markdown(st.session_state.messages[-1]["content"])

        # Streaming 끝남 → flag 제거하고 rerun
        st.session_state.streaming = False
        st.rerun()

# Clear Chat 버튼
if st.button("Clear Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state.user_input_key_num += 1
    st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"
    st.rerun()
