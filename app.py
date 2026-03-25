import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM   # ← Added LLM
from langchain_groq import ChatGroq   # Keep for optional fallback
import datetime

st.set_page_config(page_title="RecruitAI Outreach Demo", layout="centered")

# ====================== SECRETS & CONFIG ======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is missing. Add it in Streamlit → Settings → Secrets.")
    st.stop()

# === NEW RECOMMENDED WAY: Use CrewAI's native LLM wrapper ===
llm = LLM(
    model="groq/llama3-70b-8192",      # This tells CrewAI to use Groq under the hood
    temperature=0.4,
    # api_key is automatically read from GROQ_API_KEY env var
)

current_date = datetime.date.today().strftime("%Y-%m-%d")

compliance_backstory = f"""
You are an NCAA recruiting compliance expert (2025-26 rules). 
Use only public sources (.edu sites, MaxPreps, 247Sports, official team pages).
Football electronic contact generally safe after June 15 post-sophomore year.
Basketball/Soccer: June 15 after sophomore year.
Current date: {current_date}. Always include a clear disclaimer in every message.
Never suggest violating NCAA rules.
"""

# ====================== AGENTS ======================
researcher = Agent(
    role="Target & Fit Researcher",
    goal="Find 8-12 strong school/coach fits for the athlete",
    backstory=compliance_backstory,
    llm=llm,          # ← Now using CrewAI LLM
    verbose=False
)

contact_finder = Agent(
    role="Coach Contact Finder",
    goal="Find public coach emails or staff directory links",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False
)

personalizer = Agent(
    role="Message Personalizer",
    goal="Write personalized, professional outreach emails/DMs",
    backstory="You write concise, respectful recruiting emails that stand out to busy coaches.",
    llm=llm,
    verbose=False
)

compliance_guard = Agent(
    role="Compliance Guardian",
    goal="Review everything for NCAA compliance and suggest safe timing",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False
)

# ====================== STREAMLIT UI ======================
st.title("🏈 RecruitAI – Athlete Outreach Demo")
st.markdown("**Football / Basketball / Soccer** – Generate personalized, compliant coach outreach in minutes.")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position (e.g. QB, SG, Striker)", "QB")
class_year = st.text_input("Class Year (e.g. 2027)", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Preferred Targets (e.g. Texas D1)", "Texas")
stats = st.text_area("Key Stats + Highlights Link", "2,800 passing yards, 32 TDs, 68% completion. Highlights: hudl.com/profile/example")
other = st.text_area("Additional Notes (optional)", "Team captain, dual-threat elements")

athlete_input = f"{sport} | {position} | Class of {class_year} | GPA {gpa} | {location} | Stats: {stats} | {other}"

if st.button("🚀 Run Outreach Crew", type="primary"):
    with st.spinner("Crew is researching targets, finding contacts, and drafting messages... (this can take 30–90 seconds)"):
        try:
            # Define tasks (chained)
            task1 = Task(
                description=f"Research strong target schools and programs for this athlete: {athlete_input}",
                expected_output="A numbered list of 8-12 schools with brief fit rationale and any known coach needs.",
                agent=researcher
            )

            task2 = Task(
                description="From the targets above, find public coach contact information (emails or staff pages).",
                expected_output="List of coaches with contact details and source.",
                agent=contact_finder
            )

            task3 = Task(
                description=f"Draft 3 personalized outreach email/DM templates for the athlete: {athlete_input}",
                expected_output="3 ready-to-use email templates (Subject + Body) with NCAA disclaimer.",
                agent=personalizer
            )

            task4 = Task(
                description="Review the entire output for NCAA compliance and suggest safe send timing.",
                expected_output="Compliance verdict, risks, and follow-up schedule.",
                agent=compliance_guard
            )

            outreach_crew = Crew(
                agents=[researcher, contact_finder, personalizer, compliance_guard],
                tasks=[task1, task2, task3, task4],
                process=Process.sequential,
                verbose=False
            )

            result = outreach_crew.kickoff(inputs={"athlete_input": athlete_input})

            st.success("✅ Campaign Generated!")
            st.markdown("### Results")
            st.write(result)

            st.info("In the full SaaS version we will add CSV/PDF export and more polished formatting.")

        except Exception as e:
            st.error(f"Error running crew: {str(e)}")
            st.info("Tip: Check that your GROQ_API_KEY is correct and has credits.")

st.caption("Demo powered by CrewAI + Groq • Public data only • Always verify contacts & NCAA rules manually")
