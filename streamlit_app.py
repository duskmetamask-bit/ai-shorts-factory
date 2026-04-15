"""
AI Shorts Factory — Generate faceless YouTube Shorts scripts + images
"""

import streamlit as st
import openai
import os
import io
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEFAULT_MODEL  = "gpt-4o-mini"

# YouTube Shorts specs
SHORTS_MAX_SECS = 60
AVERAGE_WPM     = 150   # words per minute speaking pace

# ── Helpers ─────────────────────────────────────────────────────────────

def calc_watch_time(word_count: int) -> str:
    mins = word_count / AVERAGE_WPM
    secs = mins * 60
    if secs > SHORTS_MAX_SECS:
        return f">{SHORTS_MAX_SECS}s (trim needed)"
    return f"~{int(secs)}s"

def hook_score(hook: str) -> int:
    """0-100 heuristic based on hook qualities."""
    score = 40
    hook_lower = hook.lower()
    # Strong openers
    strong_openers = ["wait", "never", "here's", "if you", "the truth", "secret", "stop", "did you know", "this is why", "proof", "actually", "so i", "real talk", "bro ", "yo "]
    for opener in strong_openers:
        if opener in hook_lower[:40]:
            score += 15
            break
    # Numbers / lists appeal
    if any(c.isdigit() for c in hook[:20]):
        score += 10
    # Controversy / intrigue
    if any(w in hook_lower for w in ["believe", "wrong", "hate", "love", "best", "worst", "shocking"]):
        score += 10
    # Question engagement
    if hook.strip().endswith("?"):
        score += 10
    # All-caps / emphasis
    if hook[:1].isupper() and len(hook) > 5:
        score += 5
    return min(score, 100)

def viral_score(hook: str, cta: str) -> int:
    """0-100 viral potential score."""
    hs  = hook_score(hook)
    cta_lower = cta.lower()
    # Good CTA
    strong_ctas = ["follow", "save this", "share", "comment", "tag someone", "dm me", "link in bio", "book now", "try it", "start free"]
    cta_bonus = 10 if any(w in cta_lower for w in strong_ctas) else 0
    base = hs * 0.7 + cta_bonus
    # Controversy/intrigue multiplier
    if any(w in hook.lower() for w in ["secret", "truth", "never", "stop", "shocking"]):
        base += 10
    return min(int(base), 100)

def render_score_bar(score: int, label: str) -> None:
    color = "#FF0000" if score >= 75 else "#FFA500" if score >= 50 else "#888888"
    st.markdown(f"**{label}:** {score}/100")
    st.progress(score / 100, text=f"{score}%")

def build_script_prompt(topic: str, n: int) -> str:
    return (
        f"You are a viral YouTube Shorts scriptwriter. Write exactly 5 unique, faceless Shorts scripts "
        f"about: \"{topic}\"\n\n"
        f"For each script output this YAML block (no backticks, just plain text):\n\n"
        f"---\n"
        f"short_number: {n}\n"
        f"hook: <strong opening line that stops the scroll — keep under 10 words>\n"
        f"content: <body of the short — talking points + key insight — {SHORTS_MAX_SECS}s pace>\n"
        f"cta: <call to action — follow, save, share, comment, tag, link in bio>\n"
        f"thumbnail_prompt: <detailed image gen prompt for the thumbnail — vivid, high contrast, text overlay friendly>\n"
        f"---\n\n"
        f"Rules:\n"
        f"- Hook must be first line, no preamble\n"
        f"- Content must fit ~{SHORTS_MAX_SECS} seconds ({AVERAGE_WPM} WPM pace, ~{int(SHORTS_MAX_SECS/60*AVERAGE_WPM)} words max)\n"
        f"- Thumbnail prompt: describe a bold, high-contrast image a camera would take — include any text elements suggested\n"
        f"- 5 different angles / hooks, not just rewrites\n"
        f"- Output only the 5 YAML blocks, nothing else\n"
    )

