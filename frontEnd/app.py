import streamlit as st
from agents import create_chat_session, send_message
from calendar_tools import get_today_date
from google import genai
from history import load_history,save_history
import json


def main():
    st.set_page_config(
        page_title="Orbter calendar AI Agent",
        page_icon="📅",
        layout="wide"
    )
    
    st.title("Orbter calendar AI Agent 📅")
    st.markdown("Ask me to create calendars, add events, or view your schedule!")
    if 'gemini_client' not in st.session_state:
        st.session_state.gemini_client = genai.Client()
    # Initialize chat session in session state
    if 'chat_session' not in st.session_state:
        try:
            st.session_state.chat_session = create_chat_session(st.session_state.gemini_client)
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"Failed to initialize chat: {str(e)}")
            st.error("Please make sure you have set up your Google API credentials and Gemini API key.")
            st.session_state.initialized = False
    
    # Initialize messages in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show function call info if present
            if "function_call" in message and message["function_call"]:
                with st.expander("🔧 Function Call Details"):
                    st.write(f"**Function:** {message['function_call']['name']}")
                    st.json(message['function_call']['args'])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your calendar..."):
        if not st.session_state.initialized:
            st.error("Chat session not initialized. Please check your API credentials and refresh the page.")
            return
        
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response_text, function_call_info = send_message(
                        st.session_state.chat_session, 
                        prompt
                    )
                    
                    if function_call_info:
                        with st.expander("🔧 Function Call Details"):
                            st.write(f"**Function:** {function_call_info['name']}")
                            st.json(function_call_info['args'])
                    
                    # Display assistant message
                    st.markdown(response_text)
                    
                    # Add assistant message to chat history
                    assistant_message = {"role": "assistant", "content": response_text, "function_call": function_call_info}
                    st.session_state.messages.append(assistant_message)
                    history_turn = {"user": prompt, "assistant": response_text}
                    save_history('Gemini_history.json', history_turn)
                except Exception as e:
                    error_message = f"❌ An error occurred: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message,
                        "function_call": None
                    })
    
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
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = load_history('Gemini_history.json')
            st.session_state.chat_session = create_chat_session(st.session_state.gemini_client)
            st.rerun()
        
        st.divider()
        
        try:
            current_date = get_today_date()
            st.caption(f"📅 Today's date: {current_date}")
        except:
            st.caption("📅 Date: Unable to fetch")
        
        st.caption("🌍 Timezone: Asia/Jerusalem")
        
        st.divider()
        st.caption("Powered by Google Gemini 2.5 Flash")


if __name__ == "__main__":
    main()