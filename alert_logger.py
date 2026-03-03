"""
Alert Logger + Railway Operations Intelligence.
Persistent incident logging with analytics aggregation
for government operations dashboards and decision support.

Supports:
  - Real-time alert persistence (memory + CSV audit trail)
  - Severity distribution analysis for resource allocation
  - Risk trend monitoring for command center briefings
  - Hourly pattern analysis for patrol scheduling optimization
  - Alert type classification for threat intelligence reports
"""

import datetime
import csv
import os
from collections import defaultdict

LOG_FILE = "data/alert_log.csv"
FIELDS = ["timestamp", "alert_type", "severity", "risk_score",
          "vibration_level", "detections", "explanation"]

_alert_history = []


def log_alert(alert_type, severity, risk_score, vibration_level,
              detections, explanation):
    """Log a single alert event."""
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alert_type": alert_type,
        "severity": severity,
        "risk_score": round(risk_score, 1),
        "vibration_level": round(vibration_level, 4),
        "detections": detections,
        "explanation": explanation,
    }
    _alert_history.append(entry)

    if len(_alert_history) > 500:
        _alert_history.pop(0)

    _append_csv(entry)
    return entry


def _append_csv(entry):
    """Append to CSV audit trail for government record-keeping."""
    try:
        file_exists = os.path.exists(LOG_FILE)
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(entry)
    except Exception:
        pass


def get_recent_alerts(n=50):
    """Return the last N alerts (most recent first)."""
    return list(reversed(_alert_history[-n:]))


def get_alert_counts():
    """Return a summary dict of alert counts by severity."""
    counts = {"CRITICAL": 0, "WARNING": 0, "CAUTION": 0, "INFO": 0, "SAFE": 0}
    for a in _alert_history:
        sev = a.get("severity", "SAFE")
        if sev in counts:
            counts[sev] += 1
        else:
            counts[sev] = 1
    return counts


def get_total_alerts():
    """Return total number of alerts logged this session."""
    return len(_alert_history)


def clear_history():
    """Clear the in-memory alert history."""
    _alert_history.clear()


# ═══════════════════════════════════════════════════════════════════
#    RAILWAY OPERATIONS INTELLIGENCE — Analytics for Command Center
# ═══════════════════════════════════════════════════════════════════

def get_severity_distribution():
    """
    Severity breakdown for resource allocation decisions.
    Helps command centers prioritize response teams.
    """
    dist = defaultdict(int)
    for a in _alert_history:
        dist[a.get("severity", "SAFE")] += 1
    return dict(dist)


def get_risk_trend(window=20):
    """
    Running risk score trend for command center briefings.
    Shows how threat levels are evolving over time.
    """
    scores = [a["risk_score"] for a in _alert_history if "risk_score" in a]
    return scores[-window:] if scores else []


def get_hourly_distribution():
    """
    Alert frequency by hour — used for optimizing patrol schedules.
    Identifies peak threat windows for RPF deployment planning.
    """
    hourly = defaultdict(int)
    for a in _alert_history:
        try:
            ts = datetime.datetime.strptime(a["timestamp"], "%Y-%m-%d %H:%M:%S")
            hour_key = ts.strftime("%H:00")
            hourly[hour_key] += 1
        except (ValueError, KeyError):
            pass
    return dict(sorted(hourly.items()))


def get_alert_type_distribution():
    """
    Alert classification breakdown for threat intelligence reports.
    Helps identify most common attack patterns.
    """
    dist = defaultdict(int)
    for a in _alert_history:
        dist[a.get("alert_type", "Unknown")] += 1
    return dict(dist)


def get_analytics_summary():
    """
    Comprehensive operations intelligence summary.
    Designed for railway authority command center dashboards.
    """
    if not _alert_history:
        return {
            "total": 0, "avg_risk": 0.0, "max_risk": 0.0,
            "most_common": "—", "critical_pct": 0.0,
        }

    risk_scores = [a["risk_score"] for a in _alert_history if "risk_score" in a]
    severity_counts = get_alert_counts()
    type_counts = get_alert_type_distribution()
    most_common = max(type_counts, key=type_counts.get) if type_counts else "—"

    total = len(_alert_history)
    critical_pct = (severity_counts.get("CRITICAL", 0) / total * 100) if total > 0 else 0

    return {
        "total": total,
        "avg_risk": round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else 0.0,
        "max_risk": max(risk_scores) if risk_scores else 0.0,
        "most_common": most_common,
        "critical_pct": round(critical_pct, 1),
    }
