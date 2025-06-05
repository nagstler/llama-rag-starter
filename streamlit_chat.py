#!/usr/bin/env python3
"""
Streamlit Chat UI for Sales Operations Agent

This creates a web-based chat interface that:
1. Connects to your Flask API running on port 8000
2. Sends messages to /agent/chat endpoint
3. Displays responses in a chat format
"""

import streamlit as st
import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page Configuration
st.set_page_config(
    page_title="Sales Ops Agent",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for ChatGPT-like appearance
st.markdown("""
<style>
    /* Make the chat messages look better */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Style the captions for reasoning steps */
    .caption {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.2rem;
    }
    
    /* Style the reasoning text */
    .stMarkdown em {
        color: #666;
        font-style: normal;
    }
    
    /* Better spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("💬 Chat Controls")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()  # Force refresh
    
    # Show message count
    st.metric("Messages", len(st.session_state.messages))
    
    # Toggle for showing reasoning
    st.divider()
    show_reasoning = st.checkbox("Show Agent Reasoning", value=True)
    st.caption("Toggle to show/hide the agent's decision-making process")
    
    # Example Questions
    st.divider()
    st.header("💡 Try These Questions")
    examples = [
        "What sales data is available?",
        "Show me recent deals",
        "Analyze our top customers",
        "What's our pipeline status?"
    ]
    
    # When an example is clicked, we need to add it to the input
    for i, example in enumerate(examples):
        if st.button(f"→ {example}", key=f"example_{i}"):
            # Set a flag to process this example
            st.session_state.pending_message = example

# Main UI
st.title("🤖 Sales Operations Agent")
st.markdown("Ask questions about your sales data, deals, and customers.")

# Display Chat History
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        # For assistant messages, show with custom name
        with st.chat_message("assistant"):
            st.markdown("**🤖 Sales Operations Agent**")
            
            # Show reasoning if available and enabled
            if show_reasoning and "steps" in message and message["steps"]:
                with st.container():
                    for step in message["steps"]:
                        try:
                            if step["type"] == "thinking":
                                st.caption("🤔 Thinking")
                                st.markdown(f"_{step.get('content', 'Analyzing your request...')}_")
                            elif step["type"] == "tool_decision":
                                st.caption("🔧 Using tool")
                                text = step.get('reasoning') or step.get('content') or f"Using {step.get('tool', 'tool')}"
                                st.markdown(f"_{text}_")
                            elif step["type"] == "tool_execution":
                                st.caption("🔍 Searching")
                                st.markdown(f"_{step.get('content', 'Searching documents...')}_")
                            elif step["type"] == "tool_result":
                                st.caption("✅ Found information")
                                st.markdown(f"_{step.get('content', 'Processing results...')}_")
                            elif step["type"] == "conclusion":
                                st.caption("💡 Preparing response")
                                st.markdown(f"_{step.get('content', 'Formulating answer...')}_")
                        except Exception as e:
                            continue
                    st.markdown("---")
            
            # Display response without "### Response" header
            st.markdown(message["content"])

# Chat Input Box (always show it)
user_input = st.chat_input("What would you like to know?")

# Check if we have a pending message from example buttons
if "pending_message" in st.session_state:
    prompt = st.session_state.pending_message
    del st.session_state.pending_message
else:
    prompt = user_input

# Process the message if we have one
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display the user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show assistant response
    with st.chat_message("assistant"):
        st.markdown("**🤖 Sales Operations Agent**")
        
        
        # Container for step-by-step display
        reasoning_container = st.container()
        
        try:
            # Make API call to agent
            response = requests.post(
                f"{API_BASE_URL}/agent/chat",
                json={"message": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    steps = data.get("steps", [])
                    assistant_response = data.get("response", "No response received")
                    
                    # Show reasoning steps if enabled - simulate step by step
                    if show_reasoning and steps:
                        with reasoning_container:
                            for i, step in enumerate(steps):
                                try:
                                    # Add a small delay for visual effect
                                    time.sleep(0.5)
                                    
                                    if step["type"] == "thinking":
                                        st.caption("🤔 Thinking")
                                        st.markdown(f"_{step.get('content', 'Analyzing your request...')}_")
                                    elif step["type"] == "tool_decision":
                                        st.caption("🔧 Using tool")
                                        text = step.get('reasoning') or step.get('content') or f"Using {step.get('tool', 'tool')}"
                                        st.markdown(f"_{text}_")
                                    elif step["type"] == "tool_execution":
                                        st.caption("🔍 Searching")
                                        st.markdown(f"_{step.get('content', 'Searching documents...')}_")
                                    elif step["type"] == "tool_result":
                                        st.caption("✅ Found information")
                                        st.markdown(f"_{step.get('content', 'Processing results...')}_")
                                    elif step["type"] == "conclusion":
                                        st.caption("💡 Preparing response")
                                        st.markdown(f"_{step.get('content', 'Formulating answer...')}_")
                                except Exception as e:
                                    continue
                            
                            st.markdown("---")
                    
                    # Display the final response with streaming effect
                    response_placeholder = st.empty()
                    full_response = ""
                    
                    # Simulate streaming by revealing text gradually
                    for i in range(0, len(assistant_response), 5):
                        full_response = assistant_response[:i+5]
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(0.01)
                    
                    # Final response without cursor
                    response_placeholder.markdown(assistant_response)
                    
                    # Save to chat history with steps
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": assistant_response,
                        "steps": steps
                    })
                    
                except Exception as parse_error:
                        st.error(f"Error parsing response: {str(parse_error)}")
                        st.error(f"Raw response: {response.text}")
                        
            else:
                error_msg = f"Error: API returned status {response.status_code}"
                st.error(error_msg)
                if response.text:
                    st.error(f"Details: {response.text}")
                        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the Flask app is running on port 8000")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The agent might be processing a complex query.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")

# Footer
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("Powered by LangChain + LlamaIndex")
with col2:
    st.caption(f"💬 {len(st.session_state.messages)} messages in this session")