import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(page_title="RecruitAI", page_icon="🏈", layout="wide")

with st.sidebar:
    st.title("🏈 RecruitAI")
    st.markdown("**Athlete Outreach Assistant**")
    st.caption("Fast • Simple • Compliant")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing.")
    st.stop()

llm = LLM(model="groq/llama-3.1-8b-instant", temperature=0.3, max_tokens=700)

current_date = datetime.date.today().strftime("%Y-%m-%d")
backstory = f"NCAA expert. Public data only. Date: {current_date}. Add disclaimer."

researcher = Agent(role="Researcher", goal="List school fits & contacts", backstory=backstory, llm=llm, verbose=False)
personalizer = Agent(
    role="Recruiting Writer",
    goal="Write 2 different short email templates + 1 DM",
    backstory="Write natural recruiting messages. Make the two emails clearly different (one character-focused, one stats-focused).",
    llm=llm,
    verbose=False
)
compliance_guard = Agent(role="Compliance", goal="Check rules & timing", backstory=backstory, llm=llm, verbose=False)

st.title("🏈 RecruitAI")
st.markdown("Generate clean, compliant coach outreach")

# Compact Input Form
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
        position = st.text_input("Position", "PG")
        class_year = st.text_input("Class Year", "2027")
    with col2:
        gpa = st.text_input("GPA", "3.6")
        location = st.text_input("Location / Targets", "Texas")
    
    stats = st.text_area("Key Stats + Highlights Link (keep short)", 
                        "18 PPG, 5 APG, 38% from three. hudl.com/example", height=80)

    athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

    generate_btn = st.button("🚀 Generate Outreach Campaign", type="primary", use_container_width=True)

# Clean Output Section
if generate_btn:
    with st.spinner("Generating clean campaign..."):
        try:
            task1 = Task(
                description=f"List 6 school fits and suggest public coach contacts for: {athlete_input}",
                expected_output="Short list: School - Fit reason - Coach contact if known.",
                agent=researcher
            )

            task2 = Task(
                description=f"Write 2 different short email templates + 1 DM for: {athlete_input}",
                expected_output="Template 1 (character focused), Template 2 (stats focused), Short DM. Include disclaimer.",
                agent=personalizer
            )

            task3 = Task(
                description="Give brief compliance and timing advice.",
                expected_output="Short compliance note + suggested follow-up.",
                agent=compliance_guard
            )

            crew = Crew(
                agents=[researcher, personalizer, compliance_guard],
                tasks=[task1, task2, task3],
                process=Process.sequential,
                verbose=False,
                max_rpm=6,
                memory=False
            )

            result = crew.kickoff(inputs={"athlete_input": athlete_input})

            st.success("✅ Campaign Generated")

            # === CLEAN OUTPUT LAYOUT ===
            st.subheader("📍 Recommended Schools & Contacts")
            with st.expander("View schools and contacts", expanded=True):
                st.markdown(result)

            st.subheader("📧 Outreach Templates")
            st.caption("Click the buttons to copy • Customize with your name and details")

            # Template 1
            st.markdown("**1. Character & Leadership Focused Email**")
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.text_area("Template 1", value="Template 1 will appear here...", height=180, label_visibility="collapsed")
            with col_b:
                if st.button("📋 Copy", key="copy1"):
                    st.toast("✅ Template 1 copied!", icon="📋")

            # Template 2
            st.markdown("**2. Stats & Skills Focused Email**")
            col_c, col_d = st.columns([4, 1])
            with col_c:
                st.text_area("Template 2", value="Template 2 will appear here...", height=180, label_visibility="collapsed")
            with col_d:
                if st.button("📋 Copy", key="copy2"):
                    st.toast("✅ Template 2 copied!", icon="📋")

            # Short DM
            st.markdown("**3. Short DM / Text Message**")
            col_e, col_f = st.columns([4, 1])
            with col_e:
                st.text_area("Short DM", value="Short DM will appear here...", height=110, label_visibility="collapsed")
            with col_f:
                if st.button("📋 Copy", key="copy3"):
                    st.toast("✅ Short DM copied!", icon="📋")

            with st.expander("✅ Compliance & Timing"):
                st.write("Athlete-initiated electronic contact is generally allowed. Log all messages. Follow up in 10–14 days if no reply.")

        except Exception as e:
            if "rate limit" in str(e).lower():
                st.error("⏳ Rate limit reached. Please wait 15–30 seconds and try again.")
            else:
                st.error(f"Error: {str(e)}")

st.caption("Clean UI version • Ultra-light backend")
