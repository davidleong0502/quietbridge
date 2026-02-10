def mood_to_num(mood: str) -> int:
    mapping = {"Good": 4, "Okay": 3, "Lonely": 2, "Overwhelmed": 1}
    return mapping.get(mood, 3)

def simple_insight(moods_count: int, chats_count: int) -> str:
    if chats_count >= 2:
        return "You tend to use quiet chat when you check in."
    if moods_count >= 3:
        return "You have been checking in consistently."
    return "Small check-ins still matter."