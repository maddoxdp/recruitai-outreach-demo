import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(page_title="RecruitAI Outreach Demo", layout="centered")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing. Add it in Streamlit Secrets.")
    st.stop()

# Very lightweight LLM setup
llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.3,
    max_tokens=800,          # Strict cap
)

current_date = datetime.date.today().strftime("%Y-%m-%d")

# Extremely short backstory to save tokens
backstory = f"NCAA expert. Public data only. Date: {current_date}. Add disclaimer. No rule violations."

researcher = Agent(role="Researcher", goal="List 6-8 school fits", backstory=backstory, llm=llm, verbose=False)
contact_finder = Agent(role="Contact Finder", goal="Find public coach contacts", backstory=backstory, llm=llm, verbose=False)
personalizer = Agent(role="Personalizer", goal="Write 2 short email templates", backstory=backstory, llm=llm, verbose=False)
compliance_guard = Agent(role="Compliance Guard", goal="Check rules & timing", backstory=backstory, llm=llm, verbose=False)

st.title("🏈 RecruitAI – Minimal Stable Demo")
st.markdown("**Simple version to stay under rate limits**")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position", "QB")
class_year = st.text_input("Class Year", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Targets", "Texas")
stats = st.text_area("Key Stats + Highlights (keep short)", "2800 yds, 32 TDs. hudl.com/example")

athlete_input = f"{sport} {position} {class_year} GPA {gpa} {location} {stats}"

if st.button("🚀 Run Minimal Crew", type="primary"):
    with st.spinner("Running light crew..."):
        try:
            task1 = Task(description=f"List 6-8 school fits for: {athlete_input}", 
                        expected_output="Short list of schools with 1 sentence each.", 
                        agent=researcher)

            task2 = Task(description="From the list, suggest public coach contacts.", 
                        expected_output="Bullet list of contacts.", 
                        agent=contact_finder)

            task3 = Task(description=f"Write 2 short email templates for: {athlete_input}", 
                        expected_output="2 templates with subject + body + disclaimer.", 
                        agent=personalizer)

            task4 = Task(description="Give compliance summary and timing advice.", 
                        expected_output="Short verdict + schedule.", 
                        agent=compliance_guard)

            crew = Crew(
                agents=[researcher, contact_finder, personalizer, compliance_guard],
                tasks=[task1, task2, task3, task4],
                process=Process.sequential,
                verbose=False,
                max_rpm=8,      # Very conservative
                memory=False
            )

            result = crew.kickoff(inputs={"athlete_input": athlete_input})

            st.success("✅ Generated!")
            st.write(result)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Wait 10-30 seconds and try again, or use a shorter input.")

st.caption("Minimal token usage version • Wait between runs")
