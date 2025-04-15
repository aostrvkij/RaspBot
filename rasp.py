from datetime import datetime, timedelta
import requests

def get_group_id(name):
    url = 'https://xn--h1amj9b.xn--80aaiac8g.xn--p1ai/api/raspGrouplist?year=2024-2025'
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        data = response.json().get('data', [])
        for i in data:
            if i['name'] == str(name):
                return i['id']
    except Exception as e:
        print("Ошибка при получении списка групп:", e)
    return None


def get_schedule(group_name, date):
    group_id = get_group_id(group_name)
    if not group_id:
        return None

    formatted_date = date.strftime('%Y-%m-%d')
    url = f'https://xn--h1amj9b.xn--80aaiac8g.xn--p1ai/api/Rasp?idGroup={group_id}&sdate={formatted_date}'
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        data = response.json()
        return data.get('data', {}).get('rasp', None)
    except Exception as e:
        print("Ошибка при получении расписания:", e)
        return None


def get_week_schedule(group_name):
    today = datetime.today()
    weekday = today.isoweekday()  # Пн=1 ... Вс=7

    # если суббота или воскресенье — берем понедельник следующей недели
    if weekday >= 6:
        monday = today + timedelta(days=(7 - weekday + 1))
    else:
        monday = today - timedelta(days=today.weekday())

    rasp = get_schedule(group_name, monday)
    if rasp is None:
        return None  # добавлено: если не получилось получить расписание

    week_data = {i: [] for i in range(1, 8)}
    for pair in rasp:
        day = pair.get('деньНедели')
        if day in week_data:
            week_data[day].append({
                "дата": pair.get("датаНачала", "")[:10],
                "деньНедели": pair.get("деньНедели"),
                "дисциплина": pair.get("дисциплина"),
                "преподаватель": pair.get("преподаватель"),
                "начало": pair.get("начало"),
                "конец": pair.get("конец"),
                "аудитория": pair.get("аудитория")
            })

    if weekday >= 6:
        return {day: week_data[day] for day in range(1, 6 + 1)}

    return {day: week_data[day] for day in range(weekday, 6 + 1)}
