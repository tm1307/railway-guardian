import datetime


MAINTENANCE_SCHEDULE = {
    "section_1": {"active": False, "task": "None"},
}

def get_maintenance_status(track_section="section_1"):
    """
    Simulates checking the central schedule.
    Returns: (is_active, task_description)
    """
    record = MAINTENANCE_SCHEDULE.get(track_section)
    
    if record and record["active"]:
        time_now = datetime.datetime.now().strftime("%H:%M")
        return True, f"{record['task']} (Started {time_now})"
    
    return False, "No Active Work Orders"

def toggle_maintenance(track_section, status):
    """
    Updates the mock database (Called by App Sidebar)
    """
    if track_section in MAINTENANCE_SCHEDULE:
        MAINTENANCE_SCHEDULE[track_section]["active"] = status
        MAINTENANCE_SCHEDULE[track_section]["task"] = "Scheduled Repair (Team A)" if status else "None"