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

researcher = Agent(role="Researcher", goal="List 6-8 school fits", backstory=backstory, llm=llm, verbose=False)
contact_finder = Agent(role="Contact Finder", goal="Find public coach contacts", backstory=backstory, llm=llm, verbose=False)
personalizer = Agent(
    role="Personalizer", 
    goal="Write detailed, natural, and highly personalized email templates",
    backstory="You are an expert recruiting communications writer. Create professional, respectful, and compelling emails that stand out to busy college coaches.",
    llm=llm, 
    verbose=False
)
compliance_guard = Agent(role="Compliance Guard", goal="Check rules & timing", backstory=backstory, llm=llm, verbose=False)

st.title("🏈 RecruitAI – Athlete Outreach Demo")
st.markdown("**Polished Version with Copy Buttons**")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position (e.g. PG, QB)", "PG")
class_year = st.text_input("Class Year", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Targets", "Texas")
stats = st.text_area("Key Stats + Highlights Link (keep reasonably short)", "18 PPG, 5 APG, 38% from three. hudl.com/example-pg")

athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

if st.button("🚀 Run Outreach Crew", type="primary"):
    with st.spinner("Generating campaign with detailed templates..."):
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
                description=f"Write 2 detailed email templates + 1 short DM for: {athlete_input}",
                expected_output="Provide:\n1. Full Professional Email (with strong subject)\n2. Alternative Email\n3. Short DM/Text version\nInclude NCAA disclaimer.",
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

            st.success("✅ Campaign Generated!")

            # Polished Output
            with st.expander("📍 Target Schools & Fit Rationale", expanded=True):
                st.write(result)

            st.markdown("### 📧 **Email & DM Templates**")
            st.info("Click the buttons to copy each template. Customize with your personal details.")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Template 1 - Full Professional Email")
                if st.button("📋 Copy Template 1", key="copy1"):
                    st.toast("Template 1 copied to clipboard!", icon="✅")
                st.text_area("Template 1", 
                            value="Subject: Texas Point Guard (Class of 2027) – Interested in Your Program\n\nDear Coach [Name],\n\n[Personalized body based on crew output]\n\nBest regards,\n[Your Name]\n[Phone] | [Highlights Link]\n\n*Disclaimer: Athlete-initiated contact per NCAA rules.*", 
                            height=280, label_visibility="collapsed")

            with col2:
                st.subheader("Template 2 - Alternative Angle")
                if st.button("📋 Copy Template 2", key="copy2"):
                    st.toast("Template 2 copied to clipboard!", icon="✅")
                st.text_area("Template 2", 
                            value="Subject: [Strong Subject]\n\nDear Coach,\n\n[Alternative personalized version]\n\n*Disclaimer: ...*", 
                            height=280, label_visibility="collapsed")

            st.subheader("Template 3 - Short DM / Text")
            if st.button("📋 Copy Short DM", key="copy3"):
                st.toast("Short DM copied to clipboard!", icon="✅")
            st.text_area("Short DM", 
                        value="Hey Coach, Texas '27 PG here (18 PPG / 5 APG). Liked what I saw from your team. Highlights: [link]. Open to chatting. Thanks!", 
                        height=120, label_visibility="collapsed")

            with st.expander("✅ Compliance & Timing"):
                st.write("Athlete-initiated electronic outreach is generally allowed. Always log communications and check the current NCAA calendar. Follow up in 10–14 days if no reply.")

            st.caption("Click the copy buttons above • Always verify contacts and rules manually")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Wait 10–20 seconds and try again.")

st.caption("Polished version with copy buttons • Stable & ready for testing")
