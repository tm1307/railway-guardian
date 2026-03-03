"""
Maintenance Schedule Manager — Simulates a centralized railway maintenance API.
Supports multiple track sections with time-window scheduling.
"""

import datetime


MAINTENANCE_SCHEDULE = {
    "section_1": {"active": False, "task": "None", "team": "—",
                  "start": None, "end": None},
    "section_2": {"active": False, "task": "None", "team": "—",
                  "start": None, "end": None},
    "section_3": {"active": False, "task": "None", "team": "—",
                  "start": None, "end": None},
}


def get_maintenance_status(track_section="section_1"):
    """
    Check if a section is currently under scheduled maintenance.
    Returns: (is_active: bool, task_description: str)
    """
    record = MAINTENANCE_SCHEDULE.get(track_section)
    if not record:
        return False, "Unknown Section"

    if record["active"]:
        # Check time window if set
        now = datetime.datetime.now()
        if record["start"] and record["end"]:
            if not (record["start"] <= now <= record["end"]):
                return False, "Scheduled work not in active time window"

        time_str = now.strftime("%H:%M")
        team = record.get("team", "—")
        return True, f"{record['task']} | Team: {team} (Active since {time_str})"

    return False, "No Active Work Orders"


def toggle_maintenance(track_section, status):
    """
    Toggle maintenance on/off for a section (called by sidebar).
    Backward-compatible with the original API.
    """
    if track_section in MAINTENANCE_SCHEDULE:
        MAINTENANCE_SCHEDULE[track_section]["active"] = status
        if status:
            MAINTENANCE_SCHEDULE[track_section]["task"] = "Scheduled Repair"
            MAINTENANCE_SCHEDULE[track_section]["team"] = "Team A"
            MAINTENANCE_SCHEDULE[track_section]["start"] = datetime.datetime.now()
            MAINTENANCE_SCHEDULE[track_section]["end"] = (
                datetime.datetime.now() + datetime.timedelta(hours=4)
            )
        else:
            MAINTENANCE_SCHEDULE[track_section]["task"] = "None"
            MAINTENANCE_SCHEDULE[track_section]["team"] = "—"
            MAINTENANCE_SCHEDULE[track_section]["start"] = None
            MAINTENANCE_SCHEDULE[track_section]["end"] = None


def get_all_sections_status():
    """
    Return a summary of all track sections for the dashboard overview.
    Returns list of dicts with section info.
    """
    result = []
    for section_id, data in MAINTENANCE_SCHEDULE.items():
        is_active, desc = get_maintenance_status(section_id)
        result.append({
            "section": section_id.replace("_", " ").title(),
            "active": is_active,
            "task": data["task"],
            "team": data.get("team", "—"),
            "description": desc,
        })
    return result