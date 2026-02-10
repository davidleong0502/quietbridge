import streamlit as st
from mood_logic import mood_to_num, simple_insight
from personas import generate_name

st.set_page_config(page_title="QuietBridge", layout="centered")

# -------- Session State --------
if "moods" not in st.session_state:
    st.session_state.moods = []
if "reflections" not in st.session_state:
    st.session_state.reflections = []
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
if "study_count" not in st.session_state:
    st.session_state.study_count = 3
if "match_name" not in st.session_state:
    st.session_state.match_name = generate_name()

# -------- Navigation --------
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Quiet Chat", "Silent Co-Study", "Reflection", "Dashboard"]
)

st.title("QuietBridge")

if page == "Home":
    st.subheader("How are you feeling right now?")
    mood = st.radio("Mood", ["Good", "Okay", "Lonely", "Overwhelmed"], label_visibility="collapsed")
    if st.button("Save mood"):
        st.session_state.moods.append(mood)
        st.success("Saved.")

elif page == "Quiet Chat":
    st.subheader(f"Matched with: {st.session_state.match_name}")
    st.caption("Prototype chat. Keep it short and low-pressure.")
    msg = st.text_input("You", placeholder="Type a short message")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Send"):
            if msg.strip():
                st.session_state.chat_count += 1
                st.write(f"You: {msg}")
            else:
                st.warning("Type something first.")
    with col2:
        if st.button("New match"):
            st.session_state.match_name = generate_name()
            st.success("Matched.")

elif page == "Silent Co-Study":
    st.subheader(f"{st.session_state.study_count} students studying quietly")
    st.caption("No chat needed. Just presence.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Join"):
            st.session_state.study_count += 1
    with col2:
        if st.button("Leave"):
            st.session_state.study_count = max(0, st.session_state.study_count - 1)

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

elif page == "Dashboard":
    st.subheader("Your wellbeing overview")
    nums = [mood_to_num(m) for m in st.session_state.moods]
    st.write("Mood over time")
    if nums:
        st.line_chart(nums)
    else:
        st.info("No mood check-ins yet. Add a few on the Home page.")

    st.divider()
    st.write("Summary")
    moods_count = len(st.session_state.moods)
    if moods_count >= 3:
        st.write("You have been checking in consistently.")
    elif moods_count > 0:
        st.write("You have started tracking your mood. Keep it light.")
    else:
        st.write("Start with one check-in. That is enough.")

    st.divider()
    st.write("Insight")
    st.write(simple_insight(len(st.session_state.moods), st.session_state.chat_count))