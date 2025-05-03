import streamlit as st

import streamlit as st
import requests
import json
from openai import OpenAI
import time
import os

# Page configuration with custom theme colors
st.set_page_config(
    page_title="XIA - AI Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL configuration - can be set as environment variable for flexibility
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {color: #2C3E50; font-size: 28px; font-weight: 700;}
    .sub-header {color: #34495E; font-size: 20px; font-weight: 600; margin-top: 1rem;}
    .sidebar-header {font-size: 24px; font-weight: 700; margin-bottom: 1.5rem;}
    
    .chat-message-user {
        background-color: #000066; 
        padding: 10px 15px; 
        border-radius: 15px; 
        margin-bottom: 10px;
        max-width: 80%;
        align-self: flex-end;
    }
    
    .chat-message-assistant {
        background-color: #ff9966; 
        padding: 10px 15px; 
        border-radius: 15px; 
        margin-bottom: 10px;
        max-width: 80%;
    }
    
    .stButton button {
        background-color: #3498DB;
        color: white;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    
    .stButton button:hover {
        background-color: #2980B9;
    }
    
    .task-card {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 4px solid #3498DB;
    }
    
    .document-card {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 4px solid #27AE60;
    }
    
    .summary-card {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 4px solid #F1C40F;
    }
    
    /* Custom styling for the sidebar */
    .css-1d391kg {
        background-color: #2C3E50;
    }
    
    /* Adjust text input fields */
    .stTextInput input {
        border-radius: 5px;
        border: 1px solid #D5DBDB;
        padding: 10px;
    }
    
    /* Custom chat container */
    .chat-container {
        height: 60vh;
        overflow-y: auto;
        padding: 20px;
        border-radius: 10px;
        background-color: #000066;
        border: 1px solid #E5E8E8;
        margin-bottom: 20px;
    }
    
    /* Grid cards at bottom */
    .grid-card {
        height: 100%;
        padding: 15px;
        border-radius: 10px;
        background-color: #FFFFFF;
        border: 1px solid #E5E8E8;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def call_api(endpoint, method="get", data=None, retry=2):
    """Enhanced function to call backend API with retry logic."""
    url = f"{BACKEND_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    for attempt in range(retry + 1):
        try:
            if method.lower() == "get":
                response = requests.get(url, timeout=10)
            elif method.lower() == "post":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method.lower() == "put":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method.lower() == "delete":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                st.error(f"Unsupported method: {method}")
                return None

            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            if attempt < retry:
                time.sleep(1)  # Wait before retrying
                continue
            st.error("Request timed out. Please try again later.")
            return None
            
        except requests.exceptions.ConnectionError:
            st.error(f"Connection error. Please check if the backend server is running at {BACKEND_URL}")
            return None
            
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e}")
            return None
            
        except json.JSONDecodeError:
            st.error("Could not parse the API response.")
            return None
            
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return None

def display_chat_message(sender, message, is_user=False):
    """Display a stylized chat message with improved formatting."""
    # Process message to handle line breaks and formatting properly
    formatted_message = message.replace("\n", "<br>")
    
    if is_user:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end;">
            <div class="chat-message-user">
                <b>{sender}:</b> {formatted_message}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Format XIA's message to nicely display lists and structured content
        if sender == "XIA" and ("1." in message or "•" in message or "-" in message):
            # For messages that appear to have lists or structured content
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start;">
                <div class="chat-message-assistant" style="width: 85%;">
                    <b>{sender}:</b> {formatted_message}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start;">
                <div class="chat-message-assistant">
                    <b>{sender}:</b> {formatted_message}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Initialize session state variables
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"sender": "Sara", "message": "I want to launch an app that promotes sustainable shopping. Can you help me organize what I need to do?", "is_user": True}
    ]
    
    # Add an initial XIA response to match the wireframe
    detailed_plan = """I'd be happy to help you create a comprehensive startup launch plan for your sustainable shopping app. Here's a step-by-step plan to help you get started:

Pre-Launch (Weeks 1-4)

1. Define your mission and value proposition:
   • Identify your target audience (e.g., environmentally conscious consumers, small business owners)
   • Determine the key features and benefits of your app (e.g., product recommendations, carbon footprint tracking, rewards program)
   • Develop a unique value proposition statement (e.g., "Our app helps you make sustainable shopping choices and reduce your environmental impact")

2. Conduct market research:
   • Analyze the competitive landscape (e.g., existing apps, websites, and platforms promoting sustainable shopping)
   • Identify market trends, consumer behavior, and pain points related to sustainable shopping"""
   
    st.session_state.chat_history.append({"sender": "XIA", "message": detailed_plan, "is_user": False})
    st.session_state.plan = detailed_plan

if "email_draft" not in st.session_state:
    st.session_state.email_draft = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Chat"

# --- Sidebar ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg", width=40)
    st.markdown('<p class="sidebar-header">XIA</p>', unsafe_allow_html=True)
    
    # Navigation menu with highlighting for current page
    for page_name in ["Chat", "Tasks", "Documents", "Daily Summary"]:
        if st.button(
            page_name, 
            key=f"nav_{page_name}",
            on_click=lambda page=page_name: setattr(st.session_state, "current_page", page),
            use_container_width=True,
            type="primary" if st.session_state.current_page == page_name else "secondary"
        ):
            pass
    
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        # In a real application, this would handle the logout logic
        st.info("Logout functionality would be implemented in a production environment.")

    # --- Main Content Area ---
st.markdown(f'<h1 class="main-header">{st.session_state.current_page}</h1>', unsafe_allow_html=True)

# Apply dark background to the entire app
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Page Content Based on Navigation ---
if st.session_state.current_page == "Chat":
    # Display chat container with message history
    with st.container():
        for message in st.session_state.chat_history:
            display_chat_message(message["sender"], message["message"], message["is_user"])
        
        # If we have a response from XIA, show it
        if st.session_state.plan and not any(msg["message"] == st.session_state.plan for msg in st.session_state.chat_history):
            display_chat_message("XIA", st.session_state.plan)
            st.session_state.chat_history.append({"sender": "XIA", "message": st.session_state.plan, "is_user": False})
    
    # User input area
    user_message = st.text_input("Type your message...", key="user_message")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Generate Plan", use_container_width=True):
            if user_message:
                with st.spinner("Generating plan..."):
                    # Add user message to chat history
                    st.session_state.chat_history.append({"sender": "You", "message": user_message, "is_user": True})
                    
                    # Call API to generate plan
                    response = call_api("/generate-plan", method="post", data={"idea": user_message})
                    if response:
                        st.session_state.plan = response["plan"]
                        # Add assistant response to chat history
                        st.session_state.chat_history.append({"sender": "XIA", "message": st.session_state.plan, "is_user": False})
                        st.rerun()
            else:
                st.warning("Please enter your message.")
    
    with col2:
        if st.button("Create Email", use_container_width=True):
            if user_message:
                with st.spinner("Creating email..."):
                    # Add user message to chat history
                    st.session_state.chat_history.append({"sender": "You", "message": f"Create an email about: {user_message}", "is_user": True})
                    
                    # Call API to generate email
                    response = call_api("/generate-email", method="post", data={"context": "Sustainable Shopping App", "details": user_message})
                    if response:
                        st.session_state.email_draft = response["email"]
                        # Add assistant response to chat history with improved formatting
                        email_message = f"Here's an email draft for your sustainable shopping app:\n\n{st.session_state.email_draft}"
                        st.session_state.chat_history.append({"sender": "XIA", "message": email_message, "is_user": False})
                        st.rerun()
            else:
                st.warning("Please enter your message.")
    
    with col3:
        if st.button("Summarize Competition", use_container_width=True):
            if user_message:
                with st.spinner("Summarizing..."):
                    # Add user message to chat history
                    st.session_state.chat_history.append({"sender": "You", "message": f"Summarize competition for: {user_message}", "is_user": True})
                    
                    # Call API to generate summary
                    response = call_api("/generate-summary", method="post", data={"tasks": [user_message]})
                    if response:
                        st.session_state.summary = response["summary"]
                        # Add assistant response to chat history
                        summary_message = f"Competition Summary:\n\n{st.session_state.summary}"
                        st.session_state.chat_history.append({"sender": "XIA", "message": summary_message, "is_user": False})
                        st.rerun()
            else:
                st.warning("Please enter your message.")

elif st.session_state.current_page == "Tasks":
    st.markdown('<h2 class="sub-header">Task Board</h2>', unsafe_allow_html=True)
    
    # Fetch tasks from backend
    response = call_api("/task-history")
    if response:
        st.session_state.tasks = response.get("tasks", [])
    
    # Display existing tasks with stylized cards
    for i, task in enumerate(st.session_state.tasks):
        with st.container():
            st.markdown(f"""
            <div class="task-card">
                <div style="display: flex; align-items: center;">
                    <div style="flex-grow: 1;">
                        {task["title"]}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Checkbox implementation
            completed = st.checkbox("", value=(task["status"] == "completed"), key=f"task_{task['id']}")
            
            if completed != (task["status"] == "completed"):
                new_status = "completed" if completed else "pending"
                with st.spinner("Updating task..."):
                    call_api(f"/update-task-status/{task['id']}", method="put", data={"status": new_status})
                    # Update local state immediately
                    st.session_state.tasks[i]["status"] = new_status
    
    # Add new task section
    st.markdown('<h2 class="sub-header">Add New Task</h2>', unsafe_allow_html=True)
    
    with st.form(key="add_task_form", clear_on_submit=True):
        new_task_title = st.text_input("Task title:", key="new_task_title")
        submit_button = st.form_submit_button(label="Add Task")
        
        if submit_button and new_task_title:
            with st.spinner("Adding task..."):
                response = call_api("/add-task", method="post", data={"title": new_task_title, "status": "pending"})
                if response:
                    st.success(f"Task '{new_task_title}' added successfully!")
                    # Refresh the task list
                    task_response = call_api("/task-history")
                    if task_response:
                        st.session_state.tasks = task_response.get("tasks", [])
                    st.rerun()

elif st.session_state.current_page == "Documents":
    st.markdown('<h2 class="sub-header">Generated Documents</h2>', unsafe_allow_html=True)
    
    # Display documents with stylized cards
    if st.session_state.plan:
        with st.expander("Product Plan Draft", expanded=True):
            st.markdown(f"""
            <div class="document-card">
                <h4 style="margin-top: 0;">Product Plan Draft</h4>
                {st.session_state.plan}
            </div>
            """, unsafe_allow_html=True)
    
    if st.session_state.email_draft:
        with st.expander("Email to Investors", expanded=True):
            st.markdown(f"""
            <div class="document-card">
                <h4 style="margin-top: 0;">Email to Investors</h4>
                {st.session_state.email_draft}
            </div>
            """, unsafe_allow_html=True)
    
    if st.session_state.summary:
        with st.expander("Competitor Summary", expanded=True):
            st.markdown(f"""
            <div class="document-card">
                <h4 style="margin-top: 0;">Competitor Summary</h4>
                {st.session_state.summary}
            </div>
            """, unsafe_allow_html=True)
    
    # If no documents are available
    if not (st.session_state.plan or st.session_state.email_draft or st.session_state.summary):
        st.info("No documents have been generated yet. Use the Chat page to create documents.")
        
    # Document actions
    st.markdown('<h2 class="sub-header">Document Actions</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export All Documents", use_container_width=True):
            st.info("Document export functionality would be implemented in a production environment.")
    
    with col2:
        if st.button("Clear Documents", use_container_width=True):
            if st.session_state.plan or st.session_state.email_draft or st.session_state.summary:
                st.session_state.plan = None
                st.session_state.email_draft = None
                st.session_state.summary = None
                st.success("All documents cleared!")
                st.rerun()
            else:
                st.info("No documents to clear.")

elif st.session_state.current_page == "Daily Summary":
    st.markdown('<h2 class="sub-header">Daily Summary</h2>', unsafe_allow_html=True)
    
    # Fetch tasks and generate summary
    response = call_api("/task-history")
    if response:
        tasks = response.get("tasks", [])
        pending_tasks = [task for task in tasks if task["status"] == "pending"]
        completed_tasks = [task for task in tasks if task["status"] == "completed"]
        
        # Display summary stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pending Tasks", len(pending_tasks))
        with col2:
            st.metric("Completed Tasks", len(completed_tasks))
        
        # Display pending tasks
        st.markdown('<h3 style="margin-top: 20px;">Tasks Requiring Attention</h3>', unsafe_allow_html=True)
        if pending_tasks:
            for task in pending_tasks:
                st.markdown(f"""
                <div class="summary-card">
                    <div style="display: flex; align-items: center;">
                        <div style="flex-grow: 1;">
                            {task["title"]}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Get focus recommendation
            task_titles = [task["title"] for task in pending_tasks]
            if task_titles:
                # Only make API call if we don't already have a summary
                if not st.session_state.summary:
                    with st.spinner("Generating focus recommendation..."):
                        summary_response = call_api("/generate-summary", method="post", data={"tasks": task_titles})
                        if summary_response:
                            st.session_state.summary = summary_response["summary"]
                
                if st.session_state.summary:
                    st.markdown(f"""
                    <div class="summary-card" style="margin-top: 20px;">
                        <h4 style="margin-top: 0;">Recommended Focus</h4>
                        {st.session_state.summary}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("No pending tasks. You're all caught up!")

# --- Bottom Grid Section (shown on all pages) ---
st.markdown("---")
st.markdown('<h2 class="sub-header">Dashboard Overview</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="grid-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; color: #E0E0E0;">Task Board</h3>', unsafe_allow_html=True)
    
    # Add sample tasks if tasks list is empty (for demonstration purposes)
    if not st.session_state.tasks:
        st.session_state.tasks = [
            {"id": "1", "title": "Finalize Product Idea", "status": "pending"},
            {"id": "2", "title": "Research Competitors", "status": "pending"},
            {"id": "3", "title": "Design Landing Page", "status": "pending"}
        ]
    
    # Display a subset of tasks for the dashboard view
    if "tasks" in st.session_state and st.session_state.tasks:
        for i, task in enumerate(st.session_state.tasks[:3]):  # Show up to 3 tasks
            st.markdown(f'<p style="color: #E0E0E0;">- {"✅" if task["status"] == "completed" else "⬜"} {task["title"]}</p>', unsafe_allow_html=True)
        
        if len(st.session_state.tasks) > 3:
            st.markdown(f'<p style="color: #E0E0E0; font-style: italic;">...and {len(st.session_state.tasks) - 3} more tasks</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #E0E0E0;">No tasks available.</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="grid-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; color: #E0E0E0;">Generated Documents</h3>', unsafe_allow_html=True)
    
    # List document status
    doc_count = 0
    if st.session_state.plan:
        st.markdown('<p style="color: #E0E0E0;">- Product Plan Draft</p>', unsafe_allow_html=True)
        doc_count += 1
    
    # Initialize email_draft if not already set (for display purposes in the wireframe)
    if st.session_state.email_draft is None:
        st.session_state.email_draft = "Sample email content for investors"
    
    st.markdown('<p style="color: #E0E0E0;">- Email to Investors</p>', unsafe_allow_html=True)
    doc_count += 1
    
    # Initialize summary if not already set
    if st.session_state.summary is None:
        st.session_state.summary = "Competitor analysis focusing on sustainable shopping apps"
    
    st.markdown('<p style="color: #E0E0E0;">- Competitor Summary</p>', unsafe_allow_html=True)
    doc_count += 1
    
    if doc_count == 0:
        st.markdown('<p style="color: #E0E0E0;">No documents generated yet.</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="grid-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-size: 18px; color: #E0E0E0;">Daily Summary</h3>', unsafe_allow_html=True)
    
    # Display a summary for the dashboard view
    pending_count = len([task for task in st.session_state.tasks if task["status"] == "pending"])
    
    st.markdown(f'<p style="color: #E0E0E0;">You have {pending_count} pending tasks.</p>', unsafe_allow_html=True)
    
    # Make sure we have a focus item for the wireframe display
    if st.session_state.summary:
        st.markdown(f'<p style="color: #E0E0E0;"><strong>Focus:</strong> Finalize Product Description</p>', unsafe_allow_html=True)
    elif pending_count == 0:
        st.markdown('<p style="color: #E0E0E0;">No pending tasks. You\'re all caught up!</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: #E0E0E0;"><strong>Focus:</strong> Finalize Product Description</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)