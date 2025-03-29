import requests
from datetime import datetime, timedelta


def get_group_id(name):
    """Получает ID группы по названию"""
    url_id = "https://xn--h1amj9b.xn--80aaiac8g.xn--p1ai/api/raspGrouplist?year=2024-2025"
    resp = requests.get(url_id).json()["data"]
    for i in resp:
        if i["name"] == str(name):
            return i["id"]
    return None


def get_rasp_week(group_name):
    """Получает расписание на текущую или следующую неделю"""
    group_id = get_group_id(group_name)
    if not group_id:
        return None

    today = datetime.today()
    weekday = today.weekday()

    # Если сегодня пятница и пары уже прошли, переключаем на следующую неделю
    if weekday == 4 and datetime.now().hour >= 18:
        monday = today + timedelta(days=(7 - weekday))
    else:
        monday = today - timedelta(days=weekday)

    date = monday.strftime("%Y-%m-%d")

    url = f"https://xn--h1amj9b.xn--80aaiac8g.xn--p1ai/api/Rasp?idGroup={group_id}&sdate={date}"
    resp = requests.get(url).json()

    if "data" not in resp or "rasp" not in resp["data"]:
        return None

    schedule = {}
    for lesson in resp["data"]["rasp"]:
        day = lesson["день_недели"]
        lesson_date = lesson["датаНачала"][:10]
        lesson_datetime = datetime.strptime(lesson["датаНачала"], "%Y-%m-%dT%H:%M:%S")

        # Пропускаем пары, которые уже прошли сегодня
        if lesson_datetime.date() < today.date() or (
                lesson_datetime.date() == today.date() and lesson_datetime < datetime.now()):
            continue

        if day not in schedule:
            schedule[day] = {"date": lesson_date, "lessons": []}

        schedule[day]["lessons"].append(
            f"🕒 {lesson['начало']} - {lesson['конец']} (ауд: {lesson['аудитория']})\n"
            f"📚 {lesson['дисциплина']}\n"
            f"👨‍🏫 {lesson['преподаватель']}\n"
            "-------------------"
        )

    # Если расписание пустое на текущую неделю, то ищем расписание на следующую
    if not schedule:
        monday_next_week = monday + timedelta(days=7)
        date_next_week = monday_next_week.strftime("%Y-%m-%d")
        url_next_week = f"https://xn--h1amj9b.xn--80aaiac8g.xn--p1ai/api/Rasp?idGroup={group_id}&sdate={date_next_week}"
        resp_next_week = requests.get(url_next_week).json()

        if "data" not in resp_next_week or "rasp" not in resp_next_week["data"]:
            return None

        for lesson in resp_next_week["data"]["rasp"]:
            day = lesson["день_недели"]
            lesson_date = lesson["датаНачала"][:10]
            lesson_datetime = datetime.strptime(lesson["датаНачала"], "%Y-%m-%dT%H:%M:%S")

            if day not in schedule:
                schedule[day] = {"date": lesson_date, "lessons": []}

            schedule[day]["lessons"].append(
                f"🕒 {lesson['начало']} - {lesson['конец']} (ауд: {lesson['аудитория']})\n"
                f"📚 {lesson['дисциплина']}\n"
                f"👨‍🏫 {lesson['преподаватель']}\n"
                "-------------------"
            )

    return schedule
