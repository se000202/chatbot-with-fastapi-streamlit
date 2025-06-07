import streamlit as st
import requests
import os
from dotenv import load_dotenv

# .env 로드 (로컬 개발 시)
load_dotenv()

# API URL 설정 (fallback 포함)
API_URL = os.getenv("FASTAPI_URL")
if not API_URL:
    st.error("❌ API_URL is not set! Please check your environment variables.")
    st.stop()

# messages 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# loading 상태 초기화
if "loading" not in st.session_state:
    st.session_state.loading = False

# user_input_key_num 및 user_input_key 초기화 (안전 패턴 ⭐️)
if "user_input_key_num" not in st.session_state:
    st.session_state.user_input_key_num = 0
if "user_input_key" not in st.session_state:
    st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

# UI 구성
st.title("🗨️ Chatbot with Context (FastAPI + GPT)")

# 이전 대화 표시
for msg in st.session_state.messages:
    if msg["role"] != "system":
        if msg["role"] == "user":
            st.write(f"🧑‍💻 **You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.write(f"🤖 **Bot:** {msg['content']}")

# 사용자 입력 (key 변경 트릭 적용 ⭐️)
user_input = st.text_input("Your message:", key=st.session_state.user_input_key)

# Debug 영역 → 현재 messages 구조 확인 ⭐️
with st.expander("🔍 Debug: Current Messages"):
    st.json(st.session_state.messages)

# Send 버튼
if st.button("Send"):
    user_input_value = st.session_state.get(st.session_state.user_input_key, "").strip()

    if user_input_value != "":
        # user message 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input_value
        })

        # 입력창 초기화 → key_num 증가 → key 재설정 ⭐️
        st.session_state.user_input_key_num += 1
        st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

        st.session_state.loading = True
        st.rerun()

# loading 상태 처리 → spinner 표시
if st.session_state.loading:
    with st.spinner("Assistant is typing..."):
        try:
            # ✅ 빈 messages 전송 방지 → 최소한 1개 이상 있어야 요청 보냄
            if len(st.session_state.messages) == 0:
                st.error("❌ Cannot send empty messages list.")
                st.session_state.loading = False
                st.rerun()

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

        except Exception as e:
            st.error(f"❌ Exception during request: {str(e)}")

        st.session_state.loading = False
        st.rerun()

# Clear Chat 버튼
if st.button("Clear Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state.loading = False

    # 입력창 초기화 → key_num 증가 → key 재설정 ⭐️
    st.session_state.user_input_key_num += 1
    st.session_state.user_input_key = f"user_input_{st.session_state.user_input_key_num}"

    st.rerun()
