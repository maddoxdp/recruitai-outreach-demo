import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(page_title="RecruitAI Outreach Demo", layout="centered")

# ====================== SECRETS ======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is missing. Add it in Streamlit → Settings → Secrets.")
    st.stop()

# ====================== LLM (Simple & Stable - what worked before) ======================
llm = LLM(
    model="groq/llama-3.1-8b-instant",   # Fast model with better rate limits for demo
    temperature=0.4,
    max_tokens=1200,
)

current_date = datetime.date.today().strftime("%Y-%m-%d")

compliance_backstory = f"""
NCAA recruiting expert. Public sources only. Current date: {current_date}.
Always include disclaimer in messages. Never suggest violating rules.
"""

# ====================== AGENTS (Simple - no tools yet) ======================
researcher = Agent(
    role="Target & Fit Researcher",
    goal="Find 8-12 strong school/coach fits",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False,
    allow_delegation=False
)

contact_finder = Agent(
    role="Coach Contact Finder",
    goal="Find public coach contacts",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False,
    allow_delegation=False
)

personalizer = Agent(
    role="Message Personalizer",
    goal="Write 3 personalized outreach templates",
    backstory="Write concise, respectful recruiting emails.",
    llm=llm,
    verbose=False,
    allow_delegation=False
)

compliance_guard = Agent(
    role="Compliance Guardian",
    goal="Review for NCAA compliance and suggest timing",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False,
    allow_delegation=False
)

# ====================== UI ======================
st.title("🏈 RecruitAI – Athlete Outreach Demo (Stable Version)")
st.markdown("**Football • Basketball • Soccer** – Simple & working configuration")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position", "QB")
class_year = st.text_input("Class Year", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Targets", "Texas")
stats = st.text_area("Key Stats + Highlights Link", "2,800 passing yards, 32 TDs... hudl.com/...")
other = st.text_area("Additional Notes", "")

athlete_input = f"{sport} | {position} | Class of {class_year} | GPA {gpa} | {location} | {stats} | {other}"

if st.button("🚀 Run Outreach Crew", type="primary"):
    with st.spinner("Running crew... (30–60 seconds)"):
        try:
            task1 = Task(
                description=f"Research target schools for: {athlete_input}",
                expected_output="Numbered list of 8-12 schools with brief fit rationale.",
                agent=researcher
            )

            task2 = Task(
                description="Find public coach contacts from the targets.",
                expected_output="List of coaches with contact info.",
                agent=contact_finder
            )

            task3 = Task(
                description=f"Draft 3 outreach email templates for: {athlete_input}",
                expected_output="3 templates with Subject and Body + disclaimer.",
                agent=personalizer
            )

            task4 = Task(
                description="Review for NCAA compliance and suggest timing.",
                expected_output="Compliance verdict + schedule.",
                agent=compliance_guard
            )

            outreach_crew = Crew(
                agents=[researcher, contact_finder, personalizer, compliance_guard],
                tasks=[task1, task2, task3, task4],
                process=Process.sequential,
                verbose=False,
                max_rpm=10,
                memory=False
            )

            result = outreach_crew.kickoff(inputs={"athlete_input": athlete_input})

            st.success("✅ Done!")
            st.markdown("### Results")
            st.write(result)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.caption("Stable rollback version • No web tools yet • Public data only")
