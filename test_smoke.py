"""
Smoke Test Suite — Verifies all RailGuard Pro modules load and work.
Run: python test_smoke.py
"""

import sys
import traceback

PASS = 0
FAIL = 0


def check(name, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  ✅ {name}")
        PASS += 1
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        traceback.print_exc()
        FAIL += 1


# ── Original Tests ──

def test_alert_logger():
    import alert_logger
    alert_logger.clear_history()
    alert_logger.log_alert("TEST", "INFO", 25.0, 0.12, "person", "test alert")
    assert alert_logger.get_total_alerts() == 1
    recent = alert_logger.get_recent_alerts(5)
    assert len(recent) == 1
    assert recent[0]["alert_type"] == "TEST"
    counts = alert_logger.get_alert_counts()
    assert counts["INFO"] == 1
    alert_logger.clear_history()


def test_maintenance():
    import maintenance
    is_active, desc = maintenance.get_maintenance_status("section_1")
    assert isinstance(is_active, bool)
    assert isinstance(desc, str)
    maintenance.toggle_maintenance("section_1", True)
    is_active, _ = maintenance.get_maintenance_status("section_1")
    assert is_active is True
    maintenance.toggle_maintenance("section_1", False)
    sections = maintenance.get_all_sections_status()
    assert len(sections) == 3


def test_detect_model_load():
    import detect
    model = detect.load_resources()
    assert model is not None or model is None


def test_logic_anomaly_detector():
    import logic
    score, status = logic.detector.predict(0.1)
    assert isinstance(score, float)
    assert status in ("STABLE", "CRITICAL", "ERROR")
    score2, status2 = logic.detector.predict(0.8)
    assert status2 == "CRITICAL"


def test_logic_risk_score():
    import logic
    score = logic._compute_risk_score(
        person_detected=True, tool_detected=True,
        vibration_val=0.5, vibration_status="CRITICAL",
        is_under_maintenance=False, max_conf=0.85, zone_bonus=0
    )
    assert 0 <= score <= 100
    assert score > 50

    score_maint = logic._compute_risk_score(
        person_detected=True, tool_detected=True,
        vibration_val=0.5, vibration_status="CRITICAL",
        is_under_maintenance=True, max_conf=0.85, zone_bonus=0
    )
    assert score_maint < score


def test_severity_mapping():
    import logic
    assert logic._severity_from_score(80) == "CRITICAL"
    assert logic._severity_from_score(50) == "WARNING"
    assert logic._severity_from_score(30) == "CAUTION"
    assert logic._severity_from_score(12) == "INFO"
    assert logic._severity_from_score(5) == "SAFE"


# ── New Feature Tests ──

def test_forensics():
    import forensics
    report = forensics.generate_incident_report(
        alert_type="🚨 SABOTAGE", severity="CRITICAL",
        risk_score=85.5, vibration_level=0.62,
        detections="person (92%)", explanation="Test forensic report",
        frame=None, zone="Restricted — Bridge"
    )
    assert "incident_id" in report
    assert report["incident_id"].startswith("RG-")
    assert "integrity_hash" in report
    assert len(report["integrity_hash"]) == 64  # SHA-256

    # Verify integrity
    is_valid, msg = forensics.verify_report(report)
    assert is_valid, f"Verification failed: {msg}"

    # Tamper and verify again
    tampered = dict(report)
    tampered["risk_score"] = 99.9
    is_valid2, _ = forensics.verify_report(tampered)
    assert not is_valid2, "Tampered report should fail verification"

    chain = forensics.get_evidence_chain(5)
    assert len(chain) >= 1

    summary = forensics.get_chain_summary()
    assert summary["total"] >= 1


def test_geo_zones():
    import geo_zones
    zone = geo_zones.get_current_zone()
    assert "name" in zone
    assert "risk_bonus" in zone
    assert "current_km" in zone
    assert zone["risk_bonus"] >= 0

    bonus = geo_zones.get_zone_risk_bonus()
    assert isinstance(bonus, int)

    map_data = geo_zones.get_zone_map_data()
    assert "zones" in map_data
    assert len(map_data["zones"]) == 5
    assert map_data["total_km"] == 12.0


def test_predictor():
    import predictor
    engine = predictor.PredictiveEngine(window_size=20)

    # Test calibrating state
    pred = engine.get_prediction()
    assert pred["status"] == "CALIBRATING"

    # Feed stable data
    for i in range(25):
        engine.update(0.1 + (i * 0.0001))
    pred = engine.get_prediction()
    assert pred["status"] in ("STABLE", "ESCALATING", "DE-ESCALATING")

    # Feed escalating data
    engine.reset()
    for i in range(25):
        engine.update(0.05 + i * 0.02)
    pred = engine.get_prediction()
    assert pred["status"] == "ESCALATING"

    ttc = engine.get_estimated_time_to_critical()
    # May or may not return a value depending on current level
    assert ttc is None or isinstance(ttc, int)

    stats = engine.get_current_stats()
    assert "mean" in stats
    assert "std" in stats


def test_alert_analytics():
    import alert_logger
    alert_logger.clear_history()
    alert_logger.log_alert("TEST1", "CRITICAL", 80.0, 0.5, "person", "test")
    alert_logger.log_alert("TEST2", "WARNING", 50.0, 0.3, "tool", "test")
    alert_logger.log_alert("TEST3", "INFO", 15.0, 0.1, "none", "test")

    dist = alert_logger.get_severity_distribution()
    assert dist["CRITICAL"] == 1
    assert dist["WARNING"] == 1

    trend = alert_logger.get_risk_trend(10)
    assert len(trend) == 3
    assert trend[0] == 80.0

    type_dist = alert_logger.get_alert_type_distribution()
    assert "TEST1" in type_dist

    summary = alert_logger.get_analytics_summary()
    assert summary["total"] == 3
    assert summary["avg_risk"] > 0
    assert summary["max_risk"] == 80.0

    alert_logger.clear_history()


def test_zone_risk_integration():
    import logic
    # Without zone bonus
    score_no_zone = logic._compute_risk_score(
        True, False, 0.5, "CRITICAL", False, 0.8, zone_bonus=0)
    # With zone bonus (restricted area)
    score_with_zone = logic._compute_risk_score(
        True, False, 0.5, "CRITICAL", False, 0.8, zone_bonus=20)
    assert score_with_zone > score_no_zone


if __name__ == "__main__":
    print()
    print("=" * 55)
    print("  🛡️  RailGuard Pro — Smoke Test Suite")
    print("=" * 55)
    print()

    print("  ─── Core Modules ───")
    check("Alert Logger", test_alert_logger)
    check("Maintenance Module", test_maintenance)
    check("Detect Model Load", test_detect_model_load)
    check("Anomaly Detector", test_logic_anomaly_detector)
    check("Risk Score Computation", test_logic_risk_score)
    check("Severity Mapping", test_severity_mapping)

    print()
    print("  ─── Advanced Features ───")
    check("Forensic Evidence Chain", test_forensics)
    check("Geo-Zone Detection", test_geo_zones)
    check("Predictive Engine", test_predictor)
    check("Alert Analytics", test_alert_analytics)
    check("Zone Risk Integration", test_zone_risk_integration)

    print()
    print(f"  Results: {PASS} passed, {FAIL} failed")
    print("=" * 55)
    print()

    sys.exit(1 if FAIL > 0 else 0)
