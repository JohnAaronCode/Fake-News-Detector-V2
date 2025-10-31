# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import FakeNewsDetector

app = Flask(__name__)
CORS(app)

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

    is_fake = prediction == 0
    confidence_percentage = round(confidence * 100, 1)

    if is_fake:
        result = {
            "prediction": "FAKE",
            "confidence": confidence_percentage,
            "title": "Likely Misinformation",
            "message": "This content appears to be false or misleading",
            "type": "fake",
            "sources": [
                {
                    "title": "Fact Check: The Real Story Behind This Claim",
                    "source": "Snopes",
                    "description": "This claim has been debunked by multiple fact-checking organizations. The actual events occurred differently..."
                },
                {
                    "title": "What Actually Happened: Full Report",
                    "source": "FactCheck.org",
                    "description": "According to official sources and verified reports, the true version of events is..."
                }
            ],
            "warning": "This content may spread misinformation. Please verify with trusted sources before sharing."
        }
    else:
        result = {
            "prediction": "REAL",
            "confidence": confidence_percentage,
            "title": "Verified as Real",
            "message": "This news appears to be authentic",
            "type": "real",
            "sources": [
                {
                    "title": "Reuters - Breaking News",
                    "source": "Reuters",
                    "date": "2025-10-28"
                },
                {
                    "title": "Associated Press",
                    "source": "Associated Press",
                    "date": "2025-10-28"
                },
                {
                    "title": "BBC News",
                    "source": "BBC News",
                    "date": "2025-10-27"
                }
            ],
            "warning": None
        }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
