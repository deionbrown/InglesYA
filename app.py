
import json, hashlib, tempfile, asyncio
from pathlib import Path
import streamlit as st
import edge_tts

BASE=Path(__file__).resolve().parent
ASSETS=BASE/"assets"
LOGO=ASSETS/"ingles_ya_logo.jpg"

st.set_page_config(
    page_title="Inglés ¡YA! · English A1 Teacher Studio",
    page_icon=str(LOGO),
    layout="wide",
    initial_sidebar_state="expanded",
)
DATA=json.loads((BASE/"lesson_data.json").read_text(encoding="utf-8"))
UNITS=DATA["units"]; SLIDES=DATA["slides"]

if "slide" not in st.session_state: st.session_state.slide=0
if "theme" not in st.session_state: st.session_state.theme="Light"

LIGHT={"bg":"#EEF2F7","surface":"#FFFFFF","alt":"#F7F9FC","text":"#172033","muted":"#667085","border":"#D0D7E2","accent":"#7058FF","green":"#58CC02","blue":"#1CB0F6"}
DARK={"bg":"#0F172A","surface":"#172033","alt":"#1E293B","text":"#F8FAFC","muted":"#9FB0C7","border":"#2C3A4F","accent":"#7C63FF","green":"#58CC02","blue":"#1CB0F6"}
C=DARK if st.session_state.theme=="Dark" else LIGHT

shadow = "0 8px 24px rgba(20, 31, 50, 0.08)" if st.session_state.theme=="Light" else "none"
inner_shadow = "0 3px 12px rgba(20, 31, 50, 0.06)" if st.session_state.theme=="Light" else "none"

st.markdown(f"""
<style>
.stApp{{
    background:{C['bg']};
    color:{C['text']};
}}

.block-container{{
    max-width:1250px;
    padding-top:1.5rem;
    padding-bottom:3rem;
}}

[data-testid="stSidebar"]{{
    background:{C['surface']};
    border-right:1px solid {C['border']};
    box-shadow: 2px 0 12px rgba(20,31,50,0.04);
}}
[data-testid="stSidebar"] *{{
    color:{C['text']};
}}

/* Streamlit top header / toolbar */
[data-testid="stHeader"]{{
    background:{C['surface']} !important;
    border-bottom:1px solid {C['border']} !important;
}}
[data-testid="stHeader"]::before{{
    background:{C['surface']} !important;
}}
[data-testid="stToolbar"]{{
    background:transparent !important;
}}
[data-testid="stDecoration"]{{
    background:{C['accent']} !important;
}}
header[data-testid="stHeader"]{{
    box-shadow:none !important;
}}

.hero{{
    background:{C['surface']};
    border:1px solid {C['border']};
    border-radius:24px;
    padding:24px;
    margin-bottom:18px;
    box-shadow:{shadow};
}}

.lesson-card{{
    background:{C['surface']};
    border:1px solid {C['border']};
    border-radius:24px;
    padding:24px;
    margin-bottom:18px;
    box-shadow:{shadow};
}}

.hero h1{{
    color:{C['text']};
    margin:0;
}}

.hero p{{
    color:{C['muted']};
}}

.title{{
    font-size:1.35rem;
    font-weight:800;
    color:{C['accent']};
    margin-bottom:14px;
}}

.big{{
    font-size:2.4rem;
    font-weight:900;
    text-align:center;
    color:{C['text']};
}}

.ipa{{
    text-align:center;
    color:{C['muted']};
    font-size:1.1rem;
    margin-bottom:10px;
}}

.row{{
    background:{C['alt']};
    border:1px solid {C['border']};
    border-radius:14px;
    padding:12px 14px;
    margin:8px 0;
    box-shadow:{inner_shadow};
}}

.tip{{
    background:{C['alt']};
    border:1px solid {C['border']};
    border-radius:14px;
    padding:14px 16px;
    color:{C['muted']};
    margin-top:14px;
    box-shadow:{inner_shadow};
}}

.progress{{
    background:{C['alt']};
    border:1px solid {C['border']};
    height:10px;
    border-radius:999px;
    overflow:hidden;
}}

.fill{{
    background:{C['accent']};
    height:100%;
    border-radius:999px;
}}

div.stButton>button{{
    width:100%;
    border-radius:14px;
    min-height:44px;
    font-weight:700;
    border:1px solid {C['border']};
    box-shadow:{inner_shadow};
}}

[data-testid="stImage"] img{{
    border-radius:18px;
    border:1px solid {C['border']};
    box-shadow:{inner_shadow};
}}

/* Keep top-right controls readable in both themes */
[data-testid="stHeader"] button,
[data-testid="stHeader"] svg{{
    color:{C['text']} !important;
    fill:{C['text']} !important;
}}

/* Sidebar brand card */
.brand-wrap{{
    background:{C['surface']};
    border:1px solid {C['border']};
    border-radius:18px;
    padding:12px;
    margin-bottom:12px;
    box-shadow:{inner_shadow};
}}
.brand-name{{
    font-size:1.05rem;
    font-weight:800;
    color:{C['text']};
    margin-top:6px;
}}
.brand-sub{{
    font-size:.78rem;
    color:{C['muted']};
}}
</style>
""",unsafe_allow_html=True)

async def _tts(text,path):
    await edge_tts.Communicate(text=text,voice="en-US-JennyNeural",rate="-3%").save(path)

