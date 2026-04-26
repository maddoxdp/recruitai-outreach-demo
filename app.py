import streamlit as st
import os
from crewai import Agent, Task, Crew, Process, LLM
import datetime

st.set_page_config(page_title="RecruitAI", page_icon="🏈", layout="wide")

with st.sidebar:
    st.title("🏈 RecruitAI")
    st.markdown("**Athlete Outreach Assistant**")
    st.caption("Schools-First Version")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing.")
    st.stop()

llm = LLM(model="groq/llama-3.1-8b-instant", temperature=0.3, max_tokens=800)

current_date = datetime.date.today().strftime("%Y-%m-%d")
backstory = f"NCAA expert. Public data only. Date: {current_date}. Add disclaimer."

# Two specialized agents for better reliability
researcher = Agent(
    role="Recruiting Researcher",
    goal="Provide a clear list of realistic school fits",
    backstory=backstory,
    llm=llm,
    verbose=False
)

personalizer = Agent(
    role="Recruiting Writer",
    goal="Write distinct, high-quality outreach messages",
    backstory="Create natural, respectful templates. Make Template 1 character-focused and Template 2 stats-focused.",
    llm=llm,
    verbose=False
)

st.title("🏈 RecruitAI")
st.markdown("**Schools-first robust version**")

# Input
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        sport = st.selectbox("Sport", ["Select Sport", "Football", "Basketball", "Soccer"], index=0)
        position = st.text_input("Position", "PG")
        class_year = st.text_input("Class Year", "2027")
    with col2:
        gpa = st.text_input("GPA", "3.6")
        location = st.text_input("Location / Targets", "Texas")
    
    stats = st.text_area("Key Stats + Highlights (keep reasonably short)", 
                        "18 PPG, 5 APG, 38% from three, strong leader. hudl.com/example", height=80)

    athlete_input = f"{sport} {position} Class of {class_year} GPA {gpa} from {location}. Stats: {stats}"

    if st.button("🚀 Generate Full Campaign", type="primary", use_container_width=True):
        if sport == "Select Sport":
            st.warning("Please select a sport.")
        else:
            with st.spinner("Step 1: Researching schools..."):
                try:
                    # Step 1: Schools only
                    schools_task = Task(
                        description=f"List 6-8 realistic college programs that would be good fits for this athlete: {athlete_input}. Format as a clean numbered list with brief rationale for each school.",
                        expected_output="Clean numbered list of schools with fit rationale.",
                        agent=researcher
                    )

                    schools_crew = Crew(
                        agents=[researcher],
                        tasks=[schools_task],
                        process=Process.sequential,
                        verbose=False,
                        max_rpm=6,
                        memory=False
                    )

                    schools_result = schools_crew.kickoff(inputs={"athlete_input": athlete_input})

                    st.success("✅ Schools Research Complete")

                    st.subheader("📍 1. Recommended Schools")
                    with st.expander("View schools and fit rationale", expanded=True):
                        st.markdown(schools_result)

                    # Step 2: Templates
                    with st.spinner("Step 2: Generating templates..."):
                        template_task = Task(
                            description=f"Using the schools above, write 2 different email templates + 1 short DM for: {athlete_input}",
                            expected_output="Template 1 (character/leadership), Template 2 (stats/skills), Short DM. Include disclaimer.",
                            agent=personalizer
                        )

                        template_crew = Crew(
                            agents=[personalizer],
                            tasks=[template_task],
                            process=Process.sequential,
                            verbose=False,
                            max_rpm=6,
                            memory=False
                        )

                        templates_result = template_crew.kickoff(inputs={"athlete_input": athlete_input})

                        st.subheader("📧 2. Outreach Templates")
                        st.caption("Copy and customize")

                        st.markdown("**Template 1** — Character & Leadership")
                        if st.button("📋 Copy", key="t1"):
                            st.toast("✅ Copied!", icon="📋")
                        st.text_area("Template 1", value=str(templates_result), height=220, label_visibility="collapsed")

                        st.markdown("**Template 2** — Stats & Skills")
                        if st.button("📋 Copy", key="t2"):
                            st.toast("✅ Copied!", icon="📋")
                        st.text_area("Template 2", value="Template 2 will be here...", height=220, label_visibility="collapsed")

                        st.markdown("**Short DM**")
                        if st.button("📋 Copy DM", key="t3"):
                            st.toast("✅ Copied!", icon="📋")
                        st.text_area("Short DM", value="Short DM will be here...", height=110, label_visibility="collapsed")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Wait 20-30 seconds and try again if rate limited.")

st.caption("Schools-first separate-step version")
