import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.severity_analyzer import SeverityAnalyzer


def test_analyze_healthy():
    sa = SeverityAnalyzer()
    result = sa.analyze(5.0, "Tomato Healthy", 0.95)
    assert result["severity"] == "Healthy"
    assert result["risk_level"] == "None"


def test_analyze_mild():
    sa = SeverityAnalyzer()
    result = sa.analyze(8.0, "Tomato Early Blight", 0.90)
    assert result["severity"] == "Mild"
    assert result["risk_level"] == "Low"


def test_analyze_moderate():
    sa = SeverityAnalyzer()
    result = sa.analyze(20.0, "Tomato Late Blight", 0.90)
    assert result["severity"] == "Moderate"
    assert result["risk_level"] == "Medium"


def test_analyze_severe():
    sa = SeverityAnalyzer()
    result = sa.analyze(45.0, "Tomato Bacterial Spot", 0.90)
    assert result["severity"] == "Severe"
    assert result["risk_level"] == "High"


def test_get_severity_meter_value():
    sa = SeverityAnalyzer()
    assert sa.get_severity_meter_value("Healthy") == 0
    assert sa.get_severity_meter_value("Mild") == 25
    assert sa.get_severity_meter_value("Moderate") == 55
    assert sa.get_severity_meter_value("Severe") == 90


def test_get_treatment_urgency():
    sa = SeverityAnalyzer()
    assert "No treatment" in sa.get_treatment_urgency("Healthy")
    assert "Low" in sa.get_treatment_urgency("Mild")
    assert "Medium" in sa.get_treatment_urgency("Moderate")
    assert "High" in sa.get_treatment_urgency("Severe")


def test_calculate_yield_impact():
    sa = SeverityAnalyzer()
    impact = sa.calculate_yield_impact("Moderate", "Tomato")
    assert 0 < impact <= 80


def test_get_severity_description():
    sa = SeverityAnalyzer()
    desc = sa.get_severity_description("Moderate")
    assert isinstance(desc, str)
    assert len(desc) > 10


if __name__ == "__main__":
    test_analyze_healthy()
    test_analyze_mild()
    test_analyze_moderate()
    test_analyze_severe()
    test_get_severity_meter_value()
    test_get_treatment_urgency()
    test_calculate_yield_impact()
    test_get_severity_description()
    print("All severity analyzer tests passed!")
