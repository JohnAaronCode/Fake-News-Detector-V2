# model.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class FakeNewsDetector:
    def __init__(self):
        self.model_path = "fake_news_model.pkl"
        self.vectorizer_path = "tfidf_vectorizer.pkl"
        self.model = None
        self.vectorizer = None
        self.load_model()

    def train(self):
        # Example dataset (you can replace this with your own)
        data = {
            "text": [
                "The government announced a new policy to support farmers.",
                "Aliens have landed on Earth according to secret NASA documents!",
                "Scientists discovered a cure for cancer after decades of research.",
                "A man claims to have seen a dragon flying over the city.",
                "The president met with world leaders to discuss global economy.",
                "Fake website reports celebrity died, but they are alive."
            ],
            "label": [1, 0, 1, 0, 1, 0]  # 1 = Real, 0 = Fake
        }

        df = pd.DataFrame(data)

        X_train, X_test, y_train, y_test = train_test_split(
            df['text'], df['label'], test_size=0.2, random_state=42
        )

        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        X_train_tfidf = self.vectorizer.fit_transform(X_train)

        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X_train_tfidf, y_train)

        # Save model and vectorizer
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        print("✅ Model trained and saved successfully.")

    def load_model(self):
        try:
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
        except:
            print("⚠️ Model not found. Please train first by calling train().")

    def predict(self, text):
        if not self.model or not self.vectorizer:
            return None, 0.0

        features = self.vectorizer.transform([text])
        prediction = self.model.predict(features)[0]
        confidence = max(self.model.predict_proba(features)[0])
        return prediction, confidence
