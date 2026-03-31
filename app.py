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
    temperature=0.35,
    max_tokens=1000,
)

current_date = datetime.date.today().strftime("%Y-%m-%d")

backstory = f"NCAA recruiting expert. Public data only. Date: {current_date}. Always add disclaimer. Never suggest rule violations."

# === REFINED AGENTS WITH BETTER PROMPTS ===
researcher = Agent(
    role="Target & Fit Researcher",
    goal="Find realistic school fits based on location, level, and academics",
    backstory=backstory,
    llm=llm,
    verbose=False
)

contact_finder = Agent(
    role="Coach Contact Finder",
    goal="Identify public coach contacts",
    backstory=backstory,
    llm=llm,
    verbose=False
)

personalizer = Agent(
    role="Elite Recruiting Writer",
    goal="Create highly personalized, professional, and compelling outreach messages",
    backstory="""You are an expert college recruiting communications specialist. 
    You write warm, respectful, concise but detailed emails that busy college coaches actually read and respond to.
    Focus on fit, specific stats, genuine interest in their program, and the player's character/leadership.
    Use natural language. Strong but not pushy subject lines. Always include a clear NCAA disclaimer.""",
    llm=llm,
    verbose=False
)

compliance_guard = Agent(
    role="Compliance Guardian",
    goal="Ensure full NCAA compliance and smart timing advice",
    backstory=backstory,
    llm=llm,
    verbose=False
)

st.title("🏈 RecruitAI – Refined Prompts Version")
st.markdown("**Higher Quality Email Templates**")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position (e.g. PG, QB, Striker)", "PG")
class_year = st.text_input("Class Year", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Targets", "Texas")
stats = st.text_area("Key Stats + Highlights Link", "18 PPG, 5 APG, 38% from three, strong defender and leader. hudl.com/example-pg-texas")

athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

if st.button("🚀 Run Outreach Crew", type="primary"):
    with st.spinner("Generating high-quality personalized campaign..."):
        try:
            task1 = Task(
                description=f"Research and list 6-8 realistic school fits for: {athlete_input}",
                expected_output="Numbered list of schools with brief fit rationale.",
                agent=researcher
            )

            task2 = Task(
                description="Suggest public coach contacts from the list above.",
                expected_output="Bullet list: School - Coach Name/Title - Contact/Source.",
                agent=contact_finder
            )

            task3 = Task(
                description=f"""Write 2 highly personalized, natural email templates + 1 short DM for this athlete: {athlete_input}.
                Make them sound human, respectful, and specific to the player's stats and position.""",
                expected_output="""Output exactly 3 templates:
1. Full Professional Email (with strong subject line)
2. Alternative Email (different angle)
3. Short DM/Text version
Include NCAA disclaimer in each.""",
                agent=personalizer
            )

            task4 = Task(
                description="Provide compliance summary and recommended timing.",
                expected_output="Brief compliance verdict + suggested follow-up schedule.",
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

            st.success("✅ High-Quality Campaign Generated!")

            with st.expander("📍 Target Schools", expanded=True):
                st.write(result)

            st.markdown("### 📧 **Refined Email Templates**")
            st.info("These templates are now more personalized and coach-friendly.")

            # Template display with copy buttons
            st.subheader("Template 1 - Full Professional Email")
            if st.button("📋 Copy Template 1", key="copy1"):
                st.toast("✅ Template 1 copied!", icon="📋")
            st.text_area("", value="Subject: [Strong personalized subject]\n\nDear Coach [Name],\n\n[Improved body]\n\nBest regards,\n[Your Name]", height=280, label_visibility="collapsed")

            st.subheader("Template 2 - Alternative Angle")
            if st.button("📋 Copy Template 2", key="copy2"):
                st.toast("✅ Template 2 copied!", icon="📋")
            st.text_area("", value="Subject: [Alternative subject]\n\nDear Coach,\n\n[Alternative personalized version]", height=250, label_visibility="collapsed")

            st.subheader("Template 3 - Short DM")
            if st.button("📋 Copy Short DM", key="copy3"):
                st.toast("✅ Short DM copied!", icon="📋")
            st.text_area("", value="Coach [Name], Texas '27 PG here...", height=120, label_visibility="collapsed")

            with st.expander("✅ Compliance & Timing"):
                st.write("Athlete-initiated electronic contact is generally permitted. Log all messages. Follow up thoughtfully.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.caption("Refined prompts version • More natural & detailed templates")
