import os
import requests
import uuid
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="🌤️ Travel & Weather Assistant", page_icon="🌤️")
st.title("🌤️ Travel & Weather Assistant")
st.caption(f"Backend: {BACKEND_URL}")

# Generate a persistent session_id for the user
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

# Keep local chat history for display
if "history" not in st.session_state:
    st.session_state["history"] = []

# Render past messages
for role, content in st.session_state["history"]:
    with st.chat_message("user" if role == "user" else "assistant"):
        st.markdown(content)

# Chat input
if prompt := st.chat_input("Ask about weather, activities, or where to go..."):
    st.session_state["history"].append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
         # Convert history into list[dict]
        messages = [
            {"role": role, "content": content}
            for role, content in st.session_state["history"]
        ]

        resp = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "messages": messages,
                "session_id": st.session_state["session_id"],
            },
            timeout=60,
        )

        # resp = requests.post(
        #     f"{BACKEND_URL}/chat",
        #     json={"message": prompt, "session_id": st.session_state["session_id"]},  # ✅ send session_id
        #     timeout=60,
        # )
        resp.raise_for_status()
        answer = resp.json().get("response", "")
    except Exception as e:
        answer = f"Error: {e}"

    st.session_state["history"].append(("assistant", answer))
    with st.chat_message("assistant"):
        st.markdown(answer)