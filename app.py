import html
import json
import os

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

st.set_page_config(page_title="AI Career Copilot", layout="wide")

PROVIDERS = {
    "Google Gemini (free)": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.5-flash",
        "env": "GEMINI_API_KEY",
    },
    "Groq (free)": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "env": "GROQ_API_KEY",
    },
    "OpenAI (paid)": {
        "base_url": None,
        "model": "gpt-4o-mini",
        "env": "OPENAI_API_KEY",
    },
}

st.markdown(
    """
<style>
    .hero {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 2rem 2.2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }
    .hero h1 { margin: 0; font-size: 2.1rem; color: white; }
    .hero p { margin: .4rem 0 0 0; opacity: .9; font-size: 1.05rem; color: white; }

    .card {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, .08);
        border-top: 5px solid #4F46E5;
        margin-bottom: .8rem;
    }
    .card .label { color: #6B7280; font-size: .85rem; text-transform: uppercase; letter-spacing: .05em; }
    .card .value { color: #111827; font-size: 2rem; font-weight: 700; line-height: 1.2; }
    .green { border-top-color: #10B981; }
    .red { border-top-color: #EF4444; }
    .amber { border-top-color: #F59E0B; }

    .chip {
        display: inline-block;
        padding: .3rem .75rem;
        margin: .2rem .25rem .2rem 0;
        border-radius: 999px;
        font-size: .85rem;
        font-weight: 500;
    }
    .chip-good { background: #D1FAE5; color: #065F46; }
    .chip-bad { background: #FEE2E2; color: #991B1B; }

    .feedback {
        background: #F5F3FF;
        color: #1F2937;
        border-left: 5px solid #7C3AED;
        padding: .9rem 1.1rem;
        border-radius: 10px;
        margin: .5rem 0 1.2rem 0;
    }

    .stButton > button {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        border: none;
        border-radius: 10px;
        padding: .6rem 1.4rem;
        font-weight: 600;
    }
    .stButton > button:hover { color: white; opacity: .92; }

    @media (max-width: 640px) {
        .hero { padding: 1.3rem 1.2rem; }
        .hero h1 { font-size: 1.5rem; }
        .card .value { font-size: 1.6rem; }
    }
</style>
""",
    unsafe_allow_html=True,
)


def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        return json.loads(text[start : end + 1])


def ask_json(prompt):
    client = OpenAI(api_key=api_key, base_url=provider["base_url"])
    messages = [
        {"role": "system", "content": "You are an expert recruiter and career coach. Reply with valid JSON only."},
        {"role": "user", "content": prompt},
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
        )
    except Exception:
        # some providers or models reject json mode, so try once more without it
        response = client.chat.completions.create(model=model, messages=messages, temperature=0.3)
    return parse_json(response.choices[0].message.content)


def metric_card(label, value, color=""):
    st.markdown(
        f'<div class="card {color}"><div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(str(value))}</div></div>',
        unsafe_allow_html=True,
    )


def chips(items, style):
    if not items:
        return "<em>None</em>"
    return "".join(f'<span class="chip {style}">{html.escape(str(i))}</span>' for i in items)


with st.sidebar:
    st.header("Settings")
    provider_name = st.selectbox("AI provider", list(PROVIDERS.keys()))
    provider = PROVIDERS[provider_name]
    api_key = st.text_input(
        "API key",
        type="password",
        value=os.getenv(provider["env"], ""),
        key=f"key_{provider_name}",
        help=f"You can also set {provider['env']} as an environment variable or Codespaces secret.",
    )
    model = st.text_input("Model", value=provider["model"], key=f"model_{provider_name}")
    st.caption("Your resume text is sent to the selected provider for analysis.")

for key in ("analysis", "questions", "results"):
    if key not in st.session_state:
        st.session_state[key] = None

st.markdown(
    '<div class="hero"><h1>AI Career Copilot</h1>'
    "<p>Match your resume to any job, spot skill gaps, and practise interviews with instant AI feedback.</p></div>",
    unsafe_allow_html=True,
)

left, right = st.columns(2)
with left:
    st.subheader("Your resume")
    resume_file = st.file_uploader("Upload a PDF", type=["pdf"])
with right:
    st.subheader("Job description")
    job_text = st.text_area(
        "Paste the job description",
        height=180,
        label_visibility="collapsed",
        placeholder="Paste the full job description here...",
    )

if st.button("Analyse match"):
    if not api_key:
        st.error("Add your API key in the sidebar first.")
    elif not resume_file or not job_text.strip():
        st.error("Upload a resume and paste a job description.")
    else:
        resume_text = extract_pdf_text(resume_file)
        if len(resume_text) < 50:
            st.error("Could not read text from this PDF. It may be a scanned image, so try a text-based PDF.")
        else:
            with st.spinner("Comparing your resume with the job..."):
                try:
                    st.session_state.analysis = ask_json(
                        f"""Compare this resume with this job description.
Return JSON with exactly these keys:
- "match_percent": integer 0-100
- "matched_skills": list of skills the resume has that the job wants
- "missing_skills": list of skills the job wants that the resume lacks
- "summary": 2-3 sentence honest assessment

RESUME:
{resume_text[:6000]}

JOB DESCRIPTION:
{job_text[:6000]}"""
                    )
                    st.session_state.questions = None
                    st.session_state.results = None
                    st.session_state.resume_text = resume_text
                    st.session_state.job_text = job_text
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

analysis = st.session_state.analysis
if analysis:
    results = st.session_state.results
    avg_score = "N/A"
    if results:
        scores = [float(r.get("score", 0)) for r in results]
        avg_score = f"{sum(scores) / len(scores):.1f}/10"

    percent = int(analysis.get("match_percent", 0))
    match_color = "green" if percent >= 70 else "amber" if percent >= 40 else "red"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Job match", f"{percent}%", match_color)
    with c2:
        metric_card("Skills matched", len(analysis.get("matched_skills", [])), "green")
    with c3:
        metric_card("Skills missing", len(analysis.get("missing_skills", [])), "red")
    with c4:
        metric_card("Interview score", avg_score, "amber")

    st.progress(min(max(percent, 0), 100) / 100)

    tab1, tab2 = st.tabs(["Match report", "Interview practice"])

    with tab1:
        st.info(analysis.get("summary", ""))
        a, b = st.columns(2)
        with a:
            st.subheader("Skills you have")
            st.markdown(chips(analysis.get("matched_skills"), "chip-good"), unsafe_allow_html=True)
        with b:
            st.subheader("Missing skills")
            st.markdown(chips(analysis.get("missing_skills"), "chip-bad"), unsafe_allow_html=True)

    with tab2:
        if st.button("Generate interview questions"):
            with st.spinner("Writing questions..."):
                try:
                    data = ask_json(
                        f"""Write 5 interview questions for this candidate and job, mixing technical
and behavioural. Return JSON: {{"questions": ["question 1", "question 2"]}}

RESUME:
{st.session_state.resume_text[:4000]}

JOB DESCRIPTION:
{st.session_state.job_text[:4000]}"""
                    )
                    st.session_state.questions = data.get("questions", [])[:5]
                    st.session_state.results = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

        questions = st.session_state.questions
        if questions:
            answers = []
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i + 1}. {q}**")
                answers.append(
                    st.text_area("Your answer", key=f"answer_{i}", height=110, label_visibility="collapsed")
                )

            if st.button("Score my answers"):
                if not any(a.strip() for a in answers):
                    st.error("Write at least one answer first.")
                else:
                    qa = "\n\n".join(
                        f"Q{i + 1}: {q}\nAnswer: {a.strip() or '(no answer given)'}"
                        for i, (q, a) in enumerate(zip(questions, answers))
                    )
                    with st.spinner("Scoring..."):
                        try:
                            data = ask_json(
                                f"""Score each interview answer from 0 to 10 and give short, constructive,
specific feedback. Unanswered questions score 0. Return JSON:
{{"results": [{{"score": 7, "feedback": "..."}}]}} with one item per question, in order.

{qa}"""
                            )
                            st.session_state.results = data.get("results", [])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Something went wrong: {e}")

            if st.session_state.results:
                st.markdown("---")
                st.subheader("Your feedback")
                for i, r in enumerate(st.session_state.results[: len(questions)]):
                    st.markdown(f"**Q{i + 1}: {questions[i]}**")
                    st.markdown(
                        f'<div class="feedback"><b>Score: {r.get("score", 0)}/10</b><br>'
                        f'{html.escape(str(r.get("feedback", "")))}</div>',
                        unsafe_allow_html=True,
                    )
else:
    st.caption("Upload a resume, paste a job description, and click Analyse match to begin.")
