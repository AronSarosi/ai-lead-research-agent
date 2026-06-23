"""Visual theme matched to the /warm contract-generator app (localhost:3030).

Same design language as aiwitharon: warm sand base, terracotta accent, Newsreader
serif headings + Inter body. This variant is flatter and centred - a centred
hero with an italic terracotta accent phrase, soft cream cards, and a quiet
footer. Base colours live in .streamlit/config.toml; this
module layers on fonts, the hero, cards, and the footer.
"""

from __future__ import annotations

import streamlit as st

# Palette, lifted straight from the contract-generator's globals.css tokens.
BASE = "#F2ECE3"        # warm sand / page
SURFACE = "#FBF8F2"     # soft card surface
WHITE = "#FFFFFF"       # inputs
INK = "#221E19"         # headings
INK_DIM = "#5B544B"     # body
INK_MUTE = "#8A8175"    # muted captions / footer
LINE = "#E0D8CB"        # hairline
ACCENT = "#B5532E"      # terracotta
ACCENT_DEEP = "#99431F"  # terracotta hover

CARD_SHADOW = "0 1px 2px rgba(34,30,25,0.03), 0 18px 44px -34px rgba(34,30,25,0.22)"


_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Inter:wght@400;500;600&display=swap');

/* Shared modular type scale (Perfect Fourth ~1.333), used across all 4 tools. */
:root {{
  --h1: clamp(2.5rem, 5vw, 3.75rem);
  --h2: 1.5rem;
  --subhead: 1.15rem;
  --body: 1.02rem;
  --eyebrow: 0.8rem;
  --caption: 0.85rem;
}}

/* Flat warm-sand page, Inter body, warm-grey text. */
.stApp {{
  background-color: {BASE};
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: {INK_DIM};
}}
[data-testid="stHeader"] {{ background: transparent; }}

/* Airy, centred column - wide enough to use the desktop and fit the demo on one row. */
.block-container {{
  max-width: 1360px;
  padding-top: 1.4rem;
  padding-bottom: 3rem;
}}

/* Headings: Newsreader serif, warm charcoal. */
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
  font-family: 'Newsreader', Georgia, 'Times New Roman', serif;
  color: {INK};
  letter-spacing: -0.01em;
}}

/* Body + captions. */
.stApp p, .stApp li {{ color: {INK_DIM}; font-size: var(--body); }}
.stApp label, .stApp label p {{ color: {INK} !important; font-weight: 500; }}
.stApp [data-testid="stCaptionContainer"], .stApp small {{ color: {INK_MUTE} !important; }}

/* Inputs: white fields, hairline border, terracotta focus ring. */
.stTextInput input, .stTextArea textarea, .stNumberInput input {{
  background-color: {WHITE};
  border: 1px solid {LINE} !important;
  border-radius: 10px !important;
  color: {INK};
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
  border-color: {ACCENT} !important;
  box-shadow: 0 0 0 3px rgba(181,83,46,0.16) !important;
}}

/* Buttons. */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {{
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  border-radius: 10px;
  border: 1px solid {LINE};
  padding: 0.7rem 1.7rem;
  transition: transform .2s ease, border-color .2s ease, color .2s ease, background .2s ease, box-shadow .3s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  border-color: {ACCENT};
  color: {ACCENT};
}}

/* Primary / form-submit: solid terracotta. */
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primaryFormSubmit"] {{
  background: {ACCENT} !important;
  border: none !important;
  color: {WHITE} !important;
  box-shadow: 0 10px 26px -10px rgba(181,83,46,0.75);
}}
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primaryFormSubmit"]:hover {{
  background: {ACCENT_DEEP} !important;
  color: {WHITE} !important;
  transform: translateY(-2px);
  box-shadow: 0 16px 34px -10px rgba(181,83,46,0.85);
}}

/* The form rendered as a soft cream card. */
[data-testid="stForm"] {{
  background: {SURFACE};
  border: 1px solid {LINE};
  border-radius: 18px;
  padding: 2rem 2rem 1rem;
  box-shadow: {CARD_SHADOW};
}}

