import streamlit as st

def live_chat_ui():
    st.markdown("### 💬 Live Team Chat (Demo)")
    if "live_chat" not in st.session_state:
        st.session_state.live_chat = []
    chat_input = st.text_input("Send a message to your team:", key="live_chat_input")
    if st.button("Send", key="live_chat_send") and chat_input:
        st.session_state.live_chat.append(chat_input)
    for msg in st.session_state.live_chat[-10:]:
        st.markdown(f"- {msg}")
    st.info("This is a demo. For real-time sync, connect to a backend or use Firebase/WebSocket.")

def comment_thread_ui(doc_id):
    st.markdown(f"#### 🗨️ Comments for {doc_id}")
    key = f"comments_{doc_id}"
    if key not in st.session_state:
        st.session_state[key] = []
    comment = st.text_input(f"Add a comment to {doc_id}", key=f"input_{doc_id}")
    if st.button(f"Add Comment to {doc_id}") and comment:
        st.session_state[key].append(comment)
    for c in st.session_state[key]:
        st.markdown(f"- {c}")
