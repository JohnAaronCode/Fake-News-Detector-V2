import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from model import FakeNewsDetector

print("🔄 Starting model training...")
detector = FakeNewsDetector()
detector.train()
print("✅ Model training complete!")
print("📊 Model saved to api/fake_news_model.pkl")
print("📊 Vectorizer saved to api/tfidf_vectorizer.pkl")
