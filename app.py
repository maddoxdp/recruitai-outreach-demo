import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import datetime

st.set_page_config(page_title="RecruitAI Outreach Demo", layout="centered")

# ====================== SECRETS ======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is missing. Add it in Streamlit → Settings → Secrets.")
    st.stop()

if not SERPER_API_KEY:
    st.warning("⚠️ SERPER_API_KEY is missing. Add it in Secrets for full web search power.")

# ====================== TOOLS ======================
search_tool = SerperDevTool() if SERPER_API_KEY else None
scrape_tool = ScrapeWebsiteTool()

# ====================== LLM ======================
llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.3,
    max_tokens=1500,
)

current_date = datetime.date.today().strftime("%Y-%m-%d")

compliance_backstory = f"""
NCAA recruiting expert. Public sources only. Current date: {current_date}.
Always add disclaimer. Never suggest rule violations.
"""

# ====================== AGENTS (with tools) ======================
researcher = Agent(
    role="Target & Fit Researcher",
    goal="Find 8-12 strong school/coach fits using real-time web search",
    backstory=compliance_backstory,
    llm=llm,
    tools=[search_tool] if search_tool else [],
    verbose=False,
    allow_delegation=False
)

contact_finder = Agent(
    role="Coach Contact Finder",
    goal="Find public coach emails and staff directory links using search + scraping",
    backstory=compliance_backstory,
    llm=llm,
    tools=[search_tool, scrape_tool] if search_tool else [scrape_tool],
    verbose=False,
    allow_delegation=False
)

personalizer = Agent(
    role="Message Personalizer",
    goal="Write personalized, professional outreach emails/DMs",
    backstory="You write concise, respectful recruiting emails that stand out to busy coaches.",
    llm=llm,
    verbose=False,
    allow_delegation=False
)

compliance_guard = Agent(
    role="Compliance Guardian",
    goal="Review everything for NCAA compliance and suggest safe timing",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False,
    allow_delegation=False
)

# ====================== UI ======================
st.title("🏈 RecruitAI – Athlete Outreach Demo (with Real Web Tools)")
st.markdown("**Football • Basketball • Soccer** – Now with live web search & scraping for better coach contacts!")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position (e.g. QB, SG, Striker)", "QB")
class_year = st.text_input("Class Year (e.g. 2027)", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Preferred Targets (e.g. Texas D1)", "Texas")
stats = st.text_area("Key Stats + Highlights Link", "2,800 passing yards, 32 TDs, 68% completion. Highlights: hudl.com/profile/tx-qb-2027-example")
other = st.text_area("Additional Notes (optional)", "Team captain, dual-threat QB")

athlete_input = f"{sport} | {position} | Class of {class_year} | GPA {gpa} | {location} | Stats: {stats} | {other}"

if st.button("🚀 Run Outreach Crew with Web Tools", type="primary"):
    with st.spinner("Crew is now searching the web and scraping public pages... (45–120 seconds)"):
        try:
            task1 = Task(
                description=f"Research strong target schools/programs for: {athlete_input}",
                expected_output="Numbered list of 8-12 schools with fit rationale and known coach needs (use web search).",
                agent=researcher
            )

            task2 = Task(
                description="From the targets above, use search + scraping to find public coach contact info (emails/staff pages).",
                expected_output="List of coaches with contact details and source links.",
                agent=contact_finder
            )

            task3 = Task(
                description=f"Draft 3 personalized outreach email/DM templates for: {athlete_input}",
                expected_output="3 ready-to-use templates (Subject + Body) including NCAA disclaimer.",
                agent=personalizer
            )

            task4 = Task(
                description="Review the entire output for NCAA compliance and suggest safe timing.",
                expected_output="Compliance verdict, risks, and follow-up schedule.",
                agent=compliance_guard
            )

            outreach_crew = Crew(
                agents=[researcher, contact_finder, personalizer, compliance_guard],
                tasks=[task1, task2, task3, task4],
                process=Process.sequential,
                verbose=False,
                max_rpm=15,
                memory=False,
            )

            result = outreach_crew.kickoff(inputs={"athlete_input": athlete_input})

            st.success("✅ Campaign Generated with Real Web Data!")
            st.markdown("### 📋 Full Results")
            st.write(result)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.caption("Demo now uses Serper + ScrapeWebsiteTool • Public data only • Always verify contacts & NCAA rules manually")
