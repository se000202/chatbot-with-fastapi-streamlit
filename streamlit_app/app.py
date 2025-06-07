import streamlit as st
import requests
import os

# API URL 설정
API_URL = os.getenv("FASTAPI_URL")

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

# Send 버튼
if st.button("Send"):
    if st.session_state[st.session_state.user_input_key].strip() != "":
        # user message 추가
        st.session_state.messages.append({
            "role": "user",
            "content": st.session_state[st.session_state.user_input_key]
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
            response = requests.post(
                API_URL,
                json={"messages": st.session_state.messages}
            )

            if response.status_code == 200:
                bot_reply = response.json()["response"]
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Exception: {str(e)}")

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
