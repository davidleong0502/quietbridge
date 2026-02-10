def mood_to_num(mood: str) -> int:
    mood = (mood or "").strip().lower()

    level_1 = {"sad", "drained", "tired", "tense", "alert"}
    level_2 = {"calm", "restful", "peaceful", "serene"}
    level_3 = {"engaged", "content", "joyful"}
    level_4 = {"excited", "motivated", "inspired", "proud"}

    if mood in level_1:
        return 1
    if mood in level_2:
        return 2
    if mood in level_3:
        return 3
    if mood in level_4:
        return 4

    # default (keeps app from crashing if something unexpected is passed)
    return 3

def simple_insight(moods_count: int, chats_count: int) -> str:
    if chats_count >= 2:
        return "You tend to use quiet chat when you check in."
    if moods_count >= 3:
        return "You have been checking in consistently."
    return "Small check-ins still matter."
