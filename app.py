"""
app.py — AI Resume Analyzer · Streamlit Dashboard

Upload a PDF resume ➜ get an instant ATS score, skill gaps,
strengths, improvements, and interview readiness — all powered
by Google Gemini AI.
"""

import streamlit as st
from utils.pdf_reader import extract_text_from_pdf
from utils.gemini_service import analyze_resume

# ================================================================
# PAGE CONFIG — must be the very first Streamlit command
# ================================================================
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
# CUSTOM CSS — dark theme, glassmorphism, gradients, animations
# ================================================================
st.markdown("""
<style>
/* ---- Google Font ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ---- Global resets ---- */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ---- Hide default Streamlit branding ---- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---- Dark gradient background ---- */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%);
    color: #e0e0e0;
}

/* ---- Sidebar styling ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #0f0c29 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #a78bfa;
}

/* ---- Glassmorphism card ---- */
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(167, 139, 250, 0.12);
}

/* ---- Section headings inside cards ---- */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title .icon { font-size: 1.35rem; }

/* ---- Score ring ---- */
.score-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.score-ring {
    position: relative;
    width: 170px;
    height: 170px;
}
.score-ring svg {
    transform: rotate(-90deg);
}
.score-ring .bg {
    fill: none;
    stroke: rgba(255,255,255,0.06);
    stroke-width: 12;
}
.score-ring .progress {
    fill: none;
    stroke-width: 12;
    stroke-linecap: round;
    transition: stroke-dashoffset 1.2s ease;
}
.score-value {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.8rem;
    font-weight: 800;
}
.score-label {
    margin-top: 10px;
    font-size: 0.92rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    opacity: 0.7;
}

/* ---- Lists ---- */
.styled-list {
    list-style: none;
    padding: 0;
    margin: 0;
}
.styled-list li {
    padding: 10px 14px;
    margin-bottom: 8px;
    border-radius: 12px;
    background: rgba(255,255,255,0.03);
    border-left: 3px solid;
    font-size: 0.97rem;
    line-height: 1.55;
    transition: background 0.25s;
}
.styled-list li:hover {
    background: rgba(255,255,255,0.06);
}
.strength-item { border-color: #34d399; }
.missing-item  { border-color: #fbbf24; }
.improve-item  { border-color: #60a5fa; }

/* ---- Hero header ---- */
.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(135deg, #a78bfa, #6366f1, #818cf8, #c084fc);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 4s ease infinite;
    margin-bottom: 4px;
}
.hero-subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: rgba(255,255,255,0.5);
    font-weight: 400;
    margin-bottom: 36px;
}

@keyframes gradient-shift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ---- Analyze button ---- */
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #6366f1, #a78bfa);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px 0;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35);
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.5);
}
div.stButton > button:active {
    transform: translateY(0);
}

/* ---- Divider ---- */
.section-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167,139,250,0.3), transparent);
    margin: 32px 0;
}

/* ---- Fade-in animation for results ---- */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeInUp 0.6s ease forwards;
}
.fade-in-delay-1 { animation-delay: 0.15s; opacity: 0; }
.fade-in-delay-2 { animation-delay: 0.30s; opacity: 0; }
.fade-in-delay-3 { animation-delay: 0.45s; opacity: 0; }
.fade-in-delay-4 { animation-delay: 0.60s; opacity: 0; }

/* ---- Spinner override ---- */
.stSpinner > div {
    border-top-color: #a78bfa !important;
}
</style>
""", unsafe_allow_html=True)


# ================================================================
# HELPER — Render a circular score ring (SVG)
# ================================================================
def render_score_ring(score: int, label: str, color: str) -> str:
    """Return HTML for an animated circular score gauge."""
    radius = 70
    circumference = 2 * 3.14159 * radius
    offset = circumference - (score / 100) * circumference
    return f"""
    <div class="score-container">
        <div class="score-ring">
            <svg width="170" height="170" viewBox="0 0 170 170">
                <circle class="bg" cx="85" cy="85" r="{radius}"/>
                <circle class="progress" cx="85" cy="85" r="{radius}"
                    stroke="{color}"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"/>
            </svg>
            <div class="score-value" style="color:{color}">{score}</div>
        </div>
        <div class="score-label">{label}</div>
    </div>
    """


def score_color(score: int) -> str:
    """Return a color based on score thresholds."""
    if score >= 75:
        return "#34d399"   # green
    elif score >= 50:
        return "#fbbf24"   # yellow / amber
    else:
        return "#f87171"   # red


# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown("## 📄 Upload Resume")
    st.markdown(
        "<p style='color:rgba(255,255,255,0.5); font-size:0.88rem;'>"
        "Upload your resume as a PDF and let our AI analyze it instantly.</p>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Only PDF files are supported. Max size 200 MB.",
    )

    analyze_clicked = st.button("🚀 Analyze Resume", use_container_width=True)

    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.8rem; color:rgba(255,255,255,0.35);'>"
        "Powered by <b>Google Gemini AI</b><br>"
        "Built with ❤️ using Streamlit</p>",
        unsafe_allow_html=True,
    )


# ================================================================
# HERO HEADER
# ================================================================
st.markdown('<div class="hero-title">AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">'
    'Upload your resume · Get instant ATS feedback · Land more interviews'
    '</div>',
    unsafe_allow_html=True,
)

# ================================================================
# MAIN LOGIC
# ================================================================
if analyze_clicked:
    # ---- Validation ----
    if uploaded_file is None:
        st.warning("⚠️ Please upload a PDF resume first.")
        st.stop()

    # ---- Extract text ----
    with st.spinner("📖 Reading your resume…"):
        try:
            resume_text = extract_text_from_pdf(uploaded_file)
        except ValueError as ve:
            st.error(f"❌ {ve}")
            st.stop()
        except Exception as ex:
            st.error(f"❌ {ex}")
            st.stop()

    # ---- Analyze with Gemini ----
    with st.spinner("🤖 Analyzing with Gemini AI — this may take a few seconds…"):
        try:
            results = analyze_resume(resume_text)
        except EnvironmentError as ee:
            st.error(f"🔑 {ee}")
            st.stop()
        except Exception as ex:
            st.error(f"❌ Analysis failed: {ex}")
            st.stop()

    # ---- Store results in session state so they persist ----
    st.session_state["results"] = results

# ================================================================
# DISPLAY RESULTS (from session state)
# ================================================================
if "results" in st.session_state:
    results = st.session_state["results"]

    ats_score = int(results.get("ats_score", 0))
    interview_readiness = int(results.get("interview_readiness", 0))
    strengths = results.get("strengths", [])
    missing_skills = results.get("missing_skills", [])
    improvements = results.get("improvements", [])

    # ---- Divider ----
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ==============================================================
    # ROW 1 — Score Rings
    # ==============================================================
    col1, col2 = st.columns(2)

    with col1:
        ats_color = score_color(ats_score)
        st.markdown(
            f'<div class="glass-card fade-in" style="text-align:center;">'
            f'<div class="section-title" style="justify-content:center;">'
            f'<span class="icon">🎯</span> ATS Score</div>'
            f'{render_score_ring(ats_score, "ATS Compatibility", ats_color)}'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col2:
        ir_color = score_color(interview_readiness)
        st.markdown(
            f'<div class="glass-card fade-in fade-in-delay-1" style="text-align:center;">'
            f'<div class="section-title" style="justify-content:center;">'
            f'<span class="icon">🎤</span> Interview Readiness</div>'
            f'{render_score_ring(interview_readiness, "Interview Preparedness", ir_color)}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ==============================================================
    # ROW 2 — Strengths & Missing Skills
    # ==============================================================
    col3, col4 = st.columns(2)

    with col3:
        strength_items = "".join(
            f'<li class="strength-item">✅&ensp;{s}</li>' for s in strengths
        )
        st.markdown(
            f'<div class="glass-card fade-in fade-in-delay-2">'
            f'<div class="section-title">'
            f'<span class="icon">💪</span> Strengths</div>'
            f'<ul class="styled-list">{strength_items}</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col4:
        missing_items = "".join(
            f'<li class="missing-item">⚠️&ensp;{s}</li>' for s in missing_skills
        )
        st.markdown(
            f'<div class="glass-card fade-in fade-in-delay-3">'
            f'<div class="section-title">'
            f'<span class="icon">🔍</span> Missing Skills</div>'
            f'<ul class="styled-list">{missing_items}</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ==============================================================
    # ROW 3 — Improvements (full width)
    # ==============================================================
    improvement_items = "".join(
        f'<li class="improve-item">'
        f'<strong style="color:#60a5fa;">#{i+1}</strong>&ensp;{imp}</li>'
        for i, imp in enumerate(improvements)
    )
    st.markdown(
        f'<div class="glass-card fade-in fade-in-delay-4">'
        f'<div class="section-title">'
        f'<span class="icon">🚀</span> Actionable Improvements</div>'
        f'<ul class="styled-list">{improvement_items}</ul>'
        f'</div>',
        unsafe_allow_html=True,
    )

else:
    # ---- Empty state ----
    st.markdown(
        '<div style="text-align:center; margin-top:80px; opacity:0.4;">'
        '<p style="font-size:4rem; margin-bottom:8px;">📄</p>'
        '<p style="font-size:1.15rem; font-weight:500;">'
        'Upload a resume PDF in the sidebar and click <b>Analyze Resume</b> to get started.'
        '</p></div>',
        unsafe_allow_html=True,
    )
