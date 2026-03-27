// Inject Chat CSS dynamically
const chatStyles = `
<style id="chat-styles">
/* NULLBOT CHAT ICON - Floating Messenger Style */
.chat-icon-container {
 position: fixed;
 bottom: 30px;
 right: 30px;
 z-index: 1500;
 display: none;
}

.chat-icon-container.show {
 display: block;
 animation: slideUp 0.3s ease-out;
}

.chat-icon {
 width: 60px;
 height: 60px;
 background: var(--brand-experiment);
 border-radius: 50%;
 cursor: pointer;
 box-shadow: 0 8px 24px rgba(150, 123, 182, 0.4),
 0 4px 12px rgba(0, 0, 0, 0.2);
 display: flex;
 align-items: center;
 justify-content: center;
 transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
 position: relative;
}

.chat-icon:hover {
 transform: scale(1.1) translateY(-4px);
 box-shadow: 0 12px 28px rgba(150, 123, 182, 0.5),
 0 6px 16px rgba(0, 0, 0, 0.3);
 background: var(--brand-experiment-560);
}

.chat-icon::before {
 content: "💬";
 font-size: 28px;
}

/* NOTIFICATION BUBBLE - Messenger Style */
.notification-bubble {
 position: absolute;
 bottom: 70px;
 right: 0;
 background: var(--brand-experiment);
 border: 1px solid var(--background-accent);
 border-radius: 12px;
 padding: 12px 16px;
 box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
 min-width: 250px;
 opacity: 0;
 transform: translateY(10px);
 transition: all 0.3s ease;
 font-size: 14px;
 color: white;
 line-height: 1.4;
 white-space: nowrap;
}

.notification-bubble.show {
 opacity: 1;
 transform: translateY(0);
}

.notification-bubble::after {
 content: "";
 position: absolute;
 bottom: -8px;
 right: 20px;
 width: 0;
 height: 0;
 border-left: 8px solid transparent;
 border-right: 8px solid transparent;
 border-top: 8px solid var(--background-accent);
}

/* CHATBOX CONTAINER */
.chat-box {
 position: fixed;
 bottom: 100px;
 right: 30px;
 width: 340px;
 height: 450px;
 background: var(--background-secondary);
 border: 1px solid var(--background-accent);
 border-radius: 12px;
 box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
 z-index: 2000;
 display: none;
 flex-direction: column;
 overflow: hidden;
 transform: scale(0.8) translateY(20px);
 opacity: 0;
 transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.chat-box.open {
 display: flex;
 transform: scale(1) translateY(0);
 opacity: 1;
}

/* CHAT HEADER */
.chat-header {
 background: var(--background-tertiary);
 padding: 16px 20px;
 border-bottom: 1px solid var(--background-accent);
 display: flex;
 justify-content: space-between;
 align-items: center;
}

.chat-title {
 color: var(--header-primary);
 font-size: 18px;
 font-weight: 700;
 margin: 0;
}

.chat-subtitle {
 color: var(--header-secondary);
 font-size: 12px;
 margin: 0;
}

.chat-close {
 background: none;
 border: none;
 color: var(--interactive-normal);
 font-size: 24px;
 cursor: pointer;
 padding: 4px 8px;
 border-radius: 4px;
 transition: all 0.2s ease;
}

.chat-close:hover {
 background: var(--background-accent);
 color: var(--interactive-hover);
}

/* MESSAGES AREA */
.chat-messages {
 flex: 1;
 padding: 20px;
 overflow-y: auto;
 display: flex;
 flex-direction: column;
 gap: 12px;
}

/* MESSAGE BUBBLES */
.message {
 max-width: 85%;
 padding: 10px 14px;
 border-radius: 12px;
 font-size: 14px;
 line-height: 1.4;
 word-wrap: break-word;
 animation: slideUp 0.2s ease-out;
}

.message.user {
 background: var(--brand-experiment);
 color: white;
 align-self: flex-end;
 border-bottom-right-radius: 4px;
}

.message.bot {
 background: var(--background-tertiary);
 color: var(--text-normal);
 align-self: flex-start;
 border-bottom-left-radius: 4px;
}

/* PRESET OPTIONS */
.preset-options {
 display: flex;
 flex-direction: column;
 gap: 8px;
 padding: 0 20px 16px;
 border-bottom: 1px solid var(--background-accent);
}

.preset-option {
 background: var(--background-tertiary);
 border: 1px solid var(--background-accent);
 border-radius: 8px;
 padding: 10px 14px;
 cursor: pointer;
 color: var(--text-normal);
 font-size: 14px;
 transition: all 0.2s ease;
 text-align: left;
}

.preset-option:hover {
 background: var(--background-accent);
 border-color: var(--brand-experiment);
 transform: translateX(4px);
}

/* CHAT INPUT */
.chat-input-container {
 border-top: 1px solid var(--background-accent);
 padding: 16px;
 display: flex;
 gap: 10px;
 align-items: center;
}

.chat-input {
 flex: 1;
 background: var(--background-tertiary);
 border: 1px solid var(--background-accent);
 border-radius: 20px;
 padding: 10px 16px;
 color: var(--text-normal);
 font-size: 14px;
 outline: none;
 transition: all 0.2s ease;
}

.chat-input:focus {
 border-color: var(--brand-experiment);
 box-shadow: 0 0 0 2px rgba(150, 123, 182, 0.2);
}

.chat-send {
 background: var(--brand-experiment);
 border: none;
 border-radius: 50%;
 width: 36px;
 height: 36px;
 cursor: pointer;
 display: flex;
 align-items: center;
 justify-content: center;
 transition: all 0.2s ease;
}

.chat-send:hover {
 background: var(--brand-experiment-560);
 transform: scale(1.1);
}

.chat-send::before {
 content: "➤";
 color: white;
 font-size: 16px;
}

/* TYPING INDICATOR */
.typing-indicator {
 background: var(--background-tertiary);
 border-radius: 12px;
 padding: 10px 14px;
 margin-bottom: 12px;
 font-size: 14px;
 color: var(--text-muted);
 font-style: italic;
 align-self: flex-start;
 border-bottom-left-radius: 4px;
 opacity: 0;
 animation: fadeIn 0.3s ease-out forwards;
}

.typing-indicator.show {
 display: flex !important;
 align-items: center;
 gap: 8px;
}

.typing-text {
 margin-right: 8px;
}

.typing-dots {
 display: flex;
 gap: 3px;
}

.typing-dots span {
 width: 6px;
 height: 6px;
 background: var(--brand-experiment);
 border-radius: 50%;
 animation: typingDot 1.4s infinite;
}

.typing-dots span:nth-child(2) {
 animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
 animation-delay: 0.4s;
}

@keyframes typingDot {
 0%, 60%, 100% {
 transform: translateY(0);
 opacity: 0.7;
 }
 30% {
 transform: translateY(-10px);
 opacity: 1;
 }
}

/* MESSAGE ANIMATION */
.message {
 animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
 from {
 opacity: 0;
 transform: translateY(10px) scale(0.95);
 }
 to {
 opacity: 1;
 transform: translateY(0) scale(1);
 }
}

/* DISABLED INPUT */
.chat-input:disabled {
 opacity: 0.5;
 cursor: not-allowed;
}

/* SMOOTH SCROLL */
.chat-messages {
 scroll-behavior: smooth;
}

/* ANIMATIONS */
@keyframes slideUp {
 from {
 opacity: 0;
 transform: translateY(20px);
 }
 to {
 opacity: 1;
 transform: translateY(0);
 }
}

@media (max-width: 768px) {
 .chat-box {
 width: 90vw;
 right: 5vw;
 }

 .chat-icon-container {
 right: 20px;
 bottom: 20px;
 }
}
</style>
`;
document.head.insertAdjacentHTML('beforeend', chatStyles);

// Chat state variables
let chatSessionId = null;
let chatPayload = '';
let chatVulnerabilityType = '';
let chatLabType = '';
let chatHasInteracted = false;
let currentTypingInterval = null;

// Chat DOM elements
const chatIcon = document.getElementById("chatIcon");
const chatBox = document.getElementById("chatBox");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const presetOptions = document.getElementById("presetOptions");
const notificationBubble = document.getElementById("notificationBubble");

// Lab elements
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
 const lab_type = document.querySelector(".tab.active").textContent.toLowerCase();

 const res = await fetch("http://127.0.0.1:5000/analyze", {
 method: "POST",
 headers: { "Content-Type": "application/json" },
 body: JSON.stringify({
 payload: payload,
 lab_type: lab_type
 })
 });

 if (!res.ok) {
 throw new Error(`HTTP error! status: ${res.status}`);
 }

 const data = await res.json();
 explanation.innerHTML = data.explanation || "No explanation provided.";

 // Show chat if vulnerable
 if (data.is_vulnerable) {
 showChat(payload, data.vulnerability_type, lab_type, data.session_id);
 }

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

/* ---------- CHAT FUNCTIONS ---------- */
function showChat(payload, vulnerabilityType, labType, sessionId) {
 chatSessionId = sessionId;
 chatPayload = payload;
 chatVulnerabilityType = vulnerabilityType;
 chatLabType = labType;

 // Show chat icon with notification
 chatIcon.classList.add("show");
 notificationBubble.classList.add("show");

 // Reset chat state
 chatHasInteracted = false;
 clearChatMessages();
 addBotMessage("Hi, I'm NULLBOT. I can help you understand this input.");
 presetOptions.style.display = "flex";
}

function openChat() {
 chatBox.classList.add("open");
 notificationBubble.classList.remove("show");
 chatInput.focus();
}

function closeChat() {
 chatBox.classList.remove("open");
}

function clearChatMessages() {
 chatMessages.innerHTML = "";
}

function addUserMessage(message) {
 const div = document.createElement("div");
 div.className = "message user";
 div.textContent = message;
 chatMessages.appendChild(div);
 chatMessages.scrollTop = chatMessages.scrollHeight;
}

function createTypingIndicator() {
 console.log("TYPING: Creating typing indicator");
 if (!chatMessages) {
 console.error("ERROR: chatMessages not found");
 return null;
 }

 const typingDiv = document.createElement("div");
 typingDiv.className = "typing-indicator";
 typingDiv.id = "typingIndicator";

 const textDiv = document.createElement("div");
 textDiv.className = "typing-text";
 textDiv.textContent = "NULLBOT is typing";

 const dotsDiv = document.createElement("div");
 dotsDiv.className = "typing-dots";

 for (let i = 0; i < 3; i++) {
 const span = document.createElement("span");
 dotsDiv.appendChild(span);
 }

 typingDiv.appendChild(textDiv);
 typingDiv.appendChild(dotsDiv);
 chatMessages.appendChild(typingDiv);
 chatMessages.scrollTop = chatMessages.scrollHeight;

 console.log("TYPING: Typing indicator created");
 return typingDiv;
}

function removeTypingIndicator() {
 console.log("TYPING: Removing typing indicator");
 const typingDiv = document.getElementById("typingIndicator");
 if (typingDiv) {
 typingDiv.remove();
 console.log("TYPING: Typing indicator removed");
 } else {
 console.log("TYPING: No typing indicator to remove");
 }
}

function addBotMessage(message) {
 console.log("RENDERING: addBotMessage() called with:", message ? (message.substring(0, 50) + "...") : "<EMPTY MESSAGE>");
 const div = document.createElement("div");
 div.className = "message bot";
 div.textContent = message; // Set full message immediately
 chatMessages.appendChild(div);

 console.log("RENDERING: Message div created and appended to chatMessages");
 console.log("RENDERING: chatMessages.innerHTML now contains", chatMessages.children.length, "elements");

 // Smooth scroll to bottom
 chatMessages.scrollTop = chatMessages.scrollHeight;
 console.log("RENDERING: Scrolled to bottom");

 return div;
}

function selectPreset(message) {
 chatInput.value = message;
 sendChatMessage();
}

async function sendChatMessage() {
 console.log("=== FRONTEND: sendChatMessage() STARTED ===");
 const message = chatInput.value.trim();
 console.log("Message to send:", message);
 console.log("session_id:", chatSessionId);
 console.log("payload:", chatPayload);
 console.log("vulnerability_type:", chatVulnerabilityType);
 console.log("lab_type:", chatLabType);

 if (!message || !chatSessionId) {
 console.log("ERROR: Missing message or session_id. Aborting.");
 return;
 }

 // Disable input while waiting
 chatInput.disabled = true;

 // Add user message
 console.log("Adding user message to UI...");
 addUserMessage(message);
 chatInput.value = "";

 // Hide presets after first interaction
 if (!chatHasInteracted) {
 presetOptions.style.display = "none";
 chatHasInteracted = true;
 }

 // Show typing indicator - Dynamically create it
 console.log("Creating typing indicator...");
 createTypingIndicator();

 try {
 console.log("Making API call to /chat...");
 const res = await fetch("http://127.0.0.1:5000/chat", {
 method: "POST",
 headers: { "Content-Type": "application/json" },
 body: JSON.stringify({
 session_id: chatSessionId,
 message: message,
 payload: chatPayload,
 vulnerability_type: chatVulnerabilityType,
 lab_type: chatLabType
 })
 });

 console.log("API response received. Status:", res.status, res.ok ? "OK" : "ERROR");

 if (!res.ok) {
 throw new Error(`HTTP error! status: ${res.status}`);
 }

 const data = await res.json();
 console.log("API JSON data received:", data);

 // Remove typing indicator
 console.log("Removing typing indicator...");
 removeTypingIndicator();

 // Show bot message
 console.log("Rendering bot message...");
 addBotMessage(data.response);

 } catch (err) {
 console.error("Chat error:", err);
 hideTypingIndicator();
 addBotMessage("Sorry, I couldn't process your message. Please try again.");
 }

 console.log("Re-enabling chat input...");
 chatInput.disabled = false;
 console.log("=== FRONTEND: sendChatMessage() COMPLETE ===");
}

// Handle Enter key in chat input
chatInput.addEventListener("keydown", e => {
 if (e.key === "Enter" && !e.shiftKey) {
 e.preventDefault();

 // Clear any existing typing if user sends new message
 if (currentTypingInterval) {
 clearInterval(currentTypingInterval);
 currentTypingInterval = null;
 removeTypingIndicator();
 }

 sendChatMessage();
 }
});

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

 explanation.innerHTML = "Welcome to NULLBOX! Here you can safely test payloads and learn about injection attacks. Select a lab and try out some inputs to see explanations here.";

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

 explanation.innerHTML = "Welcome to NULLBOX! Here you can safely test payloads and learn about injection attacks. Select a lab and try out some inputs to see explanations here.";

 document
 .getElementById("comment")
 .addEventListener("keydown", e => {
 if (e.key === "Enter" && e.ctrlKey) {
 submitComment();
 }
 });
}

/* ---------- PING LAB ---------- */
function loadPingLab() {
 setActiveTab("ping-tab");
 leftPanel.className = "left-panel ping-theme";

 labArea.innerHTML = `
 <h2>Ping Lab</h2>
 <input type="text" id="hostname" placeholder="Hostname or IP" autocomplete="off">
 <button onclick="submitPing()">Ping</button>
 `;

 explanation.innerHTML = "Welcome to NULLBOX! Here you can safely test payloads and learn about injection attacks. Select a lab and try out some inputs to see explanations here.";

 document.getElementById("hostname").addEventListener("keydown", e => {
 if (e.key === "Enter") submitPing();
 });
}

function submitPing() {
 const payload = document.getElementById("hostname").value;
 if (!payload) {
 explanation.innerText = "Enter a hostname to analyze.";
 return;
 }
 analyzePingPayload(payload);
}

async function analyzePingPayload(payload) {
 try {
 const lab_type = document.querySelector(".tab.active").textContent.toLowerCase();
 const res = await fetch("http://127.0.0.1:5000/ping_analyze", {
 method: "POST",
 headers: { "Content-Type": "application/json" },
 body: JSON.stringify({
 hostname: payload,
 lab_type: lab_type
 })
 });

 if (!res.ok) {
 throw new Error(`HTTP error! status: ${res.status}`);
 }

 const data = await res.json();
 explanation.innerHTML = data.explanation || "No explanation provided.";

 // Show chat if vulnerable
 if (data.is_vulnerable) {
 showChat(payload, data.vulnerability_type, lab_type, data.session_id);
 }

 } catch (err) {
 console.error("Ping analyzer error:", err);
 explanation.innerText = `Analyzer error: ${err.message}`;
 }
}

function submitComment() {
 const payload = document.getElementById("comment").value;
 analyzePayload(payload);
}

/* ---------- DEFAULT ---------- */
loadLoginLab();
