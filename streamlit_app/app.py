import streamlit as st
import requests
import os

# API URL 설정 (FASTAPI_URL 환경변수 or 기본값 사용)
API_URL = os.getenv("FASTAPI_URL", "https://web-production-b2180.up.railway.app/chat")
st.write(f"API_URL = {API_URL}")  # 디버그용 출력

# messages 초기화 → 반드시 먼저 해야 함!
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# loading 상태 초기화
if "loading" not in st.session_state:
    st.session_state.loading = False

# 입력창 초기화 (user_input) ⭐️
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# 디버그용: messages 상태 출력
st.write(f"Session messages count: {len(st.session_state.messages)}")

# UI 구성
st.title("🗨️ Chatbot with Context (FastAPI + GPT)")

# 이전 대화 표시
for msg in st.session_state.messages:
    if msg["role"] != "system":
        if msg["role"] == "user":
            st.write(f"🧑‍💻 **You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.write(f"🤖 **Bot:** {msg['content']}")

# 사용자 입력 (session_state를 사용해서 초기화 가능하게 구성 ⭐️)
user_input = st.text_input("Your message:", key="user_input")

# Send 버튼
if st.button("Send"):
    if st.session_state.user_input.strip() != "":
        # user message 추가
        st.session_state.messages.append({"role": "user", "content": st.session_state.user_input})
        
        # 입력창 초기화 ⭐️
        st.session_state.user_input = ""
        
        # loading 상태 ON → spinner에서 처리
        st.session_state.loading = True
        st.rerun()

# loading 상태 처리 → spinner 표시
if st.session_state.loading:
    with st.spinner("Assistant is typing..."):
        try:
            response = requests.post(
                API_URL,
                json={"messages": st.session_state.messages}
            )
            st.write(f"Response status code: {response.status_code}")  # 디버그용
            st.write(f"Response body: {response.text}")  # 디버그용

            if response.status_code == 200:
                bot_reply = response.json()["response"]
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Exception: {str(e)}")

        st.session_state.loading = False  # loading 상태 OFF
        st.rerun()  # rerun → 새 메시지 표시

# Clear Chat 버튼
if st.button("Clear Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state.loading = False
    st.session_state.user_input = ""  # 입력창도 초기화 ⭐️
    st.rerun()
