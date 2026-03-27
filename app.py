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
st.markdown("**Improved Email Templates Version** • More Detailed & Personalized")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position (e.g. PG, QB, Striker)", "PG")
class_year = st.text_input("Class Year", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Targets", "Texas")
stats = st.text_area("Key Stats + Highlights Link (keep reasonably short)", "18 PPG, 5 APG, 38% from three, strong defender. hudl.com/example-pg-texas")

athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

if st.button("🚀 Run Outreach Crew", type="primary"):
    with st.spinner("Generating improved detailed outreach campaign..."):
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
                description=f"Write 2 detailed, natural, and compelling email templates + 1 short DM version for: {athlete_input}",
                expected_output="Provide 3 outputs:\n1. Long Email Template (full professional email)\n2. Alternative Email Template (different angle)\n3. Short DM/Text Template\nInclude strong subject lines and NCAA disclaimer.",
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

            st.success("✅ Improved Campaign Generated!")

            with st.expander("📍 Target Schools & Fit", expanded=True):
                st.write(result)   # Full result for now - we can parse better later

            st.markdown("### 📧 **Detailed Email Templates**")
            st.info("Copy and customize with your real name, exact stats, and highlights link.")

            # Nice formatted templates area
            st.subheader("Template 1 - Professional Full Email")
            st.text_area("Copy Template 1", 
                        value="Subject: Texas Point Guard (Class of 2027) Interested in Your Program\n\nDear Coach [Last Name],\n\nMy name is [Your Full Name], a [height if known] point guard from [High School], Texas (Class of 2027, 3.6 GPA). I've been following your program closely and believe my skill set would be a strong fit.\n\nThis past season I averaged 18 PPG, 5 APG while shooting 38% from three and playing strong defense. As a floor general and leader, I'm excited about the possibility of contributing to [School]...\n\nAttached are my highlights and academic resume. I'd greatly appreciate any opportunity to discuss your program.\n\nThank you for your time.\n\nBest regards,\n[Your Full Name]\n[Phone] | [Email]\n[Highlights Link]\n\n*Disclaimer: This is athlete-initiated electronic communication per NCAA rules. I understand and will comply with all recruiting guidelines.*", 
                        height=300, key="t1")

            st.subheader("Template 2 - Alternative Angle")
            st.text_area("Copy Template 2", 
                        value="Subject: PG Prospect from Texas with Strong Playmaking Ability\n\nDear Coach,\n\nI'm reaching out as a Class of 2027 point guard from Texas who has been impressed with how your team develops guards...\n\n[Personalized body]\n\n*Disclaimer: Athlete-initiated...*", 
                        height=250, key="t2")

            st.subheader("Template 3 - Short DM / Text")
            st.text_area("Copy Short DM", 
                        value="Coach [Last Name], Texas '27 PG here (18 PPG, 5 APG). Really like what you're building at [School]. Highlights: [link]. Would love to chat whenever you have time. Thanks!", 
                        height=150, key="t3")

            with st.expander("✅ Compliance & Timing"):
                st.write("Athlete-initiated electronic contact is generally allowed. Log everything. Follow up in 10-14 days if no response. Always check the latest NCAA calendar.")

            st.caption("More detailed templates • Still using stable low-token settings")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Try again in a few seconds with slightly shorter stats field.")

st.caption("Improved detailed email templates version")