/* Data editor: round corners, warm hairline. */
[data-testid="stDataFrame"], [data-testid="stDataFrameResizable"] {{
  border-radius: 12px;
  border: 1px solid {LINE};
}}

[data-testid="stAlert"] {{ border-radius: 12px; }}
.stApp hr {{ border-color: {LINE}; }}

/* --- Custom bits -------------------------------------------------------- */

/* Centred hero (shared formula). Wide enough that the H1 stays on one line. */
.hero {{ text-align: center; margin: 0.6rem auto 1.6rem; max-width: 980px; }}
.hero .kicker {{
  font-size: var(--eyebrow);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: {ACCENT};
}}
.hero h1 {{
  font-family: 'Newsreader', Georgia, serif;
  font-weight: 500;
  font-size: var(--h1);
  line-height: 1.07;
  letter-spacing: -0.02em;
  color: {INK};
  margin: 0.7rem 0 0;
  white-space: nowrap;
}}
.hero h1 .accent {{ color: {ACCENT}; font-style: italic; }}
.hero p {{
  color: {INK_DIM};
  font-size: var(--subhead);
  line-height: 1.6;
  max-width: 620px;
  margin: 1.1rem auto 0;
}}
.hero p b {{ color: {ACCENT_DEEP}; font-weight: 600; }}

/* Trust chips (the missing credibility cue). */
.trust {{
  display: flex; flex-wrap: wrap; justify-content: center;
  gap: 0.6rem; margin: 1.3rem auto 0; max-width: 760px;
}}
.trust .chip {{
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: {WHITE}; border: 1px solid {LINE};
  border-radius: 999px; padding: 0.4rem 0.9rem;
  font-size: var(--caption); color: {INK_DIM}; font-weight: 500;
}}
.trust .chip::before {{
  content: ""; width: 7px; height: 7px; border-radius: 50%;
  background: {ACCENT}; flex: none;
}}

/* Demonstration: ideal client -> arrow + prompt -> drafted outreach.
   Fixed-width blocks + one uniform gap == identical space on BOTH sides. */
/* Three columns + arrow on ONE row at desktop width. Widths + gaps are sized so
   the strip never exceeds the content area (it falls back to wrapping below ~900px). */
.demo {{display:flex; align-items:center; justify-content:center; gap:2.2rem; flex-wrap:wrap; margin:2.2rem auto 0.5rem;}}
.demo-col {{flex:0 0 auto; width:320px; display:flex; flex-direction:column; align-items:center; text-align:center;}}
.demo-cap {{letter-spacing:.08em; font-size:.9rem; color:{INK_MUTE}; font-weight:700; margin-bottom:.55rem;}}
.demo-mid {{display:flex; flex-direction:column; align-items:center; gap:.7rem; flex:0 0 auto; width:200px;}}
.demo-prompt {{background:{SURFACE}; border:1px solid {LINE}; border-radius:11px; padding:.6rem .8rem; font-size:.92rem; color:{INK_DIM}; text-align:left; line-height:1.42;}}
.straight-arrow {{line-height:0;}}

/* Left card: the ideal client profile. */
.icpcard {{width:300px; margin:0 auto; background:{WHITE}; border:1px solid {LINE}; border-radius:9px; box-shadow:0 10px 26px rgba(34,30,25,.18); padding:.7rem .8rem; text-align:left;}}
.icp-tag {{display:inline-block; font-size:.78rem; font-weight:700; color:{WHITE}; background:{ACCENT}; border-radius:3px; padding:.06rem .45rem; margin-bottom:.55rem; letter-spacing:.04em;}}
.icp-row {{display:flex; justify-content:space-between; gap:.6rem; font-size:.9rem; padding:.28rem 0; border-bottom:1px solid {LINE}; line-height:1.3;}}
.icp-row:last-child {{border-bottom:none;}}
.icp-row .k {{color:{INK_MUTE}; font-weight:600;}}
.icp-row .v {{color:{INK}; text-align:right;}}

