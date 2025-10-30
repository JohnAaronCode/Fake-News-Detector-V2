from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from model import FakeNewsDetector

# Initialize detector globally
detector = FakeNewsDetector()

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Get text from request
            text = data.get('text', '').strip()
            
            if not text:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'error': 'No text provided'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Make prediction
            prediction, confidence = detector.predict(text)
            
            if prediction is None:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'error': 'Model not loaded'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            result = {
                "prediction": "FAKE" if prediction == 0 else "REAL",
                "confidence": round(confidence, 2)
            }
            
            self.wfile.write(json.dumps(result).encode())
            return
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response).encode())
            return