def parse_scripts(raw: str) -> list:
    """Parse YAML-ish blocks from GPT response."""
    shorts = []
    current = {}
    in_block = False

    for line in raw.splitlines():
        line = line.rstrip()
        if line.strip() == "---":
            if in_block and current:
                shorts.append(current)
                current = {}
            in_block = True
            continue
        if not in_block:
            continue
        if ": " in line:
            key, _, val = line.partition(": ")
            key = key.strip().lower().replace(" ", "_")
            current[key] = val.strip()

    if current:
        shorts.append(current)

    # Ensure we have 5
    while len(shorts) < 5:
        shorts.append({"hook": "(missing)", "content": "(missing)", "cta": "(missing)", "thumbnail_prompt": "(missing)"})

    return shorts[:5]

def export_text(shorts: list, topic: str) -> str:
    buf = io.StringIO()
    buf.write(f"AI Shorts Factory — Export\n")
    buf.write(f"Topic: {topic}\n")
    buf.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n")
    buf.write("=" * 50 + "\n\n")
    for i, s in enumerate(shorts, 1):
        buf.write(f"[SHORT #{i}]\n")
        buf.write(f"HOOK:     {s.get('hook','')}\n")
        buf.write(f"CONTENT:  {s.get('content','')}\n")
        buf.write(f"CTA:      {s.get('cta','')}\n")
        buf.write(f"THUMBNAIL:{s.get('thumbnail_prompt','')}\n")
        wc = len(s.get('content','').split())
        buf.write(f"WATCH TIME: {calc_watch_time(wc)}\n")
        buf.write(f"VIRAL SCORE: {viral_score(s.get('hook',''), s.get('cta',''))}/100\n")
        buf.write("-" * 40 + "\n\n")
    return buf.getvalue()

