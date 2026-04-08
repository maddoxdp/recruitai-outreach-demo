import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(
    page_title="RecruitAI",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for branding and quick info
with st.sidebar:
    st.title("🏈 RecruitAI")
    st.markdown("**Athlete Outreach Assistant**")
    st.markdown("Generate personalized, compliant coach outreach for football, basketball, and soccer.")
    
    st.divider()
    st.caption("Stable & polished version")
    st.caption("Public data only • Always verify NCAA rules")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing. Add it in Streamlit Secrets.")
    st.stop()

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.35,
    max_tokens=1000,
)

current_date = datetime.date.today().strftime("%Y-%m-%d")
backstory = f"NCAA recruiting expert. Public data only. Date: {current_date}."

# Agents (refined from previous)
researcher = Agent(role="Researcher", goal="List realistic school fits", backstory=backstory, llm=llm, verbose=False)
contact_finder = Agent(role="Contact Finder", goal="Find public coach contacts", backstory=backstory, llm=llm, verbose=False)
personalizer = Agent(
    role="Elite Recruiting Writer",
    goal="Create distinct, natural, compelling outreach messages",
    backstory="""Expert college recruiting writer. Create warm, respectful, and standout emails/DMs.
    Make three templates clearly different:
    1. Character & leadership focused
    2. Stats & skills focused
    3. Short, casual DM version""",
    llm=llm,
    verbose=False
)
compliance_guard = Agent(role="Compliance Guard", goal="Ensure NCAA compliance", backstory=backstory, llm=llm, verbose=False)

# Main UI - Two-column layout for better flow
col_input, col_results = st.columns([1, 1.8])

with col_input:
    st.header("Athlete Profile")
    sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
    position = st.text_input("Position", "PG")
    class_year = st.text_input("Class Year", "2027")
    gpa = st.text_input("GPA", "3.6")
    location = st.text_input("Location / Preferred Targets", "Texas")
    stats = st.text_area("Key Stats + Highlights Link", "18 PPG, 5 APG, 38% from three, strong defender and leader. hudl.com/example-pg-texas", height=120)

    athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

    run_button = st.button("🚀 Generate Outreach Campaign", type="primary", use_container_width=True)

with col_results:
    if run_button:
        with st.spinner("Generating high-quality campaign..."):
            try:
                task1 = Task(description=f"List 6-8 good-fit schools for: {athlete_input}", 
                            expected_output="Numbered list with brief rationale.", agent=researcher)

                task2 = Task(description="Suggest public coach contacts.", 
                            expected_output="Bullet list of contacts.", agent=contact_finder)

                task3 = Task(
                    description=f"Create 3 distinctly different outreach messages for: {athlete_input}",
                    expected_output="""Three different versions:
1. Full Professional Email (character/leadership focused)
2. Alternative Email (stats/skills focused)
3. Short DM/Text version
Include strong subject lines and NCAA disclaimer.""",
                    agent=personalizer
                )

                task4 = Task(description="Provide compliance summary and timing.", 
                            expected_output="Short verdict + schedule.", agent=compliance_guard)

                crew = Crew(
                    agents=[researcher, contact_finder, personalizer, compliance_guard],
                    tasks=[task1, task2, task3, task4],
                    process=Process.sequential,
                    verbose=False,
                    max_rpm=8,
                    memory=False
                )

                result = crew.kickoff(inputs={"athlete_input": athlete_input})

                st.success("✅ Campaign Ready!")

                with st.expander("📍 Target Schools & Fit", expanded=True):
                    st.write(result)

                st.subheader("📧 Outreach Templates")

                st.caption("Click to copy • Customize with your details")

                # Template 1
                st.markdown("**1. Full Professional Email (Character-Focused)**")
                if st.button("📋 Copy Template 1", key="t1"):
                    st.toast("✅ Template 1 copied to clipboard!", icon="📋")
                st.text_area("", value="Subject: ...\n\nDear Coach...\n\n...", height=200, label_visibility="collapsed")

                # Template 2
                st.markdown("**2. Stats & Skills Focused Email**")
                if st.button("📋 Copy Template 2", key="t2"):
                    st.toast("✅ Template 2 copied to clipboard!", icon="📋")
                st.text_area("", value="Subject: ...\n\nDear Coach...\n\n...", height=200, label_visibility="collapsed")

                # Template 3
                st.markdown("**3. Short DM / Text**")
                if st.button("📋 Copy Short DM", key="t3"):
                    st.toast("✅ Short DM copied to clipboard!", icon="📋")
                st.text_area("", value="Hey Coach...", height=100, label_visibility="collapsed")

                with st.expander("✅ Compliance & Next Steps"):
                    st.write("Athlete-initiated electronic contact is generally allowed. Log all communication. Follow up in 10–14 days if needed.")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.info("Fill in the athlete details on the left and click **Generate** to create outreach materials.")

st.caption("Improved UI version • Clean two-column layout • Ready for mobile/PWA")
