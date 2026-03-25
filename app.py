import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_groq import ChatGroq
import datetime
import os
import json

# Secrets (set these in Streamlit Cloud → Secrets tab)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not GROQ_API_KEY or not SERPER_API_KEY:
    st.error("Missing API keys. Add GROQ_API_KEY and SERPER_API_KEY in app secrets.")
    st.stop()

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model="llama3-70b-8192", temperature=0.4)

search_tool = SerperDevTool(api_key=SERPER_API_KEY)
scrape_tool = ScrapeWebsiteTool()

current_date = datetime.date.today().strftime("%Y-%m-%d")

compliance_backstory = f"""
NCAA recruiting expert (2025-26 rules). Public data only (MaxPreps, Hudl public, .edu sites).
Football: Electronic June 15 post-sophomore; calls limited.
Basketball/Soccer: Electronic June 15 post-sophomore.
Current date: {current_date}. Flag timing. Always add disclaimer.
"""

# Simplified agents (condensed for demo speed; expand later)
researcher = Agent(role="Researcher", goal="Find fits", backstory=compliance_backstory, tools=[search_tool], llm=llm, verbose=False)
contact_finder = Agent(role="Contact Finder", goal="Get contacts", backstory=compliance_backstory, tools=[search_tool, scrape_tool], llm=llm, verbose=False)
# ... (add enricher, personalizer, compliance_guard similarly – keep verbose=False for speed)

st.title("RecruitAI – Athlete Outreach Demo")
st.markdown("Generate personalized, compliant coach outreach for football, basketball, soccer. Free demo – results simulated/condensed.")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position (e.g., QB, SG, Forward)", "QB")
class_year = st.text_input("Class Year (e.g., 2027)", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Targets (e.g., Texas D1)", "Texas")
stats = st.text_area("Key Stats / Highlights Link", "2,800 yds, 32 TDs... hudl.com/...")
other = st.text_area("Other Notes (optional)", "")

athlete_input = f"{sport}, {position}, Class of {class_year}, GPA {gpa}, {location}, {stats}. {other}"

if st.button("Run Outreach Crew (may take 1–3 min)"):
    with st.spinner("Crew researching & drafting..."):
        try:
            # Simplified task chain for demo
            task1 = Task(description=f"Research 10 top school fits for: {athlete_input}", agent=researcher, expected_output="JSON list")
            # Add more tasks... (in full version, chain all 5)

            demo_crew = Crew(
                agents=[researcher, contact_finder],  # expand with all agents
                tasks=[task1],  # expand
                process=Process.sequential,
                verbose=False
            )

            result = demo_crew.kickoff(inputs={"athlete_input": athlete_input})

            st.success("Done!")
            st.subheader("Results (Demo – Condensed)")
            st.json(result)  # or parse & format nicely

            st.info("In full SaaS: CSV/PDF export, full templates, compliance log. This demo shows core flow.")

        except Exception as e:
            st.error(f"Error: {str(e)}\nCheck API keys / rate limits.")

st.markdown("---")
st.caption("Powered by CrewAI + Groq + Serper. Public demo only – add your keys in Streamlit secrets.")
