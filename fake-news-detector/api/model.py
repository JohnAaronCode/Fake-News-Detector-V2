# model.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

class FakeNewsDetector:
    def __init__(self):
        # Update paths for Vercel deployment
        base_dir = os.path.dirname(__file__)
        self.model_path = os.path.join(base_dir, "fake_news_model.pkl")
        self.vectorizer_path = os.path.join(base_dir, "tfidf_vectorizer.pkl")
        self.model = None
        self.vectorizer = None
        self.load_model()

    def train(self):
        # Load real datasets from CSV files
        try:
            base_dir = os.path.dirname(__file__)
            
            # Try multiple paths to find the data files
            possible_paths = [
                (os.path.join(base_dir, 'data', 'fake.csv'), os.path.join(base_dir, 'data', 'true.csv')),
                (os.path.join(base_dir, '..', 'backend', 'data', 'fake.csv'), os.path.join(base_dir, '..', 'backend', 'data', 'true.csv')),
            ]
            
            fake_path = None
            true_path = None
            
            for fp, tp in possible_paths:
                if os.path.exists(fp) and os.path.exists(tp):
                    fake_path = fp
                    true_path = tp
                    break
            
            # If files don't exist, use fallback sample data
            if not fake_path or not true_path:
                print("CSV files not found, using sample data")
                fake_df = pd.DataFrame({
                    'text': [
                        "Aliens have landed on Earth according to secret NASA documents!",
                        "You won't believe this one weird trick that doctors hate!",
                        "The government is hiding a cure for cancer!",
                        "Celebrities are secretly lizard people!",
                        "5G towers are spreading the virus!"
                    ]
                })
                true_df = pd.DataFrame({
                    'text': [
                        "The government announced a new policy to support farmers.",
                        "Scientists published research findings on climate change.",
                        "The president met with world leaders to discuss economy.",
                        "Stock markets showed mixed results today.",
                        "Congress passed a new infrastructure bill."
                    ]
                })
            else:
                print("Loading real datasets from CSV files...")
                # Load the CSV files
                fake_df = pd.read_csv(fake_path)
                true_df = pd.read_csv(true_path)
                
                # Use only the 'text' column and sample 500 from each for performance
                fake_df = fake_df[['text']].sample(n=min(500, len(fake_df)), random_state=42)
                true_df = true_df[['text']].sample(n=min(500, len(true_df)), random_state=42)
                
                print(f"Loaded {len(fake_df)} fake news articles")
                print(f"Loaded {len(true_df)} true news articles")
            
            # Add labels
            fake_df['label'] = 0  # Fake
            true_df['label'] = 1  # Real
            
            # Combine datasets
            df = pd.concat([fake_df, true_df], ignore_index=True)
            
            # Shuffle the data
            df = df.sample(frac=1, random_state=42).reset_index(drop=True)
            
            print(f"Total training samples: {len(df)}")
            
        except Exception as e:
            print(f"Error loading CSV files: {e}")
            print("Using minimal fallback data")
            # Fallback to minimal sample data
            df = pd.DataFrame({
                'text': [
                    "The government announced a new policy to support farmers.",
                    "Aliens have landed on Earth according to secret NASA documents!",
                    "Scientists discovered a cure for cancer after decades of research.",
                    "A man claims to have seen a dragon flying over the city.",
                ],
                'label': [1, 0, 1, 0]
            })

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
        print("Model trained and saved successfully.")

    def load_model(self):
        try:
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
        except:
            print("Model not found. Please train first by calling train().")

    def predict(self, text):
        if not self.model or not self.vectorizer:
            return None, 0.0

        features = self.vectorizer.transform([text])
        prediction = self.model.predict(features)[0]
        confidence = max(self.model.predict_proba(features)[0])
        return prediction, confidence
