import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "Data", "processed", "balanced_security_dataset_25k_final.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "Data", "processed", "balanced_security_dataset_25k.csv")

# Extensive list of benign phrases
more_benign = [
    "script", "this is a script", "bash script", "python script", "script file",
    "write a script", "run a script", "scripting language", "script kiddie",
    "alert", "alert message", "popup alert", "warning alert", "alert dialog",
    "hello world", "test input", "normal text", "user name", "search term",
    "comment here", "profile description", "regular data", "simple", "example",
    "word", "document", "text", "message", "information", "value", "string",
    "input", "output", "function", "variable", "loop", "condition", "statement",
    "code", "program", "application", "web", "page", "site", "link", "button",
    "click", "submit", "form", "field", "label", "title", "heading", "paragraph"
]

df = pd.read_csv(INPUT_PATH)
existing = set(df["Sentence"])
new_benign = [x for x in more_benign if x not in existing]

if new_benign:
    df_benign = pd.DataFrame({
        "Sentence": new_benign,
        "SQLInjection": 0,
        "XSS": 0,
        "CommandInjection": 0,
        "Normal": 1
    })
    df = pd.concat([df, df_benign], ignore_index=True)
    print(f"Added {len(new_benign)} new benign examples.")
else:
    print("All examples already present.")

df.to_csv(OUTPUT_PATH, index=False)
print(f"Saved to {OUTPUT_PATH} with {len(df)} rows.")