const labArea = document.getElementById("labArea");
const explanation = document.getElementById("explanationPanel");
const tabs = document.querySelectorAll(".tab");
const leftPanel = document.getElementById("leftPanel");
const codeAnalyzerModal = document.getElementById("codeAnalyzerModal");
const codeInput = document.getElementById("codeInput");
const languageSelect = document.getElementById("languageSelect");
const resultsContent = document.getElementById("resultsContent");

/* ---------- Utilities ---------- */
function setActiveTab(tabClass) {
    tabs.forEach(tab => tab.classList.remove("active"));
    const activeTab = document.querySelector(`.${tabClass}`);
    if (activeTab) {
        activeTab.classList.add("active");
    }
}

async function analyzePayload(payload) {
    if (!payload) {
        explanation.innerText = "Enter a payload to analyze.";
        return;
    }

    try {
        const lab = document.querySelector(".tab.active").textContent.toLowerCase();
        
        const res = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                payload: payload,
                lab: lab
            })
        });

        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }

        const data = await res.json();
        explanation.innerHTML = data.explanation || "No explanation provided.";

    } catch (err) {
        console.error("Analyzer error:", err);
        explanation.innerText = `Analyzer error: ${err.message}`;
    }
}

/* ---------- CODE ANALYZER FUNCTIONS ---------- */
function openCodeAnalyzer() {
    codeAnalyzerModal.classList.add("active");
    document.body.style.overflow = "hidden";
    
    // Show welcome message
    resultsContent.innerHTML = `
        <div class="welcome-message">
            <h3>Welcome to Static Code Analyzer</h3>
            <p>Enter your code in the left panel and select the programming language.</p>
            <p>The analyzer will check for common input-related vulnerabilities:</p>
            <ul class="vuln-list">
                <li><strong>SQL Injection</strong> - Unsanitized database queries</li>
                <li><strong>Cross-Site Scripting (XSS)</strong> - Unsafe HTML rendering</li>
                <li><strong>Command Injection</strong> - Unsafe system commands</li>
                <li><strong>Eval Injection</strong> - Dangerous eval() usage</li>
                
            </ul>
            <p>Click "Analyze Code" to begin.</p>
        </div>
    `;
}

function closeCodeAnalyzer() {
    codeAnalyzerModal.classList.remove("active");
    document.body.style.overflow = "";
}

function clearCode() {
    codeInput.value = "";
    resultsContent.innerHTML = `
        <div class="welcome-message">
            <h3>Welcome to Static Code Analyzer</h3>
            <p>Enter your code in the left panel and select the programming language.</p>
            <p>The analyzer will check for common input-related vulnerabilities:</p>
            <ul class="vuln-list">
                <li><strong>SQL Injection</strong> - Unsanitized database queries</li>
                <li><strong>Cross-Site Scripting (XSS)</strong> - Unsafe HTML rendering</li>
                <li><strong>Command Injection</strong> - Unsafe system commands</li>
                <li><strong>Eval Injection</strong> - Dangerous eval() usage</li>
            </ul>
            <p>Click "Analyze Code" to begin.</p>
        </div>
    `;
}

async function analyzeCode() {
    const code = codeInput.value.trim();
    const language = languageSelect.value;
    
    if (!code) {
        resultsContent.innerHTML = `
            <div class="vulnerability-report">
                <div class="vuln-header">No Code Entered</div>
                <div style="text-align: center; padding: 20px; color: #ff9966;">
                    Please enter some code to analyze.
                </div>
            </div>
        `;
        return;
    }
    
    // Show loading state
    resultsContent.innerHTML = `
        <div class="welcome-message">
            <h3>Analyzing Code...</h3>
            <p>Checking for vulnerabilities in ${language} code...</p>
            <div style="margin-top: 30px;">
                <div style="width: 100%; height: 4px; background: #333; border-radius: 2px; overflow: hidden;">
                    <div style="width: 60%; height: 100%; background: #967bb6; animation: loading 2s infinite;"></div>
                </div>
            </div>
        </div>
    `;
    
    // Add CSS for loading animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes loading {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(400%); }
        }
    `;
    document.head.appendChild(style);
    
    try {
        // Call backend API for code analysis
        const res = await fetch("http://127.0.0.1:5000/analyze_code", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                code: code,
                language: language
            })
        });

        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }

        const data = await res.json();
        displayCodeAnalysisResults(data);

    } catch (err) {
        console.error("Code analysis error:", err);
        resultsContent.innerHTML = `
            <div class="vulnerability-report">
                <div class="vuln-header">Analysis Error</div>
                <div style="text-align: center; padding: 20px; color: #ff9966;">
                    Error analyzing code: ${err.message}
                    <br><br>
                    Please check if the backend server is running on port 5000.
                </div>
            </div>
        `;
    }
}

function displayCodeAnalysisResults(data) {
    if (!data.vulnerabilities || data.vulnerabilities.length === 0) {
        resultsContent.innerHTML = `
            <div class="vulnerability-report">
                <div class="no-vuln">No Vulnerabilities Found!</div>
                <div style="text-align: center; padding: 20px; color: #99ff99;">
                    Your code appears to be secure against common input-related vulnerabilities.
                    <br><br>
                    <small style="color: #bbb;">Note: This is a basic analysis. Always follow security best practices.</small>
                </div>
            </div>
        `;
        return;
    }

    let html = `
        <div class="vulnerability-report">
            <div class="vuln-header">Your code is vulnerable! The following mistakes were found:</div>
    `;
    
    data.vulnerabilities.forEach(vuln => {
        html += `
            <div class="vuln-item">
                <div class="vuln-line">
                    <span class="line-number">Line ${vuln.line}</span>
                    use of "${vuln.mistake}"
                </div>
                <div class="vuln-mistake">
                    the use of "${vuln.mistake}" makes your program open to "${vuln.explanation}"
                </div>
                <div class="vuln-solution">
                    replace with "${vuln.solution}" to prevent this risk
                </div>
                <div class="solution-code">
                    ${vuln.example || vuln.solution}
                </div>
            </div>
        `;
    });
    
    html += `
            <div style="margin-top: 30px; padding: 15px; background: #1a1a1a; border-radius: 6px; border-left: 4px solid #967bb6; color: #bbb;">
                <strong>Total Vulnerabilities Found:</strong> ${data.vulnerabilities.length}<br>
                <strong>Language:</strong> ${data.language || 'Unknown'}<br>
                <strong>Recommendation:</strong> Fix all vulnerabilities before deploying your code
            </div>
        </div>
    `;
    
    resultsContent.innerHTML = html;
}

/* ---------- LOGIN LAB ---------- */
function loadLoginLab() {
    setActiveTab("login-tab");
    leftPanel.className = "left-panel login-theme";

    labArea.innerHTML = `
        <h2>Login Lab</h2>
        <input type="text" placeholder="Username">
        <input 
            type="password" 
            id="password"
            placeholder="Password"
        >
        <button onclick="submitLogin()">Login</button>
    `;

    explanation.innerHTML = "Try SQL injection payloads ";

    document
        .getElementById("password")
        .addEventListener("keydown", e => {
            if (e.key === "Enter") submitLogin();
        });
}

function submitLogin() {
    const payload = document.getElementById("password").value;
    analyzePayload(payload);
}

/* ---------- COMMENT LAB ---------- */
function loadCommentLab() {
    setActiveTab("comment-tab");
    leftPanel.className = "left-panel comment-theme";

    labArea.innerHTML = `
        <h2>Comment Lab</h2>
        <textarea 
            id="comment"
            placeholder="Write a comment..."
        ></textarea>
        <button onclick="submitComment()">Post</button>
    `;

    explanation.innerHTML = "Try XSS payloads";

    document
        .getElementById("comment")
        .addEventListener("keydown", e => {
            if (e.key === "Enter" && e.ctrlKey) {
                submitComment();
            }
        });
}

function submitComment() {
    const payload = document.getElementById("comment").value;
    analyzePayload(payload);
}

/* ---------- DEFAULT ---------- */
loadLoginLab();