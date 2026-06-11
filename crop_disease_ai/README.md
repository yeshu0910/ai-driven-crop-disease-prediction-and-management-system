# 🌱 AI-Driven Crop Disease Prediction & Management System

A production-ready AgriTech web application that detects crop diseases from leaf images using deep learning, analyzes disease severity, provides treatment recommendations, monitors weather conditions, predicts future disease risks, and generates downloadable PDF reports.

## 🚀 Features

- **AI Disease Detection** - CNN-based classification of 60+ diseases across 15 crops
- **Multi-Crop Support** - Tomato, Potato, Rice, Wheat, Corn, Cotton, Soybean, Sugarcane, Groundnut, Sunflower, Banana, Mango, Grapes, Apple, Chili
- **Severity Analysis** - Healthy/Mild/Moderate/Severe with infection percentage
- **Smart Treatment Engine** - Chemical & organic recommendations based on disease, severity, and weather
- **Weather Intelligence** - Real-time weather, 7-day forecasts, disease risk prediction
- **Analytics Dashboard** - Interactive Plotly charts for disease trends and crop health
- **Disease Knowledge Base** - Comprehensive info on symptoms, causes, prevention, treatment
- **PDF Reports** - Downloadable diagnostic reports with images and analysis
- **Explainable AI** - Confidence analysis, heatmaps, and model interpretation
- **Database System** - SQLite for predictions, weather logs, analytics

## 📋 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core language |
| Streamlit | Web framework |
| TensorFlow/Keras | Deep learning |
| OpenCV | Image processing |
| Scikit-learn | ML evaluation |
| Plotly | Interactive charts |
| SQLite | Database |
| OpenWeather API | Weather data |
| ReportLab | PDF generation |
| Docker | Containerization |

## 🛠️ Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd crop_disease_ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenWeather API key

# Train the model (optional - fallback mode works without training)
python training/train_model.py
```

## 🚀 Running

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t crop-disease-ai .

# Run the container
docker run -p 8501:8501 -e OPENWEATHER_API_KEY=your_key crop-disease-ai
```

## ☁️ Cloud Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect repo at share.streamlit.io
3. Set `OPENWEATHER_API_KEY` in Secrets
4. Deploy

### Render
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `streamlit run app.py --server.port $PORT`
4. Add environment variables

### Railway
1. Connect repo
2. Add `OPENWEATHER_API_KEY` to environment variables
3. Deploy

## 📁 Project Structure

```
crop_disease_ai/
├── app.py                 # Main Streamlit application
├── assets/
│   └── style.css          # Custom CSS styling
├── database/
│   ├── __init__.py
│   └── db_manager.py      # SQLite database operations
├── models/                # Trained model files
├── pages/
│   ├── 1_Home.py          # Home/dashboard page
│   ├── 2_Detection.py     # Disease detection page
│   ├── 3_Analytics.py     # Analytics dashboard
│   ├── 4_Knowledge_Base.py # Disease knowledge base
│   ├── 5_Weather.py       # Weather intelligence
│   ├── 6_History.py       # Detection history
│   └── 7_About.py         # About page
├── utils/
│   ├── config.py          # Configuration constants
│   ├── image_processor.py # OpenCV image processing
│   ├── model_handler.py   # TensorFlow model handling
│   ├── weather_api.py     # Weather API integration
│   ├── severity_analyzer.py # Severity analysis
│   ├── disease_knowledge_base.py # Disease database
│   ├── recommendation_engine.py # Treatment recommendations
│   ├── explainable_ai.py  # AI explainability
│   ├── risk_predictor.py  # Disease risk prediction
│   └── pdf_generator.py   # PDF report generation
├── training/
│   ├── train_model.py     # Model training script
│   └── evaluate_model.py  # Model evaluation
├── reports/               # Generated PDF reports
├── data/                  # Training data
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Configuration

### OpenWeather API
1. Sign up at https://openweathermap.org/api
2. Get your free API key
3. Add to `.env`: `OPENWEATHER_API_KEY=your_key`

### Model Training
The system includes a dummy model for testing. For production use:
1. Download PlantVillage dataset
2. Place in `data/train/` and `data/val/`
3. Run `python training/train_model.py`

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| OPENWEATHER_API_KEY | No (mock data used if missing) | OpenWeather API key |
| APP_NAME | No | Application name |
| DEBUG | No | Debug mode |

## 🎯 Supported Diseases

60+ diseases across 15 crops including:
- Tomato: Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus
- Potato: Early Blight, Late Blight
- Rice: Brown Spot, Leaf Blast, Neck Blast
- Wheat: Brown Rust, Yellow Rust, Septoria
- Corn: Cercospora Leaf Spot, Common Rust, Northern Leaf Blight
- Cotton: Bacterial Blight, Leaf Curl
- Soybean, Sugarcane, Groundnut, Sunflower, Banana, Mango, Grapes, Apple, Chili

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This system is designed as a decision-support tool. Always consult with certified agricultural experts for final diagnosis and treatment decisions. The AI model's predictions should be verified through clinical testing.
