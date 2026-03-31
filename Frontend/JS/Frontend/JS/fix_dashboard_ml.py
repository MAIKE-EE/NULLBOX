#!/usr/bin/env python3
"""Directly edit app.js to preserve ML results in dashboard"""

# Try both relative and absolute paths
import os

filepath = 'app.js'
if not os.path.exists(filepath):
    filepath = os.path.join('Frontend', 'JS', 'app.js')

with open(filepath, 'r') as f:
    lines = f.readlines()

# Find the line with explanation.innerHTML = ` in loadDashboard function
for i in range(len(lines)):
    if 'explanation.innerHTML = `' in lines[i] and i > 950:  # Only in loadDashboard
        # Check next few lines to ensure we're in the right function
        if any('<h3>Dashboard</h3>' in lines[j] for j in range(i, min(i+5, len(lines)))):
            # Insert ML result preservation code before this line
            lines[i] = 'const mlResultHTML = lastMlResult ? \'<div style="margin-bottom: 20px; padding: 15px; background-color: var(--background-tertiary); border-radius: 8px; border: 1px solid var(--background-accent);">\' + lastMlResult + \'</div>\' : \'\';\n'
            # Modify the original line to prepend mlResultHTML
            lines[i + 1] = 'explanation.innerHTML = mlResultHTML + `' + lines[i + 1].split('`')[1]
            break

with open('Frontend/JS/app.js', 'w') as f:
    f.writelines(lines)

print('Successfully modified loadDashboard to preserve ML results')
