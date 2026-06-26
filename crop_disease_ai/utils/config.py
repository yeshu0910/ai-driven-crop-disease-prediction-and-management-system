import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
DATABASE_DIR = BASE_DIR / "database"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
DATA_DIR = BASE_DIR / "data"
TRAINING_DIR = BASE_DIR / "training"

for d in [MODELS_DIR, REPORTS_DIR, DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5"

DB_PATH = DATABASE_DIR / "crop_disease_ai.db"

MODEL_PATH = MODELS_DIR / "plant_disease_model.h5"
CLASS_INDICES_PATH = MODELS_DIR / "class_indices.npy"

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 25
LEARNING_RATE = 0.001
TARGET_ACCURACY = 0.95

CONFIDENCE_THRESHOLD = 0.85
CROP_CONFIDENCE_THRESHOLD = 0.95

SUPPORTED_CROPS = [
    "Tomato",
    "Potato",
    "Rice",
    "Wheat",
    "Corn",
    "Cotton",
    "Soybean",
    "Sugarcane",
    "Groundnut",
    "Sunflower",
    "Banana",
    "Mango",
    "Grapes",
    "Apple",
    "Chili",
]

SEVERITY_LEVELS = {
    "Healthy": {"color": "#2DD4BF", "icon": "✅", "risk": "None"},
    "Mild": {"color": "#FB923C", "icon": "⚠️", "risk": "Low"},
    "Moderate": {"color": "#A78BFA", "icon": "🔶", "risk": "Medium"},
    "Severe": {"color": "#EC4899", "icon": "🔴", "risk": "High"},
}

PRIMARY_COLOR = "#5E6AD2"
SECONDARY_COLOR = "#7C5CBF"
ACCENT_COLOR = "#2DD4BF"
BG_COLOR = "#0A0A0F"
CARD_BG = "#12121A"

DISEASE_CLASSES = {
    "Tomato___Bacterial_spot": "Tomato Bacterial Spot",
    "Tomato___Early_blight": "Tomato Early Blight",
    "Tomato___Late_blight": "Tomato Late Blight",
    "Tomato___Leaf_Mold": "Tomato Leaf Mold",
    "Tomato___Septoria_leaf_spot": "Tomato Septoria Leaf Spot",
    "Tomato___Spider_mites_Two_spotted_spider_mite": "Tomato Spider Mites",
    "Tomato___Target_Spot": "Tomato Target Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato Yellow Leaf Curl Virus",
    "Tomato___Tomato_mosaic_virus": "Tomato Mosaic Virus",
    "Tomato___healthy": "Tomato Healthy",
    "Potato___Early_blight": "Potato Early Blight",
    "Potato___Late_blight": "Potato Late Blight",
    "Potato___healthy": "Potato Healthy",
    "Rice___Brown_spot": "Rice Brown Spot",
    "Rice___Leaf_blast": "Rice Leaf Blast",
    "Rice___Neck_blast": "Rice Neck Blast",
    "Rice___healthy": "Rice Healthy",
    "Wheat___Brown_rust": "Wheat Brown Rust",
    "Wheat___Yellow_rust": "Wheat Yellow Rust",
    "Wheat___Septoria": "Wheat Septoria",
    "Wheat___healthy": "Wheat Healthy",
    "Corn___Cercospora_leaf_spot": "Corn Cercospora Leaf Spot",
    "Corn___Common_rust": "Corn Common Rust",
    "Corn___Northern_Leaf_Blight": "Corn Northern Leaf Blight",
    "Corn___healthy": "Corn Healthy",
    "Cotton___Bacterial_blight": "Cotton Bacterial Blight",
    "Cotton___Leaf_curl": "Cotton Leaf Curl",
    "Cotton___healthy": "Cotton Healthy",
    "Soybean___Bacterial_blight": "Soybean Bacterial Blight",
    "Soybean___Frog_eye_leaf_spot": "Soybean Frog Eye Leaf Spot",
    "Soybean___healthy": "Soybean Healthy",
    "Sugarcane___Red_rot": "Sugarcane Red Rot",
    "Sugarcane___Smut": "Sugarcane Smut",
    "Sugarcane___healthy": "Sugarcane Healthy",
    "Groundnut___Early_leaf_spot": "Groundnut Early Leaf Spot",
    "Groundnut___Late_leaf_spot": "Groundnut Late Leaf Spot",
    "Groundnut___healthy": "Groundnut Healthy",
    "Sunflower___Downy_mildew": "Sunflower Downy Mildew",
    "Sunflower___Leaf_blast": "Sunflower Leaf Blast",
    "Sunflower___healthy": "Sunflower Healthy",
    "Banana___Panama_disease": "Banana Panama Disease",
    "Banana___Black_sigatoka": "Banana Black Sigatoka",
    "Banana___healthy": "Banana Healthy",
    "Mango___Anthracnose": "Mango Anthracnose",
    "Mango___Powdery_mildew": "Mango Powdery Mildew",
    "Mango___healthy": "Mango Healthy",
    "Grapes___Black_rot": "Grapes Black Rot",
    "Grapes___Esca": "Grapes Esca",
    "Grapes___Leaf_blight": "Grapes Leaf Blight",
    "Grapes___healthy": "Grapes Healthy",
    "Apple___Apple_scab": "Apple Apple Scab",
    "Apple___Black_rot": "Apple Black Rot",
    "Apple___Cedar_apple_rust": "Apple Cedar Apple Rust",
    "Apple___healthy": "Apple Healthy",
    "Chili___Leaf_curl": "Chili Leaf Curl",
    "Chili___Bacterial_spot": "Chili Bacterial Spot",
    "Chili___healthy": "Chili Healthy",
}
