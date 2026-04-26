import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(page_title="RecruitAI", page_icon="🏈", layout="wide")

with st.sidebar:
    st.title("🏈 RecruitAI")
    st.markdown("**Athlete Outreach Assistant**")
    st.caption("Clean • Fast • Compliant")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing.")
    st.stop()

llm = LLM(model="groq/llama-3.1-8b-instant", temperature=0.3, max_tokens=800)

current_date = datetime.date.today().strftime("%Y-%m-%d")
backstory = f"NCAA expert. Public data only. Date: {current_date}. Add disclaimer."

researcher = Agent(role="Researcher", goal="List realistic school fits", backstory=backstory, llm=llm, verbose=False)
personalizer = Agent(role="Recruiting Writer", goal="Write distinct outreach messages", backstory="Create natural templates. Make them clearly different.", llm=llm, verbose=False)
compliance_guard = Agent(role="Compliance", goal="Check rules & timing", backstory=backstory, llm=llm, verbose=False)

st.title("🏈 RecruitAI")
st.markdown("**Generate clean, compliant coach outreach**")

# Input Form
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Select Sport", "Football", "Basketball", "Soccer"], index=0)
        position = st.text_input("Position", "PG")
        class_year = st.text_input("Class Year", "2027")
    with col2:
        gpa = st.text_input("GPA", "3.6")
        location = st.text_input("Location / Targets", "Texas")
    
    stats = st.text_area("Key Stats + Highlights Link (keep short)", 
                        "18 PPG, 5 APG, 38% from three. hudl.com/example", height=80)

    athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

    if st.button("🚀 Generate Full Campaign", type="primary", use_container_width=True):
        if sport == "Select Sport":
            st.warning("Please select a sport.")
        else:
            with st.spinner("Generating campaign..."):
                try:
                    # Step 1: Schools
                    task1 = Task(
                        description=f"List 6-8 realistic school fits with brief rationale for: {athlete_input}",
                        expected_output="Numbered list of schools with fit rationale.",
                        agent=researcher
                    )

                    # Step 2: Templates
                    task2 = Task(
                        description=f"Write 2 different email templates + 1 short DM for: {athlete_input}",
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
                        max_rpm=6,
                        memory=False
                    )

                    result = crew.kickoff(inputs={"athlete_input": athlete_input})

                    st.success("✅ Campaign Generated")

                    # Display Results
                    st.subheader("📍 1. Recommended Schools")
                    with st.expander("View schools and fit rationale", expanded=True):
                        st.markdown(result)

                    st.subheader("📧 2. Outreach Templates")
                    st.caption("Click to copy • Customize with your details")

                    # Templates (placeholder for now - real content will come from result)
                    st.markdown("**Template 1** — Character & Leadership Focused")
                    if st.button("📋 Copy", key="copy1"):
                        st.toast("✅ Copied!", icon="📋")
                    st.text_area("Template 1", value="Template 1 content...", height=180, label_visibility="collapsed")

                    st.markdown("**Template 2** — Stats & Skills Focused")
                    if st.button("📋 Copy", key="copy2"):
                        st.toast("✅ Copied!", icon="📋")
                    st.text_area("Template 2", value="Template 2 content...", height=180, label_visibility="collapsed")

                    st.markdown("**Short DM**")
                    if st.button("📋 Copy DM", key="copy3"):
                        st.toast("✅ Copied!", icon="📋")
                    st.text_area("Short DM", value="Short DM content...", height=110, label_visibility="collapsed")

                    # === DOWNLOAD BUTTON ===
                    full_campaign = f"""RECRUITAI CAMPAIGN REPORT
Generated on {current_date}

Athlete Profile:
{sport} {position} | Class of {class_year} | GPA {gpa} | {location}
Stats: {stats}

1. RECOMMENDED SCHOOLS:
{result}

2. OUTREACH TEMPLATES:
[Template 1]
[Template 2]
[Short DM]

3. COMPLIANCE:
Athlete-initiated contact is generally allowed. Log all messages.
"""

                    st.download_button(
                        label="📥 Download Full Campaign as .txt",
                        data=full_campaign,
                        file_name=f"RecruitAI_{sport}_{position}_{class_year}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                    with st.expander("✅ Compliance & Next Steps"):
                        st.write("Athlete-initiated electronic contact is generally allowed. Always log communications and check the current NCAA calendar.")

                except Exception as e:
                    if "rate limit" in str(e).lower():
                        st.error("⏳ Rate limit reached. Please wait 15–30 seconds and try again.")
                    else:
                        st.error(f"Error: {str(e)}")

st.caption("Schools-first version with Download button")
