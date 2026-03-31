#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Read the file
with open('app.js', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find and replace the welcome message in loadCommentLab
for i, line in enumerate(lines):
    if 'explanation.innerHTML = "Welcome to NULLBOX! Here you can safely test payloads' in line:
        # Check if this is in Comment Lab (after loadCommentLab definition)
        if i > 50 and 'loadCommentLab' in ''.join(lines[max(0,i-50):i]):
            # Replace this line and add the heading code
            lines[i] = '  explanation.innerHTML = "welcome to comment lab, write comments to analyze";\n\n  // Update the box heading for Comment Lab\n  const queryTitle = document.getElementById("queryTitle");\n  if (queryTitle) {\n    queryTitle.textContent = "HTML Rendered";\n  }\n'
            break

# Find and add updateXSSPreview call after renderComments
for i, line in enumerate(lines):
    if '// Render all comments using innerHTML (intentionally vulnerable to XSS)' in line:
        # Next line should be renderComments();
        if i+1 < len(lines) and 'renderComments();' in lines[i+1]:
            # Insert after renderComments();
            lines.insert(i+2, '\n  // Update XSS preview in right panel\n')
            lines.insert(i+3, '  updateXSSPreview(payload);\n')
            break

# Add updateXSSPreview function before PING LAB
for i, line in enumerate(lines):
    if '/* ---------- PING LAB ---------- */' in line:
        # Insert the function before this line
        function_code = '''function updateXSSPreview(payload) {
  const currentQuery = document.getElementById("currentQuery");
  if (!currentQuery) return;
  const vulnerableHTML = `<div class="comment">${payload}</div>`;
  currentQuery.textContent = vulnerableHTML;
}

'''
        lines.insert(i, function_code)
        break

# Write back
with open('app.js', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Changes applied successfully!")
