
from pathlib import Path
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "models"

PERFORMANCE_MODEL_FILE = MODEL_DIR / "performance_model.pkl"

# Load the trained performance model
performance_model = joblib.load(PERFORMANCE_MODEL_FILE)


def predict_performance(data):
    prediction = performance_model.predict(data)
    return float(prediction[0])
