# ClarifAI - Fake News Detector

AI-powered fake news detection system developed by John Aaron Tumangan.

## 🚀 Deployment to Vercel

### Prerequisites
- A Vercel account (sign up at https://vercel.com)
- Git installed on your machine
- Your project in a Git repository

### Deployment Steps

#### Option 1: Deploy via Vercel CLI
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Navigate to your project directory:
   ```bash
   cd "c:\Users\Tanya Grace\Desktop\Fake-News-Detector\fake-news-detector"
   ```

3. Login to Vercel:
   ```bash
   vercel login
   ```

4. Deploy:
   ```bash
   vercel --prod
   ```

#### Option 2: Deploy via Vercel Dashboard
1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. Go to https://vercel.com/dashboard
3. Click "Import Project"
4. Import your GitHub repository
5. Vercel will auto-detect the configuration from `vercel.json`
6. Click "Deploy"

### Project Structure
```
fake-news-detector/
├── api/                    # Serverless functions
│   ├── index.py           # Main API endpoint
│   ├── model.py           # ML model class
│   ├── requirements.txt   # Python dependencies
│   ├── fake_news_model.pkl
│   └── tfidf_vectorizer.pkl
├── frontend/              # Static frontend files
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── backend/               # Local development backend
│   └── ...
├── vercel.json           # Vercel configuration
├── .vercelignore         # Files to exclude from deployment
├── .gitignore           # Git ignore file
└── package.json         # Project metadata
```

### Configuration Files

#### vercel.json
- Configures Python serverless functions
- Routes `/api/*` to the Python backend
- Serves frontend files from `/frontend` directory

#### .vercelignore
- Excludes unnecessary files from deployment (pycache, csv data files, etc.)

### Environment Variables
If you need to add environment variables:
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add your variables

### Local Development
```bash
# Backend (Flask)
cd backend
pip install -r requirements.txt
python app.py

# Frontend
# Just open frontend/index.html in a browser
# Or use a simple server:
python -m http.server 8000
```

### Post-Deployment
- Your app will be available at `https://your-project-name.vercel.app`
- The API endpoints will be at `https://your-project-name.vercel.app/api/*`
- The frontend automatically detects production vs local environment

## 📝 Features
- Real-time fake news detection
- AI-powered analysis using Logistic Regression
- TF-IDF text vectorization
- Clean, modern UI with dark mode
- Responsive design

## 🛠️ Technologies
- **Backend**: Flask, scikit-learn, pandas
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Vercel Serverless Functions
- **ML**: Logistic Regression, TF-IDF

## 📄 License
MIT License - Created by John Aaron Tumangan

---
For issues or questions, please check the Vercel deployment logs in your dashboard.
