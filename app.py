import streamlit as st
import os
import time
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(page_title="RecruitAI", layout="wide")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing. Add it in Streamlit Secrets.")
    st.stop()

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.3,
    max_tokens=700,        # Even stricter cap
)

current_date = datetime.date.today().strftime("%Y-%m-%d")
backstory = f"NCAA expert. Public data only. Date: {current_date}. Add disclaimer."

# Very lightweight agents
researcher = Agent(role="Researcher", goal="List school fits & contacts", backstory=backstory, llm=llm, verbose=False)
personalizer = Agent(
    role="Recruiting Writer",
    goal="Write 2 different short email templates + 1 DM",
    backstory="Write natural, respectful recruiting messages. Make the two emails clearly different (one character-focused, one stats-focused).",
    llm=llm,
    verbose=False
)
compliance_guard = Agent(role="Compliance", goal="Check rules & timing", backstory=backstory, llm=llm, verbose=False)

st.title("🏈 RecruitAI – Ultra Light Version")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position", "PG")
class_year = st.text_input("Class Year", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Targets", "Texas")
stats = st.text_area("Key Stats (keep very short)", "18 PPG, 5 APG, 38% 3PT. hudl.com/example")

athlete_input = f"{sport} {position} {class_year} GPA {gpa} {location} {stats}"

if st.button("🚀 Generate Outreach", type="primary"):
    with st.spinner("Running light crew..."):
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
                max_rpm=6,      # Very conservative
                memory=False
            )

            result = crew.kickoff(inputs={"athlete_input": athlete_input})

            st.success("✅ Done!")

            with st.expander("📍 Schools & Contacts", expanded=True):
                st.write(result)

            st.subheader("📧 Templates")
            st.text_area("Template 1", value="Copy from output...", height=180)
            st.text_area("Template 2", value="Copy from output...", height=180)
            st.text_area("Short DM", value="Copy from output...", height=100)

            with st.expander("✅ Compliance"):
                st.write("Safe for electronic outreach in most cases. Log everything.")

        except Exception as e:
            if "rate limit" in str(e).lower() or "tokens" in str(e).lower():
                st.error("Rate limit reached. Please wait 10–30 seconds and try again.")
                st.info("Tip: Use shorter stats field or wait longer between runs.")
            else:
                st.error(f"Error: {str(e)}")

st.caption("Ultra-light version to stay under Groq limits • Wait between runs")
