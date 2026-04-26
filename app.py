import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(page_title="RecruitAI", page_icon="🏈", layout="wide")

with st.sidebar:
    st.title("🏈 RecruitAI")
    st.markdown("**Full 5-Agent Crew**")
    st.caption("Robust Version")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing.")
    st.stop()

llm = LLM(model="groq/llama-3.1-8b-instant", temperature=0.4, max_tokens=1000)

current_date = datetime.date.today().strftime("%Y-%m-%d")
backstory = f"NCAA recruiting expert. Public data only. Current date: {current_date}."

# === 5-AGENT CREW ===
researcher = Agent(
    role="Senior Trend & Fit Researcher",
    goal="Find realistic school fits with strong rationale",
    backstory=backstory + " Focus on division level, location, academics, roster needs, and recent recruiting activity.",
    llm=llm,
    verbose=False
)

contact_finder = Agent(
    role="Coach Contact Finder",
    goal="Find public coach contacts and staff information",
    backstory=backstory,
    llm=llm,
    verbose=False
)

enricher = Agent(
    role="Athlete Profile Enricher",
    goal="Build a strong, polished athlete profile and fit scores",
    backstory="Compile stats, academics, and strengths into a compelling profile.",
    llm=llm,
    verbose=False
)

personalizer = Agent(
    role="Elite Recruiting Writer",
    goal="Create high-quality, distinct outreach messages",
    backstory="""Expert recruiting communications specialist. Write warm, respectful, and compelling emails/DMs that stand out.
    Make three versions clearly different:
    1. Character & leadership focused
    2. Athletic stats & skills focused
    3. Short, natural DM/Text version""",
    llm=llm,
    verbose=False
)

compliance_guard = Agent(
    role="NCAA Compliance Guardian",
    goal="Ensure full compliance and smart timing advice",
    backstory=backstory + " Be accurate about current recruiting periods by sport.",
    llm=llm,
    verbose=False
)

st.title("🏈 RecruitAI - Full 5-Agent Crew")
st.markdown("**Robust multi-agent system**")

# Input Form
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

    if st.button("🚀 Run Full 5-Agent Crew", type="primary", use_container_width=True):
        with st.spinner("Running full 5-agent crew... (this may take 60-120 seconds)"):
            try:
                task1 = Task(
                    description=f"Research and list 6-8 realistic school fits for: {athlete_input}",
                    expected_output="Numbered list of schools with fit rationale.",
                    agent=researcher
                )

                task2 = Task(
                    description="From the schools above, find public coach contacts.",
                    expected_output="Bullet list of coach contacts with sources.",
                    agent=contact_finder
                )

                task3 = Task(
                    description=f"Build a polished athlete profile and fit scores for: {athlete_input}",
                    expected_output="Polished bio + per-school fit scores.",
                    agent=enricher
                )

                task4 = Task(
                    description=f"Write 3 distinct, high-quality outreach messages for: {athlete_input}",
                    expected_output="1. Full Professional Email (character focused)\n2. Alternative Email (stats focused)\n3. Short DM/Text version\nInclude strong subject lines and NCAA disclaimer.",
                    agent=personalizer
                )

                task5 = Task(
                    description="Provide compliance summary and recommended timing.",
                    expected_output="Compliance verdict + suggested follow-up schedule.",
                    agent=compliance_guard
                )

                crew = Crew(
                    agents=[researcher, contact_finder, enricher, personalizer, compliance_guard],
                    tasks=[task1, task2, task3, task4, task5],
                    process=Process.sequential,
                    verbose=False,
                    max_rpm=6,
                    memory=False
                )

                result = crew.kickoff(inputs={"athlete_input": athlete_input})

                st.success("✅ Full 5-Agent Campaign Generated")

                st.subheader("📍 Recommended Schools")
                with st.expander("View schools", expanded=True):
                    st.markdown(result)

                st.subheader("📧 Outreach Templates")
                st.text_area("Templates will appear here...", height=300, label_visibility="collapsed")

                with st.expander("✅ Compliance"):
                    st.write("Review the full output above for compliance details.")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("If rate limited, wait 30+ seconds and try again.")

st.caption("Full 5-agent crew restored")
