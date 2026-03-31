#!/usr/bin/env python3
"""Fix ML result display in app.js"""

with open('app.js', 'r') as f:
    lines = f.readlines()

# Find the line with "explanation.innerHTML = `" in loadDashboard
# It's around line 1077 (index 1076)
target_line = 1076

# Check if this is the correct line
if 'explanation.innerHTML = `' in lines[target_line]:
    # Insert the ML preservation logic before this line
    preservation_code = 'const mlResultHTML = lastMlResult ? \'<div style="margin-bottom: 20px; padding: 15px; background-color: var(--background-tertiary); border-radius: 8px; border: 1px solid var(--background-accent);">\' + lastMlResult + \'</div>\' : \'\';\n'
    lines.insert(target_line, preservation_code)

    # Now modify the original line to prepend mlResultHTML
    lines[target_line + 1] = 'explanation.innerHTML = mlResultHTML + `\n'

    # Write the modified content back
    with open('app.js', 'w') as f:
        f.writelines(lines)

    print(f"Successfully modified line {target_line + 1} to preserve ML results")
else:
    print(f"Could not find target line at index {target_line}. Found: {lines[target_line][:50]}...")
