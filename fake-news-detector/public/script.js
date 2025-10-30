const newsInput = document.getElementById('newsInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultContainer = document.getElementById('resultContainer');
const resultCard = document.getElementById('resultCard');
const loadingSpinner = document.getElementById('loadingSpinner');
const themeToggle = document.getElementById('themeToggle');
const correctBtn = document.getElementById('correctBtn');
const incorrectBtn = document.getElementById('incorrectBtn');

// Use relative URL for production, localhost for development
const API_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:5000' 
  : '';

// Theme toggle
themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
  localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
  themeToggle.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
});

// Load saved theme
if (localStorage.getItem('theme') === 'dark') {
  document.body.classList.add('dark-mode');
  themeToggle.textContent = '☀️';
}

// Analyze button
analyzeBtn.addEventListener('click', analyzeNews);

function analyzeNews() {
  const content = newsInput.value.trim();

  if (!content) {
    alert('Please enter news content to analyze.');
    return;
  }

  // 🔍 Detect meaningless or random input
  if (isInvalidInput(content)) {
    alert('Please enter meaningful news content (not random letters or numbers).');
    return;
  }

  analyzeBtn.disabled = true;
  loadingSpinner.classList.remove('hidden');
  resultContainer.classList.add('hidden');

  fetch(`${API_URL}/api/analyze_ai`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: content }),
  })
    .then((res) => res.json())
    .then((data) => {
      displayResult(data);
    })
    .catch((err) => {
      console.error('Error:', err);
      
      // Fallback to regular analyze if AI endpoint fails
      fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: content }),
      })
        .then((res) => res.json())
        .then((data) => displayResult(data))
        .catch(() => alert('Error analyzing content. Make sure the backend is running.'));
    })
    .finally(() => {
      analyzeBtn.disabled = false;
      loadingSpinner.classList.add('hidden');
    });
}

// ✅ Detects random or nonsense input
function isInvalidInput(text) {
  const tooManyNumbers = text.replace(/[^0-9]/g, '').length / text.length > 0.4;
  const tooManySymbols = text.replace(/[A-Za-z0-9\s]/g, '').length / text.length > 0.3;
  const words = text.split(/\s+/);
  const isTooShort = text.length < 30 || words.length < 5;
  const mostlyConsonants = words.filter(w => w.match(/[aeiouAEIOU]/)).length / words.length < 0.3;
  return tooManyNumbers || tooManySymbols || isTooShort || mostlyConsonants;
}

// 🧾 Display the analysis result
function displayResult(data) {
    const isFake = data.prediction === 'FAKE';
    const isAI = data.ai_powered || false;
    const warnings = data.warning_signs || [];
    const modelType = data.model_type || 'Standard';
    const links = data.links || [];
    const linkSummary = data.link_summary || null;

    resultCard.classList.remove('real', 'fake');
    resultCard.classList.add(isFake ? 'fake' : 'real');

    // Modern + professional centered result with AI insights
    let warningsHTML = '';
    if (warnings.length > 0) {
        warningsHTML = `
            <div style="margin-top: 15px; padding: 10px; background: rgba(255,193,7,0.1); border-radius: 8px;">
                <h4 style="margin: 0 0 8px 0; font-size: 0.9rem; color: #ff9800;">⚠️ Warning Signs Detected:</h4>
                <ul style="margin: 0; padding-left: 20px; font-size: 0.85rem; text-align: left;">
                    ${warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Links section
    let linksHTML = '';
    if (links.length > 0) {
        const getCredibilityIcon = (cred) => {
            if (cred === 'trusted') return '✅';
            if (cred === 'suspicious') return '⚠️';
            return '🔗';
        };
        
        const getCredibilityColor = (cred) => {
            if (cred === 'trusted') return '#4caf50';
            if (cred === 'suspicious') return '#ff9800';
            return '#2196f3';
        };

        linksHTML = `
            <div style="margin-top: 15px; padding: 12px; background: rgba(33,150,243,0.05); border-radius: 8px; border-left: 3px solid #2196f3;">
                <h4 style="margin: 0 0 10px 0; font-size: 0.9rem; color: #2196f3;">
                    🔗 Related Links (${links.length})
                </h4>
                ${linkSummary ? `
                    <div style="font-size: 0.75rem; margin-bottom: 10px; opacity: 0.8;">
                        <span style="color: #4caf50;">✅ Trusted: ${linkSummary.trusted}</span> | 
                        <span style="color: #ff9800;">⚠️ Suspicious: ${linkSummary.suspicious}</span> | 
                        <span style="color: #2196f3;">🔗 Unknown: ${linkSummary.unknown}</span>
                    </div>
                ` : ''}
                <div style="max-height: 200px; overflow-y: auto; text-align: left;">
                    ${links.map(link => `
                        <div style="margin: 8px 0; padding: 8px; background: rgba(255,255,255,0.5); border-radius: 4px; font-size: 0.8rem;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                <span style="font-size: 1.2rem;">${getCredibilityIcon(link.credibility)}</span>
                                <span style="font-weight: 600; color: ${getCredibilityColor(link.credibility)};">
                                    ${link.domain}
                                </span>
                            </div>
                            <a href="${link.url}" target="_blank" rel="noopener noreferrer" 
                               style="color: #1976d2; text-decoration: none; word-break: break-all; font-size: 0.75rem;">
                                ${link.url}
                            </a>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } else {
        linksHTML = `
            <div style="margin-top: 15px; padding: 10px; background: rgba(158,158,158,0.05); border-radius: 8px;">
                <p style="margin: 0; font-size: 0.85rem; opacity: 0.7;">
                    📝 No links found in the article
                </p>
            </div>
        `;
    }

    resultCard.innerHTML = `
        <div style="text-align:center; padding: 10px;">
            <h2 style="font-size:2rem; font-weight:700; margin-bottom:6px;">
                ${isFake ? '🚨 FAKE' : '✅ REAL'}
            </h2>
            <p style="font-size: 0.9rem; opacity: 0.8; margin: 5px 0;">
                Confidence: ${(data.confidence * 100).toFixed(1)}%
            </p>
            ${isAI ? `
                <div style="margin-top: 10px; padding: 8px; background: rgba(76,175,80,0.1); border-radius: 8px;">
                    <span style="font-size: 0.85rem; color: #4caf50;">
                        🤖 AI-Enhanced Analysis
                    </span>
                    <p style="font-size: 0.75rem; margin: 4px 0 0 0; opacity: 0.7;">
                        ${modelType}
                    </p>
                </div>
            ` : ''}
            ${warningsHTML}
            ${linksHTML}
        </div>
    `;

    resultContainer.classList.remove('hidden');
}

// Feedback buttons
correctBtn.addEventListener('click', () => {
  alert('Thank you for the feedback!');
  correctBtn.disabled = true;
  incorrectBtn.disabled = true;
});

incorrectBtn.addEventListener('click', () => {
  alert('We appreciate your honesty. This helps improve our system.');
  correctBtn.disabled = true;
  incorrectBtn.disabled = true;
});

// Ctrl+Enter shortcut
newsInput.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'Enter') analyzeNews();
});
