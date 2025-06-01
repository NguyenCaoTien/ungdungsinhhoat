import json
import os

DATA_FILE = "datarac/HD.JSON"

def load_activities():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_activities(activities):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(activities, f, ensure_ascii=False, indent=4)

def write_activity(username: str, date: str, title: str, time: str, notes: str, activity_id: str):
    activities = load_activities()
    activities.append({
        "id": activity_id,
        "username": username,
        "date": date,
        "title": title,
        "time": time,
        "notes": notes
    })
    save_activities(activities)

def get_all_activities():
    return load_activities()

def get_user_activities(username: str):
    return [act for act in load_activities() if act.get("username") == username]

def update_activity(activity_id: str, new_data: dict):
    activities = load_activities()
    updated = False
    for act in activities:
        if act.get("id") == activity_id:
            act.update(new_data)
            updated = True
            break
    if updated:
        save_activities(activities)
    else:
        raise ValueError(f"Không tìm thấy hoạt động với id = {activity_id}")


def delete_activity(activity_id: str):
    activities = load_activities()
    new_list = [act for act in activities if act.get("id") != activity_id]
    if len(new_list) == len(activities):
        raise ValueError(f"Không tìm thấy hoạt động với id = {activity_id}")
    save_activities(new_list)
