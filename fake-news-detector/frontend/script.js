const newsInput = document.getElementById('newsInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultContainer = document.getElementById('resultContainer');
const resultCard = document.getElementById('resultCard');
const loadingSpinner = document.getElementById('loadingSpinner');
const themeToggle = document.getElementById('themeToggle');
const correctBtn = document.getElementById('correctBtn');
const incorrectBtn = document.getElementById('incorrectBtn');

const API_URL = 'http://localhost:5000';

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

  fetch(`${API_URL}/analyze`, {
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
      alert('Error analyzing content. Make sure the backend is running.');
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

    resultCard.classList.remove('real', 'fake');
    resultCard.classList.add(isFake ? 'fake' : 'real');

    // Modern + professional centered result
    resultCard.innerHTML = `
        <div style="text-align:center; padding: 10px;">
            <h2 style="font-size:2rem; font-weight:700; margin-bottom:6px;">
                ${isFake ? 'FAKE' : 'REAL'}
            </h2>
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