/* Right card: the drafted outreach message. */
.msg-thumb {{width:300px; margin:0 auto; background:{WHITE}; border:1px solid {LINE}; border-radius:9px; box-shadow:0 10px 26px rgba(34,30,25,.18); padding:.7rem .8rem; text-align:left;}}
.msg-to {{font-size:.84rem; color:{INK_MUTE}; line-height:1.4; margin-bottom:.1rem;}}
.msg-to b {{color:{INK};}}
.msg-subj {{font-family:'Newsreader',Georgia,serif; color:{INK}; font-weight:600; font-size:1.02rem; line-height:1.22; margin:.35rem 0 .55rem 0;}}
.msg-body {{font-size:.9rem; color:{INK_DIM}; line-height:1.5;}}
.msg-body b {{color:{ACCENT_DEEP};}}
.msg-sign {{margin-top:.55rem; font-size:.9rem; color:{INK}; font-weight:600;}}

/* Two-step progress stepper: pills "1 Describe" / "2 Review". */
.stepper {{
  display: flex; align-items: center; gap: 0.6rem;
  margin: 1.8rem 0 0.6rem;
}}
.stepper .pill {{
  display: inline-flex; align-items: center; gap: 0.5rem;
  border-radius: 999px; padding: 0.4rem 0.95rem;
  font-size: 0.92rem; font-weight: 600;
  border: 1px solid {LINE}; background: {WHITE}; color: {INK_MUTE};
}}
.stepper .pill .num {{
  display: inline-flex; align-items: center; justify-content: center;
  width: 1.35rem; height: 1.35rem; border-radius: 50%;
  background: {BASE}; color: {INK_MUTE}; font-size: 0.82rem; font-weight: 700;
}}
.stepper .pill.active {{
  background: {ACCENT}; border-color: {ACCENT}; color: {WHITE};
}}
.stepper .pill.active .num {{ background: rgba(255,255,255,0.22); color: {WHITE}; }}
.stepper .track {{ width: 1.8rem; height: 2px; background: {LINE}; border-radius: 2px; flex: none; }}
.stepper .count {{
  margin-left: 0.45rem; font-size: 0.8rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em; color: {ACCENT};
}}

/* Numbered step heading above a card section. */
.step {{
  font-family: 'Newsreader', Georgia, serif;
  font-size: var(--h2);
  font-weight: 600;
  color: {INK};
  margin: 0 0 0.25rem;
}}
.step-sub {{
  color: {INK_DIM};
  font-size: 0.95rem;
  margin: 0 0 0.9rem;
}}

/* Light grouping sub-label inside the form, e.g. "WHO YOU TARGET". */
.form-group {{
  font-size: 0.78rem; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: {ACCENT};
  margin: 0.2rem 0 0.2rem;
}}
.form-group .gnote {{
  color: {INK_MUTE}; font-weight: 600; letter-spacing: 0.02em;
  text-transform: none; font-size: 0.82rem; margin-left: 0.5rem;
}}

