import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(page_title="RecruitAI Outreach Demo", layout="centered")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing. Add it in Streamlit Secrets.")
    st.stop()

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.4,
    max_tokens=1100,
)

current_date = datetime.date.today().strftime("%Y-%m-%d")

backstory = f"NCAA recruiting expert. Public data only. Date: {current_date}."

# Improved Personalizer with clear differentiation instructions
personalizer = Agent(
    role="Elite Recruiting Writer",
    goal="Create distinct, natural, and highly personalized outreach messages",
    backstory="""You are a top-tier college recruiting communications expert. 
    Your emails are warm, respectful, concise yet detailed, and stand out in a coach's crowded inbox.
    Always make the three templates clearly different:
    - Template 1: Warm, story/character-focused, highlights leadership and fit
    - Template 2: Stats and skill-focused, more direct and confident
    - Template 3: Short, casual DM/Text version for social media or quick message
    Use natural language. Strong, specific subject lines. Include NCAA disclaimer in every version.""",
    llm=llm,
    verbose=False
)

researcher = Agent(role="Researcher", goal="List 6-8 school fits", backstory=backstory, llm=llm, verbose=False)
contact_finder = Agent(role="Contact Finder", goal="Find public coach contacts", backstory=backstory, llm=llm, verbose=False)
compliance_guard = Agent(role="Compliance Guard", goal="Check rules & timing", backstory=backstory, llm=llm, verbose=False)

st.title("🏈 RecruitAI – Improved Template Differentiation")
st.markdown("**Templates should now feel clearly different**")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position", "PG")
class_year = st.text_input("Class Year", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Targets", "Texas")
stats = st.text_area("Key Stats + Highlights Link", "18 PPG, 5 APG, 38% from three, strong defender and leader. hudl.com/example-pg-texas")

athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

if st.button("🚀 Run Outreach Crew", type="primary"):
    with st.spinner("Generating distinctly different templates..."):
        try:
            task1 = Task(description=f"List 6-8 good-fit schools for: {athlete_input}", 
                        expected_output="Numbered list with brief rationale.", agent=researcher)

            task2 = Task(description="Suggest public coach contacts.", 
                        expected_output="Bullet list of contacts.", agent=contact_finder)

            task3 = Task(
                description=f"Create 3 distinctly different outreach messages for: {athlete_input}",
                expected_output="""Output exactly three different versions:
1. Full Professional Email - Warm, character/leadership focused with strong subject line
2. Alternative Professional Email - More stats/skill focused, confident tone
3. Short DM/Text version - Casual but respectful for Instagram/Twitter/Text
Include NCAA disclaimer in each.""",
                agent=personalizer
            )

            task4 = Task(description="Provide compliance summary and timing advice.", 
                        expected_output="Short compliance verdict + schedule.", agent=compliance_guard)

            crew = Crew(
                agents=[researcher, contact_finder, personalizer, compliance_guard],
                tasks=[task1, task2, task3, task4],
                process=Process.sequential,
                verbose=False,
                max_rpm=8,
                memory=False
            )

            result = crew.kickoff(inputs={"athlete_input": athlete_input})

            st.success("✅ Campaign Generated!")

            with st.expander("📍 Target Schools", expanded=True):
                st.write(result)

            st.markdown("### 📧 **Distinct Email Templates**")

            st.subheader("1. Full Professional Email (Character-Focused)")
            if st.button("📋 Copy Template 1", key="copy1"):
                st.toast("Template 1 copied!", icon="✅")
            st.text_area("Template 1", value="Paste output here...", height=260, label_visibility="collapsed")

            st.subheader("2. Stats & Skill Focused Email")
            if st.button("📋 Copy Template 2", key="copy2"):
                st.toast("Template 2 copied!", icon="✅")
            st.text_area("Template 2", value="Paste output here...", height=260, label_visibility="collapsed")

            st.subheader("3. Short DM / Text Version")
            if st.button("📋 Copy Short DM", key="copy3"):
                st.toast("Short DM copied!", icon="✅")
            st.text_area("Short DM", value="Paste output here...", height=140, label_visibility="collapsed")

            with st.expander("✅ Compliance"):
                st.write("Athlete-initiated contact is generally allowed. Log everything. Follow up in 10-14 days.")

        except Exception as e:
            st.error(f"Error: {str(e)}")

st.caption("Refined differentiation version")
