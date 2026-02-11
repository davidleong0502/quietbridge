# app.py — QuietBridge (no URL navigation for mood tiles)

import time
import random
import json
import datetime
from pathlib import Path
from datetime import date, timedelta

import streamlit as st
import pandas as pd
import altair as alt

# Optional (safe to keep even if unused right now)
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

from mood_logic import mood_to_num, simple_insight


# ==============================
# THEME
# ==============================
def apply_quietbridge_theme():
    st.markdown(
        """
        <style>
        :root { color-scheme: light !important; }
        html, body { color-scheme: light !important; }

        .stApp {
            background: linear-gradient(180deg, #EAF3FF 0%, #F6FAFF 55%, #FFFFFF 100%);
            color: #0F172A;
        }

        [data-testid="stAppViewContainer"] { color: #0F172A; }

        h1, h2, h3, h4 {
            color: #0B1220 !important;
            letter-spacing: -0.2px;
        }

        .qb-muted { color: #475569 !important; }

        .block-container {
            max-width: 720px;
            padding-top: 2.2rem;
        }

        h1 { text-align: center; margin-bottom: 0.25rem; }
        h2, h3 { text-align: center; }

        [data-testid="stCaptionContainer"],
        [data-testid="stMarkdownContainer"] p { text-align: center; }

        section[data-testid="stSidebar"] {
            background: rgba(255,255,255,0.80);
            border-right: 1px solid rgba(15, 23, 42, 0.08);
            backdrop-filter: blur(8px);
        }

        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] * {
          color: #0F172A !important;
          opacity: 1 !important;
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] label *,
        section[data-testid="stSidebar"] [role="radiogroup"] label,
        section[data-testid="stSidebar"] [role="radiogroup"] label * {
          color: #0F172A !important;
          opacity: 1 !important;
          font-weight: 500 !important;
        }

        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            border-radius: 12px !important;
            border: 1px solid rgba(15, 23, 42, 0.18) !important;
            background: rgba(255,255,255,0.95) !important;
        }

        div.stButton > button:first-child {
            background: #FF6B6B;
            color: white;
            border: 1px solid rgba(0,0,0,0.05);
            border-radius: 12px;
            padding: 0.55rem 0.9rem;
            font-weight: 600;
        }
        div.stButton > button:first-child:hover { background: #FF5252; }

        .qb-card {
          background: rgba(255,255,255,0.75);
          border: 1px solid rgba(0,0,0,0.06);
          border-radius: 18px;
          padding: 14px 14px 12px 14px;
          box-shadow: 0 10px 24px rgba(0,0,0,0.06);
          margin: 10px 0 6px 0;
          backdrop-filter: blur(6px);
          animation: qbFadeIn 300ms ease-out;
        }

        @keyframes qbFadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0px); }
        }

        .qb-row {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          justify-content: space-between;
        }

        .qb-pill {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 8px 10px;
          border-radius: 999px;
          background: rgba(255,255,255,0.85);
          border: 1px solid rgba(0,0,0,0.06);
          font-size: 0.92rem;
          box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        }

        .qb-pill .dot {
          width: 10px; height: 10px; border-radius: 50%;
          background: rgba(0,0,0,0.18);
        }

        .qb-badge {
          padding: 10px 12px;
          border-radius: 14px;
          background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.65));
          border: 1px solid rgba(0,0,0,0.06);
          min-width: 160px;
          flex: 1;
        }

        .qb-badge .big {
          font-size: 1.35rem;
          font-weight: 800;
          letter-spacing: -0.3px;
        }

        .qb-badge .label {
          opacity: 0.75;
          font-size: 0.86rem;
          margin-top: 2px;
        }

        .qb-pulse { animation: qbPulse 1.3s ease-in-out infinite; }
        @keyframes qbPulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.03); }
          100% { transform: scale(1); }
        }

        .qb-progress-wrap {
          margin-top: 10px;
          padding: 10px 12px;
          border-radius: 14px;
          background: rgba(255,255,255,0.72);
          border: 1px solid rgba(0,0,0,0.06);
        }

        .qb-progress-bar {
          width: 100%;
          height: 12px;
          border-radius: 999px;
          background: rgba(0,0,0,0.06);
          overflow: hidden;
          position: relative;
        }

        .qb-progress-fill {
          height: 100%;
          border-radius: 999px;
          background: linear-gradient(90deg, rgba(255,140,0,0.85), rgba(0,200,140,0.85));
          position: relative;
          overflow: hidden;
        }

        .qb-progress-fill::after {
          content: "";
          position: absolute;
          top: 0; left: -40%;
          width: 40%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.55), transparent);
          animation: qbShimmer 1.6s linear infinite;
        }

        @keyframes qbShimmer {
          0% { left: -40%; }
          100% { left: 100%; }
        }

        .qb-mini { font-size: 0.86rem; opacity: 0.80; margin-top: 6px; }
        .qb-title { font-weight: 800; font-size: 1.05rem; margin-bottom: 8px; }

        .qb-heatmap {
          margin-top: 10px;
          padding: 10px 10px 6px 10px;
          border-radius: 14px;
          background: rgba(255,255,255,0.65);
          border: 1px solid rgba(0,0,0,0.06);
        }

        /* Mood grid container */
        .qb-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 10px;
          margin: 10px auto 6px auto;
          max-width: 720px;
        }

        /* Make buttons look like tiles ONLY inside qb-grid */
        .qb-grid div[data-testid="stButton"] > button {
          width: 100% !important;
          height: 84px !important;
          border-radius: 16px !important;
          font-weight: 800 !important;
          font-size: 1.05rem !important;
          letter-spacing: -0.2px !important;
          border: 2px solid rgba(255,255,255,0.55) !important;
          box-shadow: 0 10px 24px rgba(0,0,0,0.07) !important;
          transition: transform 120ms ease, box-shadow 120ms ease, filter 120ms ease !important;
        }
        .qb-grid div[data-testid="stButton"] > button:hover {
          transform: translateY(-2px) scale(1.01) !important;
          box-shadow: 0 14px 30px rgba(0,0,0,0.10) !important;
          filter: saturate(1.04) !important;
        }

        /* Selected tile wrapper adds outline */
        .qb-selected div[data-testid="stButton"] > button {
          outline: 4px solid rgba(255,255,255,0.70) !important;
          box-shadow: 0 0 0 3px rgba(0,0,0,0.10), 0 16px 34px rgba(0,0,0,0.14) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


apply_quietbridge_theme()


# ==============================
# SHARED STATE (ALL USERS ON THIS SERVER)
# ==============================
@st.cache_resource
def shared_state():
    return {
        "chat": [],
        "study": [],
        "bulletins": [],
        "replies": {},  # post_id -> list of replies
    }


SHARED = shared_state()


# ==============================
# PERSISTENCE (JSON files)
# ==============================
CHECKINS_PATH = Path("checkins.json")
MOODS_PATH = Path("moods.json")


def _load_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_json_list(path: Path, rows: list[dict]) -> None:
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_checkins() -> list[dict]:
    return _load_json_list(CHECKINS_PATH)


def _save_checkins(checkins: list[dict]) -> None:
    _save_json_list(CHECKINS_PATH, checkins)


def _load_moods() -> list[dict]:
    return _load_json_list(MOODS_PATH)


def _save_moods(moods: list[dict]) -> None:
    _save_json_list(MOODS_PATH, moods)


def _upsert_today_checkin(checkins: list[dict], word: str, mode: str) -> list[dict]:
    """
    One check-in per day: saving again overwrites today's entry.
    Stores both the selected Mood Meter word and the backend mode.
    """
    today = date.today().isoformat()
    level = mood_to_num(mode)
    rec = {"date": today, "word": word, "mode": mode, "level": level}

    out = [c for c in checkins if c.get("date") != today]
    out.append(rec)
    out.sort(key=lambda x: x.get("date", ""))
    return out


def _unique_dates(checkins: list[dict]) -> set[date]:
    out = set()
    for c in checkins:
        d = c.get("date")
        if d:
            out.add(date.fromisoformat(d))
    return out


def compute_streaks(checkins: list[dict], grace_days: int = 0) -> dict:
    days = _unique_dates(checkins)
    if not days:
        return {"current": 0, "best": 0}

    cur = 0
    misses = 0
    cursor = date.today()
    while True:
        if cursor in days:
            cur += 1
        else:
            misses += 1
            if misses > grace_days:
                break
        cursor -= timedelta(days=1)

    sorted_days = sorted(days)
    best = 0
    for start in sorted_days:
        streak = 0
        misses = 0
        cursor = start
        while True:
            if cursor in days:
                streak += 1
            else:
                misses += 1
                if misses > grace_days:
                    break
            cursor += timedelta(days=1)
        best = max(best, streak)

    return {"current": cur, "best": best}


def week_progress(checkins: list[dict], goal: int = 5) -> tuple[int, int]:
    today = date.today()
    y, w, _ = today.isocalendar()
    days = _unique_dates(checkins)
    cnt = sum(1 for d in days if d.isocalendar()[:2] == (y, w))
    return cnt, goal


def mood_stats_7d(checkins: list[dict]) -> dict:
    if not checkins:
        return {"avg_level": None, "top_word": None}

    today = date.today()
    cutoff = today - timedelta(days=6)
    last7 = [c for c in checkins if c.get("date") and date.fromisoformat(c["date"]) >= cutoff]
    if not last7:
        return {"avg_level": None, "top_word": None}

    avg = sum(int(c.get("level", 3)) for c in last7) / len(last7)

    freq = {}
    for c in last7:
        w = c.get("word")
        if w:
            freq[w] = freq.get(w, 0) + 1
    top_word = max(freq, key=freq.get) if freq else None

    return {"avg_level": avg, "top_word": top_word}


def calendar_heatmap(checkins: list[dict], weeks: int = 16):
    if not checkins:
        st.info("No check-ins yet.")
        return

    day_level = {}
    for c in checkins:
        if c.get("date"):
            day_level[date.fromisoformat(c["date"])] = int(c.get("level", 3))

    end = date.today()
    start = end - timedelta(days=weeks * 7 - 1)

    rows = []
    d = start
    while d <= end:
        lvl = day_level.get(d, 0)
        week_idx = (d - start).days // 7
        dow = d.weekday()  # Mon=0..Sun=6
        rows.append({"date": d.isoformat(), "week": week_idx, "dow": dow, "level": lvl})
        d += timedelta(days=1)

    df = pd.DataFrame(rows)

    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X("week:O", title=None, axis=alt.Axis(labels=False, ticks=False)),
            y=alt.Y(
                "dow:O",
                title=None,
                axis=alt.Axis(labelExpr="['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][datum.value]"),
            ),
            color=alt.Color("level:Q", scale=alt.Scale(domain=[0, 1, 2, 3, 4]), legend=None),
            tooltip=["date:N", "level:Q"],
        )
        .properties(height=140)
    )

    st.altair_chart(chart, use_container_width=True)


def render_streak_card_polished(checkins: list[dict]):
    gentle = st.toggle("Gentle streak mode (1-day grace)", value=True)
    grace = 1 if gentle else 0

    streaks = compute_streaks(checkins, grace_days=grace)
    wk, goal = week_progress(checkins, goal=5)
    stats = mood_stats_7d(checkins)

    today_iso = date.today().isoformat()
    checked_today = any(c.get("date") == today_iso for c in checkins)

    if "last_seen_checkin_date" not in st.session_state:
        st.session_state.last_seen_checkin_date = None

    if checked_today and st.session_state.last_seen_checkin_date != today_iso:
        st.balloons()
        st.session_state.last_seen_checkin_date = today_iso

    pct = 0 if goal <= 0 else min(100, int((wk / goal) * 100))
    avg = "-" if stats["avg_level"] is None else f"{stats['avg_level']:.2f}"
    top_word = stats["top_word"]

    if streaks["current"] >= 7:
        vibe = "Strong week"
    elif streaks["current"] >= 3:
        vibe = "Nice momentum"
    elif streaks["current"] >= 1:
        vibe = "Good start"
    else:
        vibe = "Start today"

    status_text = "Checked in today" if checked_today else "Not checked in yet"
    status_dot = "rgba(0,180,120,0.85)" if checked_today else "rgba(255,140,0,0.85)"
    pulse_class = "qb-badge qb-pulse" if checked_today else "qb-badge"

    st.markdown(
        f"""
        <div class="qb-card">
          <div class="qb-title">Daily check-in streak</div>

          <div class="qb-row" style="align-items:center; margin-bottom: 10px;">
            <span class="qb-pill">
              <span class="dot" style="background:{status_dot};"></span>
              <b>{status_text}</b>
            </span>
            <span class="qb-pill">{vibe}</span>
            {"<span class='qb-pill'>Most common (7d): <b>"+top_word+"</b></span>" if top_word else ""}
          </div>

          <div class="qb-row">
            <div class="{pulse_class}">
              <div class="big">{streaks["current"]}</div>
              <div class="label">Current streak</div>
            </div>
            <div class="qb-badge">
              <div class="big">{streaks["best"]}</div>
              <div class="label">Best streak</div>
            </div>
            <div class="qb-badge">
              <div class="big">{avg}</div>
              <div class="label">Avg level (7 days)</div>
            </div>
            <div class="qb-badge">
              <div class="big">{wk}/{goal}</div>
              <div class="label">Weekly goal</div>
            </div>
          </div>

          <div class="qb-progress-wrap">
            <div style="display:flex; justify-content:space-between; gap:10px;">
              <div class="qb-mini"><b>Weekly progress</b> — aim for {goal} check-ins</div>
              <div class="qb-mini"><b>{pct}%</b></div>
            </div>
            <div class="qb-progress-bar" aria-label="weekly-progress">
              <div class="qb-progress-fill" style="width:{pct}%;"></div>
            </div>
            <div class="qb-mini">Consistency beats perfection</div>
          </div>

          <div class="qb-heatmap">
            <div class="qb-mini" style="margin-bottom:6px;"><b>Last 16 weeks</b></div>
        """,
        unsafe_allow_html=True,
    )

    calendar_heatmap(checkins, weeks=16)
    st.markdown("</div></div>", unsafe_allow_html=True)


# ==============================
# MOOD TILES (NO LINKS, NO URL CHANGE)
# ==============================

def render_mood_tiles(mood_grid: list[list[str]], selected_mood: str | None):
    st.markdown("<div class='qb-grid'>", unsafe_allow_html=True)

    for r, row in enumerate(mood_grid):
        cols = st.columns(4)
        for c, word in enumerate(row):
            with cols[c]:
                if word == selected_mood:
                    st.markdown("<div class='qb-selected'>", unsafe_allow_html=True)

                if st.button(word, key=f"mood_{r}_{c}", use_container_width=True):
                    st.session_state.selected_mood = word
                    st.session_state.selected_mode = mood_to_num(word)
                    st.rerun()

                if word == selected_mood:
                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)




# ==============================
# SESSION STATE INIT
# ==============================
if "pending_nav" not in st.session_state:
    st.session_state.pending_nav = None

if "guided_banner" not in st.session_state:
    st.session_state.guided_banner = ""

if "name" not in st.session_state:
    ADJ = ["Soft", "Calm", "Warm", "Gentle", "Quiet", "Happy", "Funny"]
    NOUN = ["Cloud", "River", "Fox", "Lantern", "Pine", "Forest", "Ocean", "Sheep"]
    st.session_state.name = random.choice(ADJ) + random.choice(NOUN)

if "moods" not in st.session_state:
    st.session_state.moods = _load_moods()

if "checkins" not in st.session_state:
    st.session_state.checkins = _load_checkins()

if "reflections" not in st.session_state:
    st.session_state.reflections = []

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = None

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = None

if "mood_words" not in st.session_state:
    st.session_state.mood_words = []

if "last_mood" not in st.session_state:
    st.session_state.last_mood = None

if "support_mode" not in st.session_state:
    st.session_state.support_mode = None


# ==============================
# UI
# ==============================
st.title("QuietBridge")
st.caption(f"You are: **{st.session_state.name}**")

PAGES = ["Home", "Chatroom", "Silent Co-Study", "Reflection", "Community Query", "Dashboard"]

if "nav" not in st.session_state:
    st.session_state.nav = "Home"

if st.session_state.pending_nav in PAGES:
    st.session_state.nav = st.session_state.pending_nav
    st.session_state.pending_nav = None

page = st.sidebar.radio("Navigate", PAGES, key="nav")
st.session_state.pending_nav = None


# ==============================
# HOME
# ==============================
if page == "Home":
    st.subheader("How are you feeling right now?")
    st.caption("Tap a word. First instinct is fine.")

    render_streak_card_polished(st.session_state.checkins)
    st.divider()

    with st.expander("Streak settings"):
        if st.button("Reset streak data (demo)", type="secondary"):
            st.session_state.checkins = []
            _save_checkins([])
            st.success("Streak data cleared.")
            st.rerun()

    mood_grid = [
        ["Excited", "Joyful", "Motivated", "Inspired"],
        ["Tense",   "Alert",  "Engaged",   "Proud"],
        ["Sad",     "Calm",   "Content",   "Peaceful"],
        ["Drained", "Tired",  "Restful",   "Serene"],
    ]

    st.markdown("#### Mood meter")

    top = st.columns([1, 8, 1])
    with top[1]:
        st.caption("Higher energy")

    mid = st.columns([1, 8, 1])
    with mid[1]:
        render_mood_tiles(mood_grid, st.session_state.selected_mood)

        cA, cB = st.columns([3, 1])
        with cA:
            if st.session_state.selected_mood:
                st.success(f"Selected: **{st.session_state.selected_mood}**")
            else:
                st.info("Select a word above.")
        with cB:
            if st.button("Clear", use_container_width=True):
                st.session_state.selected_mood = None
                st.session_state.selected_mode = None
                st.rerun()

    bottom = st.columns([1, 8, 1])
    with bottom[1]:
        st.caption("Lower energy")

    st.divider()

    if st.button("Save mood", use_container_width=True):
        if not st.session_state.selected_mode:
            st.warning("Pick a mood word first.")
        else:
            st.session_state.moods.append(
                {"mood": st.session_state.selected_mood, "timestamp": time.time()}
            )
            _save_moods(st.session_state.moods)

            st.session_state.last_mood = st.session_state.selected_mode
            st.session_state.mood_words.append(st.session_state.selected_mood)

            st.session_state.checkins = _upsert_today_checkin(
                st.session_state.checkins,
                word=st.session_state.selected_mood,
                mode=st.session_state.selected_mood,
            )
            _save_checkins(st.session_state.checkins)

            st.toast("Check-in saved.", icon="✅")
            st.success("Saved.")


# ==============================
# CHATROOM
# ==============================
elif page == "Chatroom":
    st.subheader("A gentle shared space to talk")

    if st.session_state.get("guided_banner"):
        st.info(st.session_state.guided_banner)

    st.caption("Short, low-pressure messages.")

    for m in SHARED["chat"][-20:]:
        st.write(f"**{m['u']}**: {m['t']}")

    msg = st.text_input("Message", placeholder="Type something gentle")

    if st.button("Send"):
        if msg.strip():
            SHARED["chat"].append({"u": st.session_state.name, "t": msg.strip(), "time": time.time()})
            st.session_state.chat_count += 1
            st.rerun()
        else:
            st.warning("Type something first.")


# ==============================
# SILENT CO-STUDY
# ==============================
elif page == "Silent Co-Study":
    room = SHARED["study"]
    n = len(room)

    st.subheader("Silent Co-Study")
    st.caption("No chat needed. Just presence.")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.session_state.name in room:
            if st.button("Leave room", use_container_width=True):
                room.remove(st.session_state.name)
                st.rerun()
        else:
            if st.button("Join room", use_container_width=True):
                room.append(st.session_state.name)
                st.rerun()

    st.divider()

    st.markdown("### Room is currently")
    st.markdown(f"## **{n}** quiet souls")
    st.caption("Each lamp is a person studying right now.")

    max_icons = 24
    lit = min(n, max_icons)
    extra = max(0, n - max_icons)

    icons = "💡" * lit + (f" +{extra}" if extra else "")
    st.markdown(f"<div style='font-size: 34px; line-height: 1.6;'>{icons}</div>", unsafe_allow_html=True)

    st.divider()

    if room:
        with st.expander("See who’s here", expanded=False):
            for u in room:
                st.write(f"- {u}")


# ==============================
# REFLECTION
# ==============================
elif page == "Reflection":
    st.subheader("Prompt of the day")
    st.write("What is one small thing you survived today?")

    text = st.text_area("Reflection", height=150, label_visibility="collapsed")

    if st.button("Save reflection"):
        if text.strip():
            st.session_state.reflections.append(text.strip())
            st.success("Saved.")
        else:
            st.warning("Write something first.")

    if st.session_state.reflections:
        st.divider()
        st.write("Recent reflections:")
        for r in reversed(st.session_state.reflections[-3:]):
            st.write(f"- {r}")


# ==============================
# COMMUNITY QUERY
# ==============================
elif page == "Community Query":
    st.subheader("Community Query")
    st.caption("Post a worry or question. Others can reply anonymously with gentle advice.")

    with st.expander("Post something (anonymous to others)", expanded=True):
        title = st.text_input("Title", placeholder="e.g., Feeling behind in school")
        body = st.text_area("What’s going on?", placeholder="Share as much as you want.", height=120)

        col1, col2 = st.columns([1, 2])
        with col1:
            post_anon = st.checkbox("Post anonymously", value=True)
        with col2:
            st.caption("If anonymous: your username won’t be shown on the board.")

        if st.button("Post to board", use_container_width=True):
            if not title.strip() or not body.strip():
                st.warning("Please fill in both title and details.")
            else:
                post_id = f"p_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
                SHARED["bulletins"].append(
                    {
                        "id": post_id,
                        "title": title.strip(),
                        "body": body.strip(),
                        "author": None if post_anon else st.session_state.name,
                        "time": time.time(),
                    }
                )
                SHARED["replies"].setdefault(post_id, [])
                st.success("Posted.")
                st.rerun()

    st.divider()

    posts = list(reversed(SHARED["bulletins"]))
    if not posts:
        st.info("No posts yet. Be the first to start the board.")
    else:
        q = st.text_input("Search posts", placeholder="Type keywords…")
        if q.strip():
            ql = q.strip().lower()
            posts = [p for p in posts if ql in p["title"].lower() or ql in p["body"].lower()]

        for p in posts[:30]:
            author_label = "Anonymous" if p["author"] is None else p["author"]

            with st.container():
                st.markdown(f"### {p['title']}")
                st.caption(f"Posted by **{author_label}**")
                st.write(p["body"])

                replies = SHARED["replies"].get(p["id"], [])
                if replies:
                    st.write("**Replies:**")
                    for r in replies[-10:]:
                        st.write(f"- {r['text']}")
                else:
                    st.caption("No replies yet.")

                with st.form(key=f"reply_form_{p['id']}", clear_on_submit=True):
                    reply_text = st.text_area(
                        "Reply (anonymous)",
                        key=f"reply_{p['id']}",
                        placeholder="Write something helpful and kind…",
                        height=90,
                    )
                    submitted = st.form_submit_button("Send reply")

                if submitted:
                    if reply_text.strip():
                        rep_id = f"r_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
                        SHARED["replies"].setdefault(p["id"], []).append(
                            {"id": rep_id, "text": reply_text.strip(), "time": time.time()}
                        )
                        st.rerun()
                    else:
                        st.warning("Write a reply first.")

                st.divider()


# ==============================
# DASHBOARD
# ==============================
elif page == "Dashboard":
    st.subheader("Here is your wellbeing overview!")

    if st.session_state.moods:
        st.write("### Your Mood History")
        mood_entries = st.session_state.moods
        mood_values = [mood_to_num(entry["mood"]) for entry in mood_entries]
        mood_timestamps = [datetime.datetime.fromtimestamp(entry["timestamp"]) for entry in mood_entries]

        mood_df = pd.DataFrame({"Date": mood_timestamps, "Mood Score": mood_values}).set_index("Date")
        st.line_chart(mood_df)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.write("### Summary of your Moods")
            mood_strings = [entry["mood"] for entry in st.session_state.moods]
            mood_counts = pd.Series(mood_strings).value_counts()
            st.write("**Your most frequent moods:**")
            for mood, count in mood_counts.head(3).items():
                st.write(f"- {mood}: {count} times")

            avg_mood_score = sum(mood_values) / len(mood_values)
            st.write(f"**Average mood score:** {avg_mood_score:.2f} (1=lowest, 4=highest)")

        with col2:
            st.write("### An Insight for You")
            avg_mood_score = sum(mood_values) / len(mood_values)
            if avg_mood_score > 3:
                st.success("Predominantly positive moods lately.")
            elif avg_mood_score > 2:
                st.info("Generally balanced moods.")
            else:
                st.warning("Looks like a tougher period. Consider using Reflection or reaching out.")

        st.divider()

        st.write("### Mood Log")
        st.caption("All moods you've recorded, with timestamps")

        for entry in reversed(st.session_state.moods):
            mood = entry["mood"]
            ts = datetime.datetime.fromtimestamp(entry["timestamp"])
            formatted_time = ts.strftime("%B %d, %Y at %I:%M %p")
            st.write(f"**{mood}** — {formatted_time}")
    else:
        st.info("No mood check-ins yet. Start by logging your mood on the Home page!")

    st.divider()

    if st.session_state.chat_count >= 2:
        st.write("You tend to reach out when you check in.")
    elif len(st.session_state.moods) >= 3:
        st.write("You have been checking in consistently.")
    elif len(st.session_state.moods) > 0:
        st.write("You have started tracking your mood.")
    else:
        st.write("Start with one check-in. That is enough for today.")
