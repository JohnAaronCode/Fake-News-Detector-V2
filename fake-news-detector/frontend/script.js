const newsInput = document.getElementById("newsInput")
const analyzeBtn = document.getElementById("analyzeBtn")
const resultContainer = document.getElementById("resultContainer")
const loadingSpinner = document.getElementById("loadingSpinner")
const themeToggle = document.getElementById("themeToggle")
const correctBtn = document.getElementById("correctBtn")
const incorrectBtn = document.getElementById("incorrectBtn")

// Use relative URL for production, localhost for development
const API_URL = window.location.hostname === "localhost" ? "http://localhost:5000" : ""

// Theme toggle
themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode")
  localStorage.setItem("theme", document.body.classList.contains("dark-mode") ? "dark" : "light")
  themeToggle.textContent = document.body.classList.contains("dark-mode") ? "☀️" : "🌙"
})

// Load saved theme
if (localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark-mode")
  themeToggle.textContent = "☀️"
}

// Analyze button
analyzeBtn.addEventListener("click", analyzeNews)

function analyzeNews() {
  const content = newsInput.value.trim()

  if (!content) {
    alert("Please enter news content to analyze.")
    return
  }

  if (isInvalidInput(content)) {
    alert("Please enter meaningful news content (not random letters or numbers).")
    return
  }

  analyzeBtn.disabled = true
  loadingSpinner.classList.remove("hidden")
  resultContainer.classList.add("hidden")

  fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: content }),
  })
    .then((res) => res.json())
    .then((data) => {
      displayResult(data)
    })
    .catch((err) => {
      console.error("Error:", err)
      alert("Error analyzing content. Make sure the backend is running.")
    })
    .finally(() => {
      analyzeBtn.disabled = false
      loadingSpinner.classList.add("hidden")
    })
}

function isInvalidInput(text) {
  const tooManyNumbers = text.replace(/[^0-9]/g, "").length / text.length > 0.4
  const tooManySymbols = text.replace(/[A-Za-z0-9\s]/g, "").length / text.length > 0.3
  const words = text.split(/\s+/)
  const isTooShort = text.length < 30 || words.length < 5
  const mostlyConsonants = words.filter((w) => w.match(/[aeiouAEIOU]/)).length / words.length < 0.3
  return tooManyNumbers || tooManySymbols || isTooShort || mostlyConsonants
}

function displayResult(data) {
  const isFake = data.type === "fake"
  const statusHeader = document.getElementById("statusHeader")
  const confidenceBar = document.getElementById("confidenceBar")
  const confidenceValue = document.getElementById("confidenceValue")
  const sourcesSection = document.getElementById("sourcesSection")
  const warningSection = document.getElementById("warningSection")
  const actionButtonContainer = document.getElementById("actionButtonContainer")

  // Display status header
  if (isFake) {
    statusHeader.className = "status-header fake"
    statusHeader.innerHTML = `
      <div class="status-icon">✕</div>
      <div class="status-text">
        <h2>Likely Misinformation</h2>
        <p>This content appears to be false or misleading</p>
      </div>
    `
    confidenceBar.style.width = data.confidence + "%"
    confidenceBar.className = "confidence-bar fake"
  } else {
    statusHeader.className = "status-header real"
    statusHeader.innerHTML = `
      <div class="status-icon">✓</div>
      <div class="status-text">
        <h2>Verified as Real</h2>
        <p>This news appears to be authentic</p>
      </div>
    `
    confidenceBar.style.width = data.confidence + "%"
    confidenceBar.className = "confidence-bar real"
  }

  confidenceValue.textContent = data.confidence + "%"

  // Display sources
  if (isFake) {
    sourcesSection.innerHTML = `
      <h3 class="sources-title">🔴 What's Actually True</h3>
      <div class="sources-list">
        ${data.sources
          .map(
            (source, index) => `
          <div class="source-card">
            <div class="source-header">
              <span class="source-initial">${source.source.charAt(0)}</span>
              <div class="source-info">
                <h4>${source.title}</h4>
                <p class="source-name">${source.source}</p>
              </div>
              <a href="#" class="source-link">⤴</a>
            </div>
            <p class="source-description">${source.description}</p>
          </div>
        `,
          )
          .join("")}
      </div>
    `

    // Display warning
    warningSection.className = "warning-section"
    warningSection.innerHTML = `
      <p><strong>Warning:</strong> ${data.warning}</p>
    `

    // Display action button
    actionButtonContainer.innerHTML = `
      <button class="action-btn read-report">Read Fact-Check Reports</button>
    `
  } else {
    sourcesSection.innerHTML = `
      <h3 class="sources-title">📋 Verified Sources</h3>
      <div class="sources-list">
        ${data.sources
          .map(
            (source, index) => `
          <div class="source-card">
            <div class="source-header">
              <span class="source-initial">${source.source.charAt(0)}</span>
              <div class="source-info">
                <h4>${source.title}</h4>
                <p class="source-name">${source.source}</p>
              </div>
              <span class="source-date">${source.date}</span>
              <a href="#" class="source-link">⤴</a>
            </div>
          </div>
        `,
          )
          .join("")}
      </div>
    `

    warningSection.classList.add("hidden")

    // Display action button
    actionButtonContainer.innerHTML = `
      <button class="action-btn learn-more">Learn More About These Sources</button>
    `
  }

  resultContainer.classList.remove("hidden")
  resetFeedbackButtons()
}

function resetFeedbackButtons() {
  correctBtn.disabled = false
  incorrectBtn.disabled = false
}

// Feedback buttons
correctBtn.addEventListener("click", () => {
  alert("Thank you for the feedback!")
  correctBtn.disabled = true
  incorrectBtn.disabled = true
})

incorrectBtn.addEventListener("click", () => {
  alert("We appreciate your honesty. This helps improve our system.")
  correctBtn.disabled = true
  incorrectBtn.disabled = true
})

// Ctrl+Enter shortcut
newsInput.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key === "Enter") analyzeNews()
})
