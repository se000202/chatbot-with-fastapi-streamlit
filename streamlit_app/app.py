# ✅ app.py — Streamlit with Streaming + session_state 업데이트 개선

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
for msg in st.session_state.messages:
    if msg["role"] != "system":
        if msg["role"] == "user":
            st.write(f"🧑‍💻 **You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(msg['content'])  # ⭐️ LaTeX 수식 포함 표시 가능

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

# ⭐️ Streaming Send 버튼 개선본
if st.button("Send (Streaming)"):
    user_input_value = st.session_state.get(st.session_state.user_input_key, "").strip()

    if user_input_value != "":
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input_value
        })

        # 입력창 초기화
        st.session_state.user_input_key_num += 1
        st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

        # ⭐️ 빈 assistant 메시지 먼저 추가 (실시간 업데이트 반영 목적)
        st.session_state.messages.append({
            "role": "assistant",
            "content": ""
        })

        # Streaming call
        with st.spinner("Assistant is streaming..."):
            response = requests.post(
                API_URL,
                json={"messages": st.session_state.messages},
                stream=True
            )

            reply_box = st.empty()  # reply_box 항상 표시용

            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # session_state에 최신 업데이트 → 기존 채팅에도 바로 반영됨
                    st.session_state.messages[-1]["content"] += line
                    reply_box.markdown(st.session_state.messages[-1]["content"])

        # rerun으로 최신 state 반영
        st.rerun()

# Clear Chat 버튼
if st.button("Clear Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state.user_input_key_num += 1
    st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"
    st.rerun()
