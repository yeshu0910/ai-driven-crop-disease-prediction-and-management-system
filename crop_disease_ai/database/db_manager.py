import sqlite3
import json
from datetime import datetime, date
from pathlib import Path
from utils.config import DB_PATH


class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS farmers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                location TEXT,
                farm_size REAL,
                crops_grown TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER,
                image_path TEXT,
                crop_name TEXT NOT NULL,
                disease_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                severity TEXT,
                infection_percentage REAL,
                risk_level TEXT,
                weather_data TEXT,
                treatment_recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farmer_id) REFERENCES farmers(id)
            );

            CREATE TABLE IF NOT EXISTS weather_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                wind_speed REAL,
                weather_description TEXT,
                rainfall REAL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS disease_risk_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_name TEXT NOT NULL,
                disease_name TEXT,
                risk_level TEXT NOT NULL,
                risk_score REAL,
                forecast_date DATE NOT NULL,
                weather_conditions TEXT,
                suggestions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_scans INTEGER DEFAULT 0,
                healthy_scans INTEGER DEFAULT 0,
                diseased_scans INTEGER DEFAULT 0,
                date DATE UNIQUE,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER,
                was_correct INTEGER,
                actual_disease TEXT,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id)
            );

            CREATE INDEX IF NOT EXISTS idx_predictions_crop ON predictions(crop_name);
            CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at);
            CREATE INDEX IF NOT EXISTS idx_weather_logged ON weather_logs(logged_at);
        """)

        conn.commit()
        conn.close()

    def add_farmer(self, name, phone=None, email=None, location=None,
                   farm_size=None, crops_grown=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO farmers (name, phone, email, location, farm_size, crops_grown)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, email, location, farm_size, crops_grown))
        conn.commit()
        farmer_id = cursor.lastrowid
        conn.close()
        return farmer_id

    def get_farmer(self, farmer_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmers WHERE id = ?", (farmer_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_all_farmers(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmers ORDER BY created_at DESC")
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def save_prediction(self, farmer_id, image_path, crop_name, disease_name,
                        confidence, severity=None, infection_percentage=None,
                        risk_level=None, weather_data=None,
                        treatment_recommendations=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions
            (farmer_id, image_path, crop_name, disease_name, confidence,
             severity, infection_percentage, risk_level, weather_data,
             treatment_recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (farmer_id, image_path, crop_name, disease_name, confidence,
              severity, infection_percentage, risk_level,
              json.dumps(weather_data) if weather_data else None,
              json.dumps(treatment_recommendations) if treatment_recommendations else None))
        conn.commit()
        pred_id = cursor.lastrowid
        conn.close()
        self._update_analytics(disease_name)
        return pred_id

    def get_prediction(self, pred_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE id = ?", (pred_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            d = dict(result)
            if d.get("weather_data"):
                try:
                    d["weather_data"] = json.loads(d["weather_data"])
                except (json.JSONDecodeError, TypeError):
                    pass
            if d.get("treatment_recommendations"):
                try:
                    d["treatment_recommendations"] = json.loads(
                        d["treatment_recommendations"])
                except (json.JSONDecodeError, TypeError):
                    pass
            return d
        return None

    def get_all_predictions(self, limit=100):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, f.name as farmer_name
            FROM predictions p
            LEFT JOIN farmers f ON p.farmer_id = f.id
            ORDER BY p.created_at DESC LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def get_predictions_by_crop(self, crop_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, f.name as farmer_name
            FROM predictions p
            LEFT JOIN farmers f ON p.farmer_id = f.id
            WHERE p.crop_name = ?
            ORDER BY p.created_at DESC
        """, (crop_name,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def log_weather(self, location, temperature=None, humidity=None,
                    pressure=None, wind_speed=None,
                    weather_description=None, rainfall=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO weather_logs
            (location, temperature, humidity, pressure, wind_speed,
             weather_description, rainfall)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (location, temperature, humidity, pressure, wind_speed,
              weather_description, rainfall))
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        return log_id

    def get_weather_logs(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM weather_logs
            ORDER BY logged_at DESC LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def save_risk_prediction(self, crop_name, disease_name, risk_level,
                             risk_score, forecast_date, weather_conditions,
                             suggestions):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO disease_risk_predictions
            (crop_name, disease_name, risk_level, risk_score,
             forecast_date, weather_conditions, suggestions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (crop_name, disease_name, risk_level, risk_score,
              forecast_date.isoformat() if isinstance(forecast_date, date) else forecast_date,
              json.dumps(weather_conditions),
              json.dumps(suggestions) if suggestions else None))
        conn.commit()
        risk_id = cursor.lastrowid
        conn.close()
        return risk_id

    def get_risk_predictions(self, crop_name=None, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        if crop_name:
            cursor.execute("""
                SELECT * FROM disease_risk_predictions
                WHERE crop_name = ?
                ORDER BY forecast_date DESC LIMIT ?
            """, (crop_name, limit))
        else:
            cursor.execute("""
                SELECT * FROM disease_risk_predictions
                ORDER BY forecast_date DESC LIMIT ?
            """, (limit,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def _update_analytics(self, disease_name):
        today = date.today().isoformat()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analytics WHERE date = ?", (today,))
        existing = cursor.fetchone()
        if existing:
            is_healthy = 1 if "healthy" in disease_name.lower() else 0
            cursor.execute("""
                UPDATE analytics
                SET total_scans = total_scans + 1,
                    healthy_scans = healthy_scans + ?,
                    diseased_scans = diseased_scans + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE date = ?
            """, (is_healthy, 1 - is_healthy, today))
        else:
            is_healthy = 1 if "healthy" in disease_name.lower() else 0
            cursor.execute("""
                INSERT INTO analytics (date, total_scans, healthy_scans, diseased_scans)
                VALUES (?, 1, ?, ?)
            """, (today, is_healthy, 1 - is_healthy))
        conn.commit()
        conn.close()

    def get_analytics(self, days=30):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM analytics
            WHERE date >= date('now', '-? days')
            ORDER BY date ASC
        """, (days,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def get_disease_frequency(self, limit=20):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT disease_name, COUNT(*) as count
            FROM predictions
            GROUP BY disease_name
            ORDER BY count DESC LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def get_monthly_trends(self, months=6):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%Y-%m', created_at) as month,
                   COUNT(*) as total,
                   SUM(CASE WHEN disease_name LIKE '%healthy%' THEN 1 ELSE 0 END) as healthy,
                   SUM(CASE WHEN disease_name NOT LIKE '%healthy%' THEN 1 ELSE 0 END) as diseased
            FROM predictions
            WHERE created_at >= date('now', '-? months')
            GROUP BY month
            ORDER BY month ASC
        """, (months,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def get_summary_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM predictions")
        total_scans = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT COUNT(*) as total FROM predictions
            WHERE disease_name LIKE '%healthy%'
        """)
        healthy_scans = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(DISTINCT crop_name) as total FROM predictions")
        total_crops = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT disease_name, COUNT(*) as cnt
            FROM predictions
            WHERE disease_name NOT LIKE '%healthy%'
            GROUP BY disease_name
            ORDER BY cnt DESC LIMIT 1
        """)
        common_disease_row = cursor.fetchone()
        common_disease = dict(common_disease_row) if common_disease_row else None
        conn.close()
        return {
            "total_scans": total_scans,
            "healthy_scans": healthy_scans,
            "diseased_scans": total_scans - healthy_scans,
            "total_crops": total_crops,
            "most_common_disease": common_disease["disease_name"] if common_disease else "N/A",
            "most_common_count": common_disease["cnt"] if common_disease else 0
        }

    def save_feedback(self, prediction_id, was_correct, actual_disease=None,
                      comments=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (prediction_id, was_correct, actual_disease, comments)
            VALUES (?, ?, ?, ?)
        """, (prediction_id, 1 if was_correct else 0, actual_disease, comments))
        conn.commit()
        fb_id = cursor.lastrowid
        conn.close()
        return fb_id