/* Quiet footer, like "Built by Aron Sarosi". */
.footer {{
  border-top: 1px solid {LINE};
  margin-top: 3rem;
  padding-top: 1.4rem;
}}
.footer .discl {{
  color: {INK_MUTE};
  font-style: italic;
  font-size: 0.86rem;
  line-height: 1.55;
  max-width: 760px;
}}
.footer .built {{
  color: {INK_MUTE};
  font-size: 0.86rem;
  margin-top: 0.6rem;
}}
</style>
"""


def inject_theme() -> None:
    """Inject the fonts and styling. Call once, right after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_header() -> None:
    """Hero: eyebrow tool name, value-prop H1, one-line subhead, trust chips."""
    st.markdown(
        """
        <div class="hero">
          <div class="kicker">AI Lead Research Agent</div>
          <h1>Describe your client. <span class="accent">Get the outreach.</span></h1>
          <p>Give it your ideal client and the offer you're pitching. The agent finds
          matching companies, researches each one, and drafts a personal message in your
          voice. You review and edit every draft - <b>it never sends anything.</b></p>
        </div>
        <div class="trust">
          <span class="chip">Researched, not generic</span>
          <span class="chip">You review every draft</span>
          <span class="chip">Never sends on its own</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# One clean, straight arrow pointing input -> output. Nothing overlaps it.
_STRAIGHT_ARROW = (
    '<svg class="straight-arrow" width="150" height="30" viewBox="0 0 150 30" '
    'fill="none" stroke="#B5532E" stroke-width="5" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M6 15 L132 15"/>'
    '<path d="M132 15 L116 6"/><path d="M132 15 L116 24"/></svg>'
)


def render_demo() -> None:
    """A framed preview of the real result: ideal client -> prompt -> drafted outreach."""
    st.markdown(
        f"""
        <div class="demo">
          <div class="demo-col">
            <div class="demo-cap">YOUR IDEAL CLIENT</div>
            <div class="icpcard">
              <span class="icp-tag">ICP</span>
              <div class="icp-row"><span class="k">Industry</span><span class="v">Recruitment</span></div>
              <div class="icp-row"><span class="k">Size</span><span class="v">10 to 50</span></div>
              <div class="icp-row"><span class="k">Location</span><span class="v">London</span></div>
              <div class="icp-row"><span class="k">Offer</span><span class="v">AI automation that saves admin hours</span></div>
            </div>
          </div>
          <div class="demo-mid">
            <div class="demo-prompt">&ldquo;Find clients like this and write the first message.&rdquo;</div>
            {_STRAIGHT_ARROW}
          </div>
          <div class="demo-col">
            <div class="demo-cap">DRAFTED OUTREACH</div>
            <div class="msg-thumb">
              <div class="msg-to">To: <b>Priya Shah</b>, Founder at Northbridge Talent</div>
              <div class="msg-subj">Cutting your team's admin, not your headcount</div>
              <div class="msg-body">Hi Priya, I saw Northbridge is scaling its London desk
              fast. Most recruiters that size lose hours a week to manual CV screening and
              follow-ups. I build <b>AI automation that quietly handles that</b> so your
              consultants stay on the phone. Worth a quick look?</div>
              <div class="msg-sign">Aron</div>
            </div>
          </div>
        </div>
        <div class="demo-cap" style="text-align:center; font-weight:400; font-style:italic; color:{INK_MUTE}; letter-spacing:0; margin-top:1rem;">A researched, personal draft - ready for you to review and send.</div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper(current: int) -> None:
    """Two-step progress stepper. `current` is 1 (Describe) or 2 (Review).

    Shows two pills - "1 Describe" and "2 Review" - with the active step in
    terracotta and the other muted, plus a clear "Step N of 2" label.
    """
    steps = [(1, "Describe"), (2, "Review")]
    pills = ""
    for i, (num, label) in enumerate(steps):
        active = " active" if num == current else ""
        pills += (
            f'<span class="pill{active}"><span class="num">{num}</span>{label}</span>'
        )
        if i < len(steps) - 1:
            pills += '<span class="track"></span>'
    st.markdown(
        f'<div class="stepper">{pills}<span class="count">Step {current} of 2</span></div>',
        unsafe_allow_html=True,
    )


def render_step(title: str, subtitle: str = "") -> None:
    """A serif numbered step heading, e.g. '1. Describe your ideal client'."""
    html = f'<div class="step">{title}</div>'
    if subtitle:
        html += f'<div class="step-sub">{subtitle}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_group(label: str, note: str = "") -> None:
    """A light grouping sub-label inside the form, e.g. 'WHO YOU TARGET'."""
    extra = f'<span class="gnote">{note}</span>' if note else ""
    st.markdown(f'<div class="form-group">{label}{extra}</div>', unsafe_allow_html=True)


def render_footer() -> None:
    """Quiet footer: review disclaimer + 'Built by Aron Sarosi'."""
    st.markdown(
        """
        <div class="footer">
          <p class="discl">Drafts are a starting point for your review. Personalise each one
          before sending, and check any contact details - the agent infers a likely
          person, it does not verify them.</p>
          <p class="built">Built by Aron Sarosi</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
