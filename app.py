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

# ====================== LLM (Light & Fast) ======================
llm = LLM(
    model="groq/llama-3.1-8b-instant",   # Highest speed + decent limits for demo
    temperature=0.3,
    max_tokens=1200,                     # Cap output size
)

current_date = datetime.date.today().strftime("%Y-%m-%d")

# Short & efficient backstory (reduces repeated tokens dramatically)
compliance_backstory = f"""
NCAA compliance expert. Public sources only (.edu, MaxPreps, 247). 
Current date: {current_date}. Always add disclaimer. Never violate rules.
"""

# ====================== AGENTS (with tools) ======================
researcher = Agent(
    role="Target Researcher",
    goal="Find 8-10 realistic school fits using web search",
    backstory=compliance_backstory,
    llm=llm,
    tools=[search_tool] if search_tool else [],
    verbose=False,
    allow_delegation=False
)

contact_finder = Agent(
    role="Coach Contact Finder",
    goal="Find public coach contacts via search and scraping",
    backstory=compliance_backstory,
    llm=llm,
    tools=[search_tool, scrape_tool] if search_tool else [scrape_tool],
    verbose=False,
    allow_delegation=False
)

personalizer = Agent(
    role="Message Personalizer",
    goal="Create 3 short, professional outreach templates",
    backstory="Write concise recruiting emails that respect coaches' time.",
    llm=llm,
    verbose=False,
    allow_delegation=False
)

compliance_guard = Agent(
    role="Compliance Guardian",
    goal="Check NCAA rules and suggest timing",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False,
    allow_delegation=False
)

# Manager for hierarchical process (helps control token flow)
manager = Agent(
    role="Recruiting Project Manager",
    goal="Coordinate the crew and keep outputs concise",
    backstory="You ensure efficient, high-quality recruiting campaigns.",
    llm=llm,
    verbose=False
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
    with st.spinner("Crew is searching the web and generating outreach... (45–90 seconds)"):
        try:
            task1 = Task(
                description=f"Quickly research 8-10 good-fit schools for this athlete: {athlete_input}. Keep it brief.",
                expected_output="Short numbered list of schools with 1-2 sentence fit rationale each.",
                agent=researcher
            )

            task2 = Task(
                description="From the list above, find public coach contact info.",
                expected_output="Bullet list: School - Coach Name - Contact/Source (keep very short).",
                agent=contact_finder
            )

            task3 = Task(
                description=f"Write 3 short, natural outreach email templates for: {athlete_input}",
                expected_output="3 templates labeled 1,2,3 with Subject and Body. Include disclaimer.",
                agent=personalizer
            )

            task4 = Task(
                description="Review for compliance and suggest safe timing.",
                expected_output="Short compliance summary + recommended schedule.",
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

            st.success("✅ Campaign Generated with Web Tools!")
            st.markdown("### 📋 Full Results")
            st.write(result)

        except Exception as e:
            st.error(f"❌ Error running crew: {str(e)}")
            st.info("Tip: Try a shorter athlete description or check Groq rate limits.")

st.caption("Demo uses Serper + ScrapeWebsiteTool • Public data only • Always verify contacts & NCAA rules manually")
