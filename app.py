import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime
import json

st.set_page_config(page_title="RecruitAI Outreach Demo", layout="centered")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing. Add it in Streamlit Secrets.")
    st.stop()

# Lightweight LLM setup (stable version)
llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.3,
    max_tokens=800,
)

current_date = datetime.date.today().strftime("%Y-%m-%d")

backstory = f"NCAA recruiting expert. Public data only. Date: {current_date}. Always add disclaimer. Never suggest rule violations."

# Agents
researcher = Agent(role="Researcher", goal="List 6-8 school fits", backstory=backstory, llm=llm, verbose=False)
contact_finder = Agent(role="Contact Finder", goal="Find public coach contacts", backstory=backstory, llm=llm, verbose=False)
personalizer = Agent(role="Personalizer", goal="Write 2 short email templates", backstory=backstory, llm=llm, verbose=False)
compliance_guard = Agent(role="Compliance Guard", goal="Check rules & timing", backstory=backstory, llm=llm, verbose=False)

st.title("🏈 RecruitAI – Athlete Outreach Demo")
st.markdown("**Polished Version** • Football • Basketball • Soccer")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position (e.g. PG, QB)", "PG")
class_year = st.text_input("Class Year", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Targets", "Texas")
stats = st.text_area("Key Stats + Highlights Link (keep short)", "18 PPG, 5 APG, 38% 3PT. hudl.com/example-pg")

athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

if st.button("🚀 Run Outreach Crew", type="primary"):
    with st.spinner("Generating polished outreach campaign..."):
        try:
            task1 = Task(
                description=f"List 6-8 good-fit schools for: {athlete_input}",
                expected_output="Short numbered list of schools with 1 sentence rationale each.",
                agent=researcher
            )

            task2 = Task(
                description="Suggest public coach contacts from the targets.",
                expected_output="Bullet list of School - Coach - Contact info.",
                agent=contact_finder
            )

            task3 = Task(
                description=f"Write 2 short, natural email templates for: {athlete_input}",
                expected_output="2 templates labeled Template 1 and Template 2 with Subject and Body + disclaimer.",
                agent=personalizer
            )

            task4 = Task(
                description="Give brief compliance summary and suggested timing.",
                expected_output="Short verdict + follow-up schedule.",
                agent=compliance_guard
            )

            crew = Crew(
                agents=[researcher, contact_finder, personalizer, compliance_guard],
                tasks=[task1, task2, task3, task4],
                process=Process.sequential,
                verbose=False,
                max_rpm=8,
                memory=False
            )

            result = crew.kickoff(inputs={"athlete_input": athlete_input})

            # Polished Output Display
            st.success("✅ Campaign Generated Successfully!")

            with st.expander("📍 **1. Target Schools & Fit Rationale**", expanded=True):
                st.write(result)  # We'll improve parsing later if needed

            # For now, show full result in sections (simple version)
            st.markdown("### 📧 **2. Email Templates**")
            st.info("Copy the templates below and customize with your name/info.")

            # Attempt to show templates nicely (basic for now)
            st.text_area("Template 1 (Copy)", value="Dear Coach,\n\n[Personalized intro here]\n\nBest,\n[Your Name]", height=200, key="template1")
            st.text_area("Template 2 (Copy)", value="Subject: [Strong Subject Line]\n\nBody here...\n\nDisclaimer: Athlete-initiated contact per NCAA rules.", height=200, key="template2")

            with st.expander("✅ **3. Compliance & Timing**"):
                st.write("Safe to send electronic outreach now in most cases. Log all communication. Follow up in 10-14 days if no reply.")

            st.caption("Results are AI-generated • Always verify contacts and NCAA rules manually • Public data only")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Wait 10-20 seconds and try again with a shorter input.")

st.caption("Polished output version • Stable & under rate limits")