# ── App ─────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Shorts Factory",
    page_icon="🎬",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, .stApp { background: #0F0F0F; color: #FFFFFF; font-family: 'Inter', sans-serif; }

.stTextInput > div > div > input {
    background: #1A1A1A; color: #FFFFFF; border: 1px solid #FF0000; font-size: 1.1rem;
    border-radius: 8px; padding: 0.6rem 1rem;
}

.stButton > button {
    background: #FF0000; color: #FFFFFF; font-weight: 700; border: none;
    border-radius: 8px; padding: 0.6rem 2rem; font-size: 1rem;
    transition: background 0.2s;
}
.stButton > button:hover { background: #CC0000; }

.short-card {
    background: #1A1A1A; border-left: 4px solid #FF0000;
    border-radius: 8px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem;
}

.short-number {
    background: #FF0000; color: #FFFFFF; font-weight: 900;
    display: inline-block; border-radius: 6px;
    padding: 0.15rem 0.7rem; font-size: 0.85rem; margin-bottom: 0.6rem;
}

section[data-testid="stSidebar"] { background: #161616; }

h1 { color: #FFFFFF; font-weight: 900; }
h2, h3 { color: #FFFFFF; }
.stMarkdown { color: #CCCCCC; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────
st.markdown("""
<p style="color:#FF0000;font-weight:900;font-size:1.4rem;letter-spacing:0.1em;">🎬 AI SHORTS FACTORY</p>
<h1 style="font-size:2.4rem;font-weight:900;">Turn Any Topic Into 5 Viral <span style="color:#FF0000;">YouTube Shorts</span></h1>
<p style="color:#AAAAAA;font-size:1.05rem;">AI-generated scripts with hooks, CTAs, thumbnail prompts & viral scores — ready to film or voice-over.</p>
<br/>
""", unsafe_allow_html=True)

# ── Sidebar: Pricing ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💰 Pricing")
    st.markdown("""
    | Tier | Price | Shorts |
    |------|-------|--------|
    | **Free** | $0 | 5 / day |
    | **Pro** | $19/mo | Unlimited |
    """)
    st.markdown("---")
    st.markdown("### ℹ️ How it works")
    st.markdown("""
    1. **Enter a topic** — keyword, niche, or viral trend
    2. **AI generates 5 scripts** — with hooks, content & CTAs
    3. **Each gets a thumbnail prompt** — feed into Midjourney / Ideogram
    4. **Check viral scores** — export the best ones
    5. **Film & post** — or use avatar tools like HeyGen
    """)
    st.markdown("---")
    st.markdown("*Free tier: 5 shorts/day  \nPro: unlimited for $19/mo*")

# ── Topic Input ──────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input(
        "🎯 Topic / Keyword",
        placeholder="e.g. crypto gains, fitness tips for men, AI tools 2026...",
        help="Enter the main theme for your Shorts",
    )
with col2:
    num_shorts = st.selectbox("Shorts", [5, 3, 1], index=0)

generate = st.button("🚀 Generate Shorts", use_container_width=True)

st.markdown("---")

# ── Generation ────────────────────────────────────────────────────────────
if generate:
    if not topic.strip():
        st.error("⚠️ Please enter a topic first.")
    elif not OPENAI_API_KEY:
        st.error("⚠️ OpenAI API key not set. Add it to your environment as OPENAI_API_KEY.")
    else:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        with st.spinner("🤖 AI is crafting your shorts..."):
            try:
                response = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[{"role": "user", "content": build_script_prompt(topic, num_shorts)}],
                    temperature=0.9,
                    max_tokens=2000,
                )
                raw = response.choices[0].message.content
                shorts = parse_scripts(raw)

                st.session_state["shorts"]   = shorts
                st.session_state["topic"]   = topic
                st.session_state["raw"]      = raw
                st.success(f"✅ Generated {len(shorts)} shorts for: *{topic}*")

            except Exception as e:
                st.error(f"❌ Error: {e}")

# ── Display Shorts ────────────────────────────────────────────────────────
if "shorts" in st.session_state:
    shorts = st.session_state["shorts"]
    topic  = st.session_state["topic"]

    st.markdown(f"## 📋 Results for: **{topic}**")

    cols = st.columns(1 if len(shorts) <= 2 else (2 if len(shorts) <= 4 else 3))
    cards_per_row = 2 if len(shorts) <= 4 else 3

    for i, short in enumerate(shorts):
        with st.container():
            wc   = len(short.get("content","").split())
            vs   = viral_score(short.get("hook",""), short.get("cta",""))
            wt   = calc_watch_time(wc)

            with st.container():
                st.markdown(f"""
                <div class="short-card">
                    <span class="short-number">SHORT #{i+1}</span>
                    &nbsp;&nbsp;<span style="color:#888;font-size:0.85rem;">⏱ {wt} &nbsp; 🔥 Viral: {vs}/100</span>
                    <br/><br/>
                    <p style="color:#FF4444;font-weight:700;font-size:1.05rem;">▶ HOOK</p>
                    <p style="color:#FFFFFF;font-size:1.05rem;">{short.get('hook','')}</p>
                    <p style="color:#FF4444;font-weight:700;font-size:1.05rem;">▶ CONTENT</p>
                    <p style="color:#DDDDDD;">{short.get('content','')}</p>
                    <p style="color:#FF4444;font-weight:700;font-size:1.05rem;">▶ CTA</p>
                    <p style="color:#AAAAAA;">{short.get('cta','')}</p>
                    <p style="color:#FF4444;font-weight:700;font-size:1.05rem;">▶ THUMBNAIL PROMPT</p>
                    <p style="color:#BBBBBB;font-size:0.92rem;background:#111;border-radius:6px;padding:0.6rem;">{short.get('thumbnail_prompt','')}</p>
                </div>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    render_score_bar(vs, "🔥 Viral Score")
                with c2:
                    render_score_bar(hook_score(short.get("hook","")), "⚡ Hook Strength")

                st.markdown("---")

    # Export
    st.markdown("### 📥 Export")
    export_data = export_text(shorts, topic)
    st.download_button(
        label="📄 Download All Shorts (.txt)",
        data=export_data,
        file_name=f"ai-shorts-{topic[:20].replace(' ','-')}.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ── Footer ───────────────────────────────────────────────────────────────
st.markdown("""
<br/>
<p style="text-align:center;color:#444;font-size:0.8rem;">
AI Shorts Factory · Free tier: 5 shorts/day · Pro: $19/mo · Built with OpenAI GPT-4o
</p>
""", unsafe_allow_html=True)
