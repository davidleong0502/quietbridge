import time
import random
import streamlit as st

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
    mood = st.radio(
        "Mood",
        ["Good", "Okay", "Lonely", "Overwhelmed"],
        label_visibility="collapsed"
    )

    if st.button("Save mood"):
        st.session_state.moods.append(mood)
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
