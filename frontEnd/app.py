
import streamlit as st
import requests
from datetime import datetime

# Backend API URL
BACKEND_URL = "http://localhost:8000"  # Change this when deployed


def call_backend_chat(user_id: str, message: str) -> dict:
    """
    Call the backend API to process a chat message.
    
    Args:
        user_id: User identifier
        message: User's message
    
    Returns:
        Response from backend
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "user_id": user_id,
                "message": message
            },
            timeout=30  # 30 second timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend: {e}")
        return None


def get_conversation_history(user_id: str) -> list:
    """
    Get conversation history from backend.
    
    Args:
        user_id: User identifier
    
    Returns:
        List of messages
    """
    try:
        response = requests.get(
            f"{BACKEND_URL}/history/{user_id}",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get("messages", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load history: {e}")
        return []


def clear_conversation_history(user_id: str) -> bool:
    """
    Clear conversation history for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        True if successful
    """
    try:
        response = requests.delete(
            f"{BACKEND_URL}/history/{user_id}",
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to clear history: {e}")
        return False


def check_backend_health() -> bool:
    """
    Check if backend is running.
    
    Returns:
        True if backend is healthy
    """
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def main():
    st.set_page_config(
        page_title="Orbter Calendar AI Agent",
        page_icon="📅",
        layout="wide"
    )
    
    st.title("Orbter Calendar AI Agent 📅")
    st.markdown("*Now powered by FastAPI backend!*")
    
    # Check backend health
    if not check_backend_health():
        st.error("⚠️ Backend is not running!")
        st.info("Please start the backend server:")
        st.code("cd backend\npython main.py")
        st.stop()
    
    # Initialize session state for user ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"streamlit_user_{datetime.now().timestamp()}"
    
    # Initialize messages in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show function call info if present
            if "function_call" in message and message["function_call"]:
                with st.expander("🔧 Function Call Details"):
                    st.write(f"**Function:** {message['function_call']}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your calendar..."):
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response from backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Call backend API
                response_data = call_backend_chat(
                    user_id=st.session_state.user_id,
                    message=prompt
                )
                
                if response_data and response_data.get("success"):
                    response_text = response_data.get("response", "No response")
                    function_called = response_data.get("function_called")
                    
                    # Show function call if present
                    if function_called:
                        with st.expander("🔧 Function Call Details"):
                            st.write(f"**Function:** {function_called}")
                    
                    # Display assistant message
                    st.markdown(response_text)
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "function_call": function_called
                    })
                else:
                    error_msg = "❌ Failed to get response from backend"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "function_call": None
                    })
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This AI agent can help you:
        - 📝 Create new calendars
        - ➕ Add events to calendars
        - 📋 List all your calendars
        - 📅 View events in a calendar
        
        **Example prompts:**
        - "Create a calendar called 'Work'"
        - "Add a meeting tomorrow at 3pm in my Work calendar"
        - "Show me all my calendars"
        - "List events in my Work calendar"
        - "Schedule a dentist appointment next Monday at 10am"
        """)
        
        st.divider()
        
        # Backend status
        st.subheader("🔗 Backend Status")
        if check_backend_health():
            st.success("✅ Connected")
            st.caption(f"API: {BACKEND_URL}")
        else:
            st.error("❌ Disconnected")
        
        st.divider()
        
        # User info
        st.subheader("👤 User Info")
        st.caption(f"User ID: {st.session_state.user_id[:20]}...")
        
        st.divider()
        
        # Clear history button
        if st.button("🗑️ Clear Chat History"):
            if clear_conversation_history(st.session_state.user_id):
                st.session_state.messages = []
                st.success("History cleared!")
                st.rerun()
        
        # Load history button
        if st.button("📥 Load History from Backend"):
            history = get_conversation_history(st.session_state.user_id)
            if history:
                st.session_state.messages = [
                    {
                        "role": msg["role"],
                        "content": msg["message"],
                        "function_call": msg.get("function_call")
                    }
                    for msg in history
                ]
                st.success(f"Loaded {len(history)} messages!")
                st.rerun()
        
        st.divider()
        
        st.caption("🌍 Timezone: Asia/Jerusalem")
        st.caption("🤖 Powered by Gemini 2.5 Flash")
        st.caption("⚡ FastAPI Backend")
        
        st.divider()
        
        # Info about the new architecture
        with st.expander("🏗️ New Architecture"):
            st.markdown("""
            **Before:**
            Streamlit → Google Calendar
            (Everything in one place)
            
            **Now:**
            Streamlit → FastAPI Backend → Google Calendar
                                 ↓
                              Database
            
            **Benefits:**
            - 🌐 Can add WhatsApp easily
            - 👥 Multi-user support
            - 💾 Proper database
            - 🔒 Better security
            - 📈 Scalable
            """)


if __name__ == "__main__":
    main()