import time
import random
import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates
from pathlib import Path

MOOD_GRID = [
    ["Excited", "Joyful", "Motivated", "Inspired"],
    ["Tense",   "Alert",  "Engaged",   "Proud"],
    ["Sad",     "Calm",   "Content",   "Peaceful"],
    ["Drained", "Tired",  "Restful",   "Serene"],
]
GRID_LEFT = 220
GRID_TOP = 190
CELL_W = 320
CELL_H = 190
ROWS, COLS = 4, 4
def click_to_cell(x, y):
    if x is None or y is None:
        return None
    if x < GRID_LEFT or y < GRID_TOP:
        return None
    col = (x - GRID_LEFT) // CELL_W
    row = (y - GRID_TOP) // CELL_H
    if 0 <= row < ROWS and 0 <= col < COLS:
        return int(row), int(col)
    return None
def draw_highlight(img, row, col):
    out = img.copy()
    d = ImageDraw.Draw(out)

    x0 = GRID_LEFT + col * CELL_W
    y0 = GRID_TOP + row * CELL_H
    x1 = x0 + CELL_W
    y1 = y0 + CELL_H

    inset = 10
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset

    d.rectangle([x0, y0, x1, y1], outline=(255,255,255), width=10)
    d.rectangle([x0+2, y0+2, x1-2, y1-2], outline=(0,0,0), width=6)

    return out


# ==============================
# SHARED STATE (ALL USERS ON THIS SERVER)
# ==============================
@st.cache_resource
def shared_state():
    return {
        "chat": [],   # shared chat messages
        "study": []   # names of users in silent study
    }

SHARED = shared_state()

# ==============================
# PRIVATE SESSION (PER USER)
# ==============================
if "name" not in st.session_state:
    ADJ = ["Soft", "Calm", "Warm", "Gentle", "Quiet", "Happy", "Funny"]
    NOUN = ["Cloud", "River", "Fox", "Lantern", "Pine", "Forest", "Ocean", "Sheep"]
    st.session_state.name = random.choice(ADJ) + random.choice(NOUN)

if "moods" not in st.session_state:
    st.session_state.moods = []

if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = None
    
if "selected_cell" not in st.session_state:
    st.session_state.selected_cell = None

if "reflections" not in st.session_state:
    st.session_state.reflections = []

if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

# ==============================
# UI CONFIG
# ==============================
st.set_page_config(page_title="QuietBridge", layout="centered")

st.title("QuietBridge")
st.caption(f"You are: **{st.session_state.name}**")

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Quiet Chat", "Silent Co-Study", "Reflection", "Dashboard"]
)

# ==============================
# HOME
# ==============================
if page == "Home":
    st.subheader("How are you feeling right now?")
    st.write("Click a block on the mood meter:")

    # Row of controls (Clear on the right)
    left, right = st.columns([3, 1])
    with right:
        if st.button("Clear selection"):
            st.session_state.selected_mood = None
            st.session_state.selected_cell = None
            st.rerun()

    BASE_DIR = Path(__file__).parent
    img_path = BASE_DIR / "mood_meter_4x4_color_fixed_arrow.jpg"
    base_img = Image.open(img_path)
    # Show highlighted version if selected
    img_to_show = base_img
    if st.session_state.selected_cell is not None:
        r, c = st.session_state.selected_cell
        img_to_show = draw_highlight(base_img, r, c)

    click = streamlit_image_coordinates(img_to_show, width=base_img.width)

    if click is not None:
        cell = click_to_cell(click["x"], click["y"])
        if cell is not None:
            r, c = cell
            st.session_state.selected_cell = (r, c)
            st.session_state.selected_mood = MOOD_GRID[r][c]

    if st.session_state.selected_mood:
        st.info(
            f"Selected: **{st.session_state.selected_mood}** "
            f"(Level {mood_to_num(st.session_state.selected_mood)})"
        )

    if st.button("Save mood"):
        if not st.session_state.selected_mood:
            st.warning("Please click a mood block first.")
        else:
            st.session_state.moods.append(st.session_state.selected_mood)
            st.success("Saved.")

# ==============================
# QUIET CHAT
# ==============================
elif page == "Quiet Chat":
    st.subheader("Quiet Chat")
    st.caption("Short, low-pressure messages.")

    # Show last 20 messages
    for m in SHARED["chat"][-20:]:
        st.write(f"**{m['u']}**: {m['t']}")

    msg = st.text_input("Message", placeholder="Type something gentle")

    if st.button("Send"):
        if msg.strip():
            SHARED["chat"].append({
                "u": st.session_state.name,
                "t": msg.strip(),
                "time": time.time()
            })
            st.session_state.chat_count += 1
            st.rerun()
        else:
            st.warning("Type something first.")

# ==============================
# SILENT CO-STUDY
# ==============================
elif page == "Silent Co-Study":
    room = SHARED["study"]

    st.subheader(f"{len(room)} studying quietly")
    st.caption("No chat needed. Just presence.")

    if st.session_state.name in room:
        if st.button("Leave"):
            room.remove(st.session_state.name)
            st.rerun()
    else:
        if st.button("Join"):
            room.append(st.session_state.name)
            st.rerun()

    if room:
        st.divider()
        for u in room:
            st.write(f"• {u}")

# ==============================
# REFLECTION
# ==============================
elif page == "Reflection":
    st.subheader("Prompt of the day")
    st.write("What is one small thing you survived today?")

    text = st.text_area(
        "Reflection",
        height=150,
        label_visibility="collapsed"
    )

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
# DASHBOARD
# ==============================
elif page == "Dashboard":
    st.subheader("Your wellbeing overview")

    mapping = {
        "Good": 4,
        "Okay": 3,
        "Lonely": 2,
        "Overwhelmed": 1
    }

    if st.session_state.moods:
        st.write("Mood over time")
        st.line_chart([mapping[m] for m in st.session_state.moods])
    else:
        st.info("No mood check-ins yet.")

    st.divider()

    if st.session_state.chat_count >= 2:
        st.write("You tend to reach out when you check in.")
    elif len(st.session_state.moods) >= 3:
        st.write("You have been checking in consistently.")
    elif len(st.session_state.moods) > 0:
        st.write("You have started tracking your mood.")
    else:
        st.write("Start with one check-in. That is enough.")
