st.set_page_config(page_title="XIA - Your AI Cofounder", layout="wide")

with st.sidebar:
    st.title("XIA")
    st.page_link("#chat", label="Chat")
    st.page_link("#tasks", label="Tasks")
    st.page_link("#documents", label="Documents")
    st.page_link("#summary", label="Daily Summary")

st.markdown(
    """
    <style>
    body {
        background-color: #F5F0E1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.header("Chat with XIA")

with st.container():
    st.markdown("**Sara:** I want to launch an app that promotes sustainable shopping. Can you help me organize what I need to do?")

    st.chat_message("assistant").markdown(
        """
        **XIA:** That’s a great idea, Sara! Here's a high-level to-do list:
        - Define your core features
        - Research competitors
        - Design landing page content
        - Create outreach emails
        - Set a launch goal and timeline
        """
    )
st.write("")
col1, col2, col3 = st.columns(3)
with col1:
    st.button("Generate Plan")
with col2:
    st.button("Create Email")
with col3:
    st.button("Summarize Competition")

st.write("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Task Board")
    st.success(" Finalize Product Idea")
    st.warning(" Research Competitors")
    st.warning(" Design Landing Page")

with col2:
    st.subheader("Generated Documents")
    st.info(" Product Plan Draft")
    st.info("✉ Email to Investors")
    st.info(" Competitor Summary")

with col3:
    st.subheader("Daily Summary")
    st.write(" 5 pending tasks")
    st.write(" Focus: Finalize Product Description")
