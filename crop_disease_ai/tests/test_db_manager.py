import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_db_init():
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    assert db is not None


def test_save_prediction():
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    pred_id = db.save_prediction(
        farmer_id=1,
        image_path="test.jpg",
        crop_name="Tomato",
        disease_name="Tomato Healthy",
        confidence=0.95,
        severity="Healthy",
        infection_percentage=2.5,
        risk_level="None"
    )
    assert pred_id > 0

    pred = db.get_prediction(pred_id)
    assert pred is not None
    assert pred["crop_name"] == "Tomato"
    assert pred["disease_name"] == "Tomato Healthy"


def test_get_summary_stats():
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    stats = db.get_summary_stats()
    assert "total_scans" in stats
    assert "healthy_scans" in stats
    assert "diseased_scans" in stats
    assert "total_crops" in stats
    assert "most_common_disease" in stats


def test_log_weather():
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    log_id = db.log_weather(
        location="Test City",
        temperature=25.5,
        humidity=65.0,
        wind_speed=3.2,
        weather_description="clear sky"
    )
    assert log_id > 0


def test_get_weather_logs():
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    logs = db.get_weather_logs(limit=10)
    assert isinstance(logs, list)


def test_get_all_predictions():
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    predictions = db.get_all_predictions(limit=10)
    assert isinstance(predictions, list)


if __name__ == "__main__":
    test_db_init()
    pid = test_save_prediction()
    test_get_summary_stats()
    test_log_weather()
    test_get_weather_logs()
    test_get_all_predictions()
    print("All database tests passed!")
