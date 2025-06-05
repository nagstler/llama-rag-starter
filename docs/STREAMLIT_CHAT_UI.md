# Streamlit Chat UI Documentation

## Overview

This document explains the implementation of the Streamlit-based chat interface for the Sales Operations Agent. The UI provides a clean, interactive way to communicate with the LangChain agent through the Flask API.

## Architecture

```
User → Streamlit UI (Port 8501) → HTTP POST → Flask API (Port 8000) → LangChain Agent → Response
         ↑                                                                              ↓
         └──────────────────────── Display Response ←──────────────────────────────────┘
```

## Key Concepts

### 1. Streamlit Execution Model

Streamlit has a unique execution model that developers must understand:

- **Full Script Rerun**: Every user interaction causes the entire Python script to execute from top to bottom
- **Session State**: Special dictionary that persists data between reruns
- **Widgets**: UI elements that trigger reruns when interacted with

```python
# This entire script runs every time user clicks a button or types something
import streamlit as st

# This runs on every rerun
st.title("My App")  

# Session state persists between reruns
if "counter" not in st.session_state:
    st.session_state.counter = 0
```

### 2. Session State Management

Session state is crucial for maintaining chat history:

```python
# Initialize on first run only
if "messages" not in st.session_state:
    st.session_state.messages = []

# This list persists across reruns
st.session_state.messages.append({"role": "user", "content": "Hello"})
```

## Implementation Details

### File Structure
```
streamlit_chat.py      # Main chat UI application
requirements.txt       # Includes streamlit dependency
```

### Core Components

#### 1. Page Configuration
```python
st.set_page_config(
    page_title="Sales Ops Assistant",
    page_icon="🤖",
    layout="centered"
)
```
- Sets browser tab title and icon
- Configures page layout (centered vs wide)

#### 2. State Initialization
```python
if "messages" not in st.session_state:
    st.session_state.messages = []
```
- Creates persistent message storage
- Only runs on first load, not on reruns

#### 3. Sidebar Implementation
```python
with st.sidebar:
    st.header("💬 Chat Controls")
    
    # Clear button triggers rerun when clicked
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()  # Force immediate rerun
```

The sidebar contains:
- Clear chat functionality
- Message counter
- Example questions

#### 4. Example Questions Handler

This was tricky to implement due to Streamlit's execution model:

```python
# In sidebar
for i, example in enumerate(examples):
    if st.button(f"→ {example}", key=f"example_{i}"):
        st.session_state.pending_message = example

# In main area
user_input = st.chat_input("What would you like to know?")

if "pending_message" in st.session_state:
    prompt = st.session_state.pending_message
    del st.session_state.pending_message
else:
    prompt = user_input
```

Why this approach?
- Button clicks trigger reruns
- We can't directly insert text into chat_input
- Solution: Use session state as a message queue

#### 5. Chat Display Logic

```python
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown("**🤖 Sales Operations Assistant**")
            st.markdown(message["content"])
```

- `st.chat_message()` creates chat bubble UI
- Different styling for user vs assistant
- Assistant always shows with consistent branding

#### 6. API Integration

```python
if prompt:
    # Add to history immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show assistant response area
    with st.chat_message("assistant"):
        st.markdown("**🤖 Sales Operations Assistant**")
        
        # Spinner shows during API call
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{API_BASE_URL}/agent/chat",
                json={"message": prompt},
                timeout=30
            )
```

Key points:
- Messages added to history before API call
- Spinner provides visual feedback
- 30-second timeout for long queries

#### 7. Error Handling

```python
try:
    response = requests.post(...)
    if response.status_code == 200:
        # Handle success
    else:
        st.error(f"Error: API returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    st.error("❌ Cannot connect to API. Make sure the Flask app is running on port 8000")
except requests.exceptions.Timeout:
    st.error("⏱️ Request timed out. The agent might be processing a complex query.")
```

Three types of errors handled:
1. HTTP errors (non-200 status)
2. Connection errors (API not running)
3. Timeout errors (long processing)

## Streamlit Widget Reference

### Widgets Used

1. **st.chat_input()**
   - Creates the message input box
   - Returns text when Enter is pressed
   - Always appears at bottom of page

2. **st.chat_message()**
   - Creates chat bubble container
   - Accepts "user" or "assistant" role
   - Provides avatar and styling

3. **st.button()**
   - Creates clickable button
   - Returns True when clicked (for that run only)
   - Requires unique key for multiple buttons

4. **st.sidebar**
   - Context manager for sidebar content
   - Everything inside appears in left panel

5. **st.spinner()**
   - Shows loading animation
   - Used as context manager

6. **st.error()/st.success()**
   - Colored alert boxes
   - Used for status messages

7. **st.metric()**
   - Shows a metric with label and value
   - Used for message count

8. **st.divider()**
   - Horizontal line separator

## Data Flow

### 1. User Types Message
```
User types in chat_input → Press Enter → Returns text → Triggers rerun
```

### 2. Example Question Click
```
User clicks example button → Sets pending_message → Triggers rerun → 
→ Pending message detected → Processed as prompt
```

### 3. Message Processing
```
1. Add to session state messages
2. Display user message
3. Call API with message
4. Receive response
5. Display response
6. Add response to messages
```

## State Management Patterns

### Pattern 1: Conditional Initialization
```python
if "key" not in st.session_state:
    st.session_state.key = initial_value
```

### Pattern 2: Message Queue
```python
# Set message in one place
st.session_state.pending_message = "Hello"

# Process in another place
if "pending_message" in st.session_state:
    process(st.session_state.pending_message)
    del st.session_state.pending_message
```

### Pattern 3: Force Rerun
```python
if st.button("Clear"):
    st.session_state.messages = []
    st.rerun()  # Immediate rerun to show changes
```

## Common Pitfalls and Solutions

### 1. Widget Keys
**Problem**: "DuplicateWidgetID" error
```python
# Wrong - buttons have same key
for item in items:
    if st.button("Click"):  # Error!
```

**Solution**: Use unique keys
```python
for i, item in enumerate(items):
    if st.button("Click", key=f"btn_{i}"):
```

### 2. State Persistence
**Problem**: Variables reset on rerun
```python
# Wrong - resets on every rerun
counter = 0
if st.button("Increment"):
    counter += 1  # Always shows 1
```

**Solution**: Use session state
```python
if "counter" not in st.session_state:
    st.session_state.counter = 0
if st.button("Increment"):
    st.session_state.counter += 1
```

### 3. Input Widget Behavior
**Problem**: Can't programmatically set input value
```python
# This doesn't work
user_input = st.text_input("Enter text", value=dynamic_value)
```

**Solution**: Use our pending message pattern

## Performance Considerations

1. **Minimize API Calls**: Cache responses when possible
2. **Efficient Reruns**: Only modify state when necessary
3. **Timeout Handling**: Set reasonable timeouts for API calls
4. **Error Recovery**: Graceful handling prevents UI freezing

## Security Considerations

1. **API Endpoint**: Never expose API keys in frontend
2. **Input Validation**: The API should validate all inputs
3. **Error Messages**: Don't expose sensitive system details
4. **CORS**: Handled by Flask backend

## Deployment Notes

### Development
```bash
streamlit run streamlit_chat.py
```

### Production
```bash
streamlit run streamlit_chat.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true
```

### Environment Variables
```bash
# Can configure API URL
export API_BASE_URL="https://api.production.com"
```

## Testing the UI

### Manual Testing Checklist
- [ ] Chat input accepts text
- [ ] Messages display correctly
- [ ] Example questions work
- [ ] Clear chat functions
- [ ] Error messages appear appropriately
- [ ] API timeout handling works
- [ ] Message count updates

### Common Test Scenarios
1. Send a normal message
2. Click an example question
3. Send message when API is down
4. Send multiple messages quickly
5. Clear chat and start over

## Future Enhancements

1. **Message Actions**: Edit, copy, delete individual messages
2. **Export Chat**: Download conversation history
3. **Voice Input**: Speech-to-text integration
4. **Rich Responses**: Tables, charts, formatted data
5. **User Settings**: Theme, text size, preferences
6. **Multi-Agent**: Switch between different agents
7. **File Upload**: Attach documents to messages

## Troubleshooting

### "Cannot connect to API"
- Ensure Flask app is running on port 8000
- Check firewall settings
- Verify API_BASE_URL is correct

### "Request timed out"
- Agent may be processing complex query
- Check Flask logs for errors
- Consider increasing timeout

### UI Not Updating
- Check browser console for errors
- Ensure session state is properly managed
- Try force refresh (Ctrl+R)

## Code Organization Best Practices

1. **Constants at Top**: API URLs, configuration
2. **State Init Early**: Before any UI elements
3. **Logical Sections**: Sidebar, main area, footer
4. **Error Handling**: Wrap API calls in try-except
5. **Clear Comments**: Explain non-obvious patterns

This implementation provides a production-ready chat interface that seamlessly integrates with the LangChain agent backend while maintaining a clean, intuitive user experience.