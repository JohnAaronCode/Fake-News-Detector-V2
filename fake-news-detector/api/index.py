from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from model import FakeNewsDetector

app = Flask(__name__)
CORS(app)

# Initialize detector globally
detector = FakeNewsDetector()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Fake News Detector API running'})

@app.route('/train', methods=['POST'])
def train_model():
    detector.train()
    return jsonify({'message': 'Model retrained successfully'})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    prediction, confidence = detector.predict(text)

    if prediction is None:
        return jsonify({'error': 'Model not loaded'}), 500

    result = {
        "prediction": "FAKE" if prediction == 0 else "REAL",
        "confidence": round(confidence, 2)
    }

    return jsonify(result)

# Vercel serverless handler
app = app
