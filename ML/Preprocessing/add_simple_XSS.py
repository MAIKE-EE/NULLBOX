import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BALANCED_PATH = os.path.join(BASE_DIR, "Data", "processed", "balanced_security_dataset_25k.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "Data", "processed", "balanced_security_dataset_25k_with_xss.csv")

simple_xss = [
    "<script>alert('XSS')</script>",
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert('XSS')",
    "<body onload=alert('XSS')>",
    "<svg onload=alert(1)>",
    "alert('XSS')",
    "prompt('XSS')",
    "<a href='javascript:alert(1)'>click</a>"
]

df = pd.read_csv(BALANCED_PATH)

# Avoid duplicates
existing = set(df["Sentence"])
new_xss = [x for x in simple_xss if x not in existing]

if new_xss:
    df_xss = pd.DataFrame({
        "Sentence": new_xss,
        "SQLInjection": 0,
        "XSS": 1,
        "CommandInjection": 0,
        "Normal": 0
    })
    df = pd.concat([df, df_xss], ignore_index=True)
    print(f"Added {len(new_xss)} new XSS examples.")
else:
    print("All XSS examples already present.")

df.to_csv(OUTPUT_PATH, index=False)
print(f"New dataset saved to {OUTPUT_PATH} with {len(df)} rows.")