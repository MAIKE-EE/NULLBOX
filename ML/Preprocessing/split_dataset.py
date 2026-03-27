import pandas as pd
import os
from sklearn.model_selection import train_test_split

# Set paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # goes up one level to ML/
INPUT_PATH = os.path.join(BASE_DIR, "Data", "processed", "balanced_security_dataset_25k.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data", "processed")

# Load the balanced dataset
if not os.path.exists(INPUT_PATH):
    print(f"Error: {INPUT_PATH} not found.")
    sys.exit(1)

df = pd.read_csv(INPUT_PATH)

# Create label column (needed for stratification)
def get_label(row):
    if row["Normal"] == 1: return 0
    if row["SQLInjection"] == 1: return 1
    if row["XSS"] == 1: return 2
    if row["CommandInjection"] == 1: return 3
    return -1
df["label"] = df.apply(get_label, axis=1)

# Split into train (70%), temp (30%)
train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42, stratify=df["label"])

# Split temp into val (15%) and test (15%)
val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df["label"])

# Drop temporary label column
for split_df in (train_df, val_df, test_df):
    split_df.drop(columns=["label"], inplace=True)

# Save
train_df.to_csv(os.path.join(OUTPUT_DIR, "balanced_security_train.csv"), index=False)
val_df.to_csv(os.path.join(OUTPUT_DIR, "balanced_security_val.csv"), index=False)
test_df.to_csv(os.path.join(OUTPUT_DIR, "balanced_security_test.csv"), index=False)

print(f"Train size: {len(train_df)}")
print(f"Val size:   {len(val_df)}")
print(f"Test size:  {len(test_df)}")