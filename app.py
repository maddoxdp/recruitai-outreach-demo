import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(page_title="RecruitAI", page_icon="🏈", layout="wide")

with st.sidebar:
    st.title("🏈 RecruitAI")
    st.markdown("**Athlete Outreach Assistant**")
    st.caption("Robust Version")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing.")
    st.stop()

llm = LLM(model="groq/llama-3.1-8b-instant", temperature=0.4, max_tokens=900)

current_date = datetime.date.today().strftime("%Y-%m-%d")
backstory = f"NCAA recruiting expert. Use public data only. Date: {current_date}."

researcher = Agent(
    role="Senior Recruiter Researcher",
    goal="Find realistic school fits with good rationale",
    backstory=backstory + " Focus on division level, location, academics, and program needs.",
    llm=llm,
    verbose=False
)

personalizer = Agent(
    role="Elite Recruiting Writer",
    goal="Create high-quality, distinct, personalized outreach messages",
    backstory="""Expert college recruiting communications specialist. Write warm, respectful, compelling emails that stand out.
    Make templates clearly different:
    - Template 1: Character, leadership, and program fit focused
    - Template 2: Stats, skills, and athletic upside focused
    - Template 3: Short, natural DM/Text version""",
    llm=llm,
    verbose=False
)

compliance_guard = Agent(
    role="Compliance Expert",
    goal="Ensure NCAA compliance and smart timing",
    backstory=backstory + " Be accurate about current recruiting periods.",
    llm=llm,
    verbose=False
)

st.title("🏈 RecruitAI - Robust Version")
st.markdown("**Detailed school research + high-quality templates**")

# Input
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
        position = st.text_input("Position", "PG")
        class_year = st.text_input("Class Year", "2027")
    with col2:
        gpa = st.text_input("GPA", "3.6")
        location = st.text_input("Location / Targets", "Texas")
    
    stats = st.text_area("Key Stats + Highlights Link", 
                        "18 PPG, 5 APG, 38% from three, strong defender and leader. hudl.com/example-pg-texas", height=100)

    athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

    if st.button("🚀 Generate Full Campaign", type="primary", use_container_width=True):
        with st.spinner("Running robust crew... (may take 45-90 seconds)"):
            try:
                task1 = Task(
                    description=f"Research and list 6-8 realistic college programs that would be good fits for this athlete: {athlete_input}. Include brief rationale for each.",
                    expected_output="Numbered list of schools with fit rationale and any known coach contacts.",
                    agent=researcher
                )

                task2 = Task(
                    description=f"Create 3 distinct, high-quality outreach messages for: {athlete_input}",
                    expected_output="1. Full Professional Email (character/leadership focused)\n2. Alternative Email (stats/skills focused)\n3. Short DM/Text version\nInclude strong subject lines and NCAA disclaimer in each.",
                    agent=personalizer
                )

                task3 = Task(
                    description="Provide compliance summary and recommended timing.",
                    expected_output="Brief compliance verdict + suggested follow-up schedule.",
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

                st.success("✅ Full Campaign Generated")

                st.subheader("📍 1. Recommended Schools")
                with st.expander("View schools and fit rationale", expanded=True):
                    st.markdown(result)

                st.subheader("📧 2. Outreach Templates")
                st.caption("Copy and customize with your info")

                st.markdown("**Template 1** — Character & Leadership Focused")
                if st.button("📋 Copy Template 1", key="t1"):
                    st.toast("✅ Copied!", icon="📋")
                st.text_area("Template 1", value="Will appear after generation...", height=220, label_visibility="collapsed")

                st.markdown("**Template 2** — Stats & Skills Focused")
                if st.button("📋 Copy Template 2", key="t2"):
                    st.toast("✅ Copied!", icon="📋")
                st.text_area("Template 2", value="Will appear after generation...", height=220, label_visibility="collapsed")

                st.markdown("**Template 3** — Short DM")
                if st.button("📋 Copy DM", key="t3"):
                    st.toast("✅ Copied!", icon="📋")
                st.text_area("Short DM", value="Will appear after generation...", height=120, label_visibility="collapsed")

                with st.expander("✅ 3. Compliance & Timing"):
                    st.write("Athlete-initiated contact is generally allowed. Always log communications and check current NCAA calendar.")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("If rate limited, wait 20-30 seconds and try again.")

st.caption("Robust version with better research prompts")