@st.cache_data(show_spinner=False)
def make_audio(text):
    key=hashlib.sha1(text.encode()).hexdigest()
    d=Path(tempfile.gettempdir())/"a1_teacher_audio"; d.mkdir(exist_ok=True)
    p=d/f"{key}.mp3"
    if not p.exists(): asyncio.run(_tts(text,str(p)))
    return p.read_bytes()

def play(text,key,label="🔊 Listen"):
    if st.button(label,key=key):
        try: st.audio(make_audio(text),format="audio/mp3",autoplay=True)
        except Exception: st.warning("Audio unavailable right now.")

st.sidebar.image(str(LOGO), use_container_width=True)
st.sidebar.markdown(
    f"""
    <div class="brand-wrap">
      <div class="brand-name">Inglés ¡YA!</div>
      <div class="brand-sub">English A1 Teacher Studio · Web Edition v3</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("### Appearance")
theme=st.sidebar.radio("Theme",["Light","Dark"],horizontal=True,label_visibility="collapsed",index=0 if st.session_state.theme=="Light" else 1)
if theme!=st.session_state.theme:
    st.session_state.theme=theme; st.rerun()

st.sidebar.markdown("### Units")
for i,u in enumerate(UNITS,1):
    if i==1:
        if st.sidebar.button(f"Unit {i} · {u}",type="primary",key=f"u{i}"):
            st.session_state.slide=0; st.rerun()
    else:
        st.sidebar.button(f"Unit {i} · {u}",disabled=True,key=f"u{i}")

idx=st.session_state.slide
s=SLIDES[idx]
pct=(idx+1)/len(SLIDES)*100

st.markdown(f"""<div class="hero"><h1>Unit 1 · Introductions</h1><p>Lesson 1 · Hello! My name is…</p>
<div style="display:flex;justify-content:space-between;color:{C['muted']};margin-top:14px"><span>{s['title']}</span><span>{idx+1}/{len(SLIDES)}</span></div>
<div class="progress" style="margin-top:8px"><div class="fill" style="width:{pct:.1f}%"></div></div></div>""",unsafe_allow_html=True)

st.markdown('<div class="lesson-card">',unsafe_allow_html=True)
st.markdown(f'<div class="title">{s["title"]}</div>',unsafe_allow_html=True)

img=ASSETS/s["image"]
if img.exists(): st.image(str(img),use_container_width=True)

t=s["type"]
if t=="warmup":
    st.markdown(f'<div class="big">{s["headline"]}</div><div class="ipa">{s["ipa"]}</div>',unsafe_allow_html=True)
    play(s["headline"],"warm")
    st.markdown(f'<div class="tip">💡 <b>Teacher note:</b> {s["note"]}</div>',unsafe_allow_html=True)

elif t=="vocab":
    for i,(w,ipa,es) in enumerate(s["items"]):
        a,b=st.columns([5,1])
        with a: st.markdown(f'<div class="row"><b>{w}</b> &nbsp; <span style="color:{C["muted"]}">{ipa}</span><br><span style="color:{C["muted"]}">{es}</span></div>',unsafe_allow_html=True)
        with b: play(w,f"v{i}")

elif t=="sentences":
    for i,(en,es) in enumerate(s["items"]):
        a,b=st.columns([5,1])
        with a: st.markdown(f'<div class="row"><b>{en}</b><br><span style="color:{C["muted"]}">{es}</span></div>',unsafe_allow_html=True)
        with b: play(en,f"s{i}")

elif t=="dialogue":
    full=[]
    for i,(who,line) in enumerate(s["lines"]):
        full.append(line)
        a,b=st.columns([5,1])
        with a: st.markdown(f'<div class="row"><b style="color:{C["accent"]}">{who}:</b> {line}</div>',unsafe_allow_html=True)
        with b: play(line,f"d{i}")
    play(" ".join(full),"dfull","▶ Play full dialogue")

elif t=="listening":
    play(s["audio"],"listen","▶ Play listening")
    st.subheader(s["question"])
    ch=st.radio("Choose one:",s["options"],key="lc")
    if st.button("Check answer",key="lcheck"):
        st.success("Correct! ✓") if ch==s["answer"] else st.error(f"Correct answer: {s['answer']}")

elif t=="speaking":
    st.markdown("### Speaking time")
    for i,q in enumerate(s["questions"],1): st.markdown(f"**{i}. {q}**")

elif t=="quiz":
    st.subheader(s["question"])
    ch=st.radio("Choose one:",s["options"],key="qc")
    if st.button("Check answer",key="qcheck"):
        st.success("Great job! ✓") if ch==s["answer"] else st.error(f"Best answer: {s['answer']}")

elif t=="review":
    st.markdown("## 🎉 You did it!")
    for item in s["items"]: st.markdown(f"✅ **{item}**")

st.markdown("</div>",unsafe_allow_html=True)

c1,c2,c3=st.columns([1,2,1])
with c1:
    if st.button("← Previous",disabled=idx==0):
        st.session_state.slide-=1; st.rerun()
with c3:
    if idx<len(SLIDES)-1:
        if st.button("Next →",type="primary"):
            st.session_state.slide+=1; st.rerun()
    else:
        if st.button("Finish lesson ✓",type="primary"):
            st.success("Unit 1 completed!"); st.balloons()
