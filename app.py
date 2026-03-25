import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
import datetime

st.set_page_config(page_title="RecruitAI Outreach Demo", layout="centered")

# ====================== SECRETS & CONFIG ======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # Optional for now (demo uses basic search)

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY is missing. Add it in Streamlit → Settings → Secrets.")
    st.stop()

# Initialize LLM (fast & cheap on Groq)
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama3-70b-8192",
    temperature=0.4
)

current_date = datetime.date.today().strftime("%Y-%m-%d")

compliance_backstory = f"""
You are an NCAA recruiting compliance expert (2025-26 rules). 
Use only public sources (.edu sites, MaxPreps, 247Sports, official team pages).
Football electronic contact generally safe after June 15 post-sophomore year.
Basketball/Soccer: June 15 after sophomore year.
Current date: {current_date}. Always include a clear disclaimer in every message.
Never suggest violating NCAA rules.
"""

# ====================== AGENTS (Simplified for Demo Speed) ======================
researcher = Agent(
    role="Target & Fit Researcher",
    goal="Find 8-12 strong school/coach fits for the athlete",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False
)

contact_finder = Agent(
    role="Coach Contact Finder",
    goal="Find public coach emails or staff directory links",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False
)

personalizer = Agent(
    role="Message Personalizer",
    goal="Write personalized, professional outreach emails/DMs",
    backstory="You write concise, respectful recruiting emails that stand out to busy coaches.",
    llm=llm,
    verbose=False
)

compliance_guard = Agent(
    role="Compliance Guardian",
    goal="Review everything for NCAA compliance and suggest safe timing",
    backstory=compliance_backstory,
    llm=llm,
    verbose=False
)

# ====================== STREAMLIT UI ======================
st.title("🏈 RecruitAI – Athlete Outreach Demo")
st.markdown("**Football / Basketball / Soccer** – Generate personalized, compliant coach outreach in minutes.")

sport = st.selectbox("Sport", ["Football", "Basketball", "Soccer"])
position = st.text_input("Position (e.g. QB, SG, Striker)", "QB")
class_year = st.text_input("Class Year (e.g. 2027)", "2027")
gpa = st.text_input("GPA", "3.6")
location = st.text_input("Location / Preferred Targets (e.g. Texas D1)", "Texas")
stats = st.text_area("Key Stats + Highlights Link", "2,800 passing yards, 32 TDs, 68% completion. Highlights: hudl.com/profile/example")
other = st.text_area("Additional Notes (optional)", "Team captain, dual-threat elements")

athlete_input = f"{sport} | {position} | Class of {class_year} | GPA {gpa} | {location} | Stats: {stats} | {other}"

if st.button("🚀 Run Outreach Crew", type="primary"):
    if not athlete_input.strip():
        st.warning("Please fill in the athlete details.")
        st.stop
