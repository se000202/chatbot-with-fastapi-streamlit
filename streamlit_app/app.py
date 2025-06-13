# ✅ app.py — Streamlit 최종본 (Send → /chat, Streaming → /chat_stream + Bot 이모지 + 줄바꿈 처리)

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
st.title("💬 Chatbot with Streaming + Safe Python + LaTeX")

# reply_box 전역 선언
reply_box = st.empty()

# 이전 대화 표시
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.write(f"🧑‍💼 **You:** {msg['content']}")
    elif msg["role"] == "assistant":
        safe_content = msg["content"]
        if i == len(st.session_state.messages) - 1 and st.session_state.get("streaming", False):
            reply_box.markdown(f"🤖 **Bot:** {safe_content}", unsafe_allow_html=False)
        else:
            st.markdown(f"🤖 **Bot:** {safe_content}", unsafe_allow_html=False)

# 사용자 입력
user_input = st.text_area("Your message:", height=100, key=st.session_state.user_input_key)

# Streaming Send 버튼 (우선 Streaming만 제공)
if st.button("Send (Streaming)"):
    user_input_value = st.session_state.get(st.session_state.user_input_key, "").strip()

    if user_input_value != "":
        st.session_state.messages.append({
            "role": "user",
            "content": user_input_value
        })

        st.session_state.user_input_key_num += 1
        st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

        st.session_state.messages.append({
            "role": "assistant",
            "content": ""
        })
        st.session_state.streaming = True

        # 코드 요청인지 확인
        code_keywords = ["파이썬 코드", "python 코드", "Python function", "def compute", "코드 작성", "코드로 해결"]

        target_api = "/chat_stream"
        for keyword in code_keywords:
            if keyword in user_input_value:
                target_api = "/chat"  # 코드 실행은 일반 chat (sync) 사용 (Streaming 불필요)
                break

        with st.spinner("Assistant is streaming..."):
            response = requests.post(
                API_URL + target_api,
                json={"messages": st.session_state.messages},
                stream=(target_api == "/chat_stream")
            )

            if target_api == "/chat":
                # 일반 chat → 결과 한 번에 처리
                if response.status_code == 200:
                    try:
                        resp_json = response.json()
                        if "response" in resp_json:
                            bot_reply = resp_json["response"]
                            st.session_state.messages[-1]["content"] = bot_reply
                        else:
                            st.error(f"❌ Invalid response format: {resp_json}")
                    except Exception as e:
                        st.error(f"❌ Error parsing JSON: {str(e)}\nResponse text: {response.text}")
                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")

            else:
                # Streaming chat
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        line += "\n\n"
                        st.session_state.messages[-1]["content"] += line
                        reply_box.markdown(f"🤖 **Bot:** {st.session_state.messages[-1]['content']}", unsafe_allow_html=False)

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
