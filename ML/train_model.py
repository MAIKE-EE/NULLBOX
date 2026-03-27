# ML/train_model.py

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
import sys
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(__file__))
from preprocess import preprocess_payload

# ========== CONFIGURATION ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data", "processed")
TRAIN_PATH = os.path.join(DATA_DIR, "balanced_security_train.csv")
VAL_PATH   = os.path.join(DATA_DIR, "balanced_security_val.csv")
TEST_PATH  = os.path.join(DATA_DIR, "balanced_security_test.csv")

MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Column names (adjust if needed)
CODE_COL = "Sentence"
SQL_COL = "SQLInjection"
XSS_COL = "XSS"
CMD_COL = "CommandInjection"
NORMAL_COL = "Normal"

class_names = ["Benign", "SQL Injection", "XSS", "Command Injection"]

# ========== LABEL FUNCTION ==========
def get_label(row):
    if row[NORMAL_COL] == 1:
        return 0
    if row[SQL_COL] == 1:
        return 1
    if row[XSS_COL] == 1:
        return 2
    if row[CMD_COL] == 1:
        return 3
    return 0  # fallback (should not happen)

# ========== LOAD PRE‑SPLIT DATA ==========
print("Loading pre‑split data...")
train_df = pd.read_csv(TRAIN_PATH)
val_df   = pd.read_csv(VAL_PATH)
test_df  = pd.read_csv(TEST_PATH)

print(f"Train size: {len(train_df)}")
print(f"Val size:   {len(val_df)}")
print(f"Test size:  {len(test_df)}")

# ========== PREPROCESS ==========
print("Preprocessing...")
for df in (train_df, val_df, test_df):
    df["clean_code"] = df[CODE_COL].apply(preprocess_payload)

X_train = train_df["clean_code"]
y_train = train_df.apply(get_label, axis=1)

X_val   = val_df["clean_code"]
y_val   = val_df.apply(get_label, axis=1)

X_test  = test_df["clean_code"]
y_test  = test_df.apply(get_label, axis=1)

print("Class distribution in train set:")
print(y_train.value_counts())

# ========== BUILD PIPELINE ==========
vectorizer = TfidfVectorizer(
    max_features=15000,
    ngram_range=(3, 5),
    analyzer='char',
    lowercase=False,
)

rf = RandomForestClassifier(
    n_estimators=150,
    max_depth=30,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

pipeline = Pipeline([
    ('tfidf', vectorizer),
    ('clf', rf)
])

# ========== TRAIN ==========
print("Training model...")
pipeline.fit(X_train, y_train)

# ========== EVALUATION ==========
y_val_pred = pipeline.predict(X_val)
y_test_pred = pipeline.predict(X_test)

val_acc = accuracy_score(y_val, y_val_pred)
test_acc = accuracy_score(y_test, y_test_pred)

print(f"\nValidation Accuracy: {val_acc:.4f}")
print(f"Test Accuracy:       {test_acc:.4f}")

print("\nValidation Report:")
print(classification_report(y_val, y_val_pred, target_names=class_names))

print("\nTest Report:")
print(classification_report(y_test, y_test_pred, target_names=class_names))

# ========== SAVE REPORTS ==========
def save_report(y_true, y_pred, name):
    report = classification_report(y_true, y_pred, target_names=class_names)
    with open(os.path.join(MODEL_DIR, f"{name}_report.txt"), "w") as f:
        f.write(report)

save_report(y_val, y_val_pred, "validation")
save_report(y_test, y_test_pred, "test")

# ========== CONFUSION MATRICES ==========
def plot_confusion(y_true, y_pred, title):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names,
                yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, f"{title}.png"))
    plt.close()

plot_confusion(y_val, y_val_pred, "validation_confusion_matrix")
plot_confusion(y_test, y_test_pred, "test_confusion_matrix")

# ========== ACCURACY BAR CHART ==========
plt.figure(figsize=(4,5))
plt.bar(["Validation", "Test"], [val_acc, test_acc], color=['steelblue', 'darkorange'])
plt.ylim(0, 1)
plt.ylabel("Accuracy")
plt.title("Model Accuracy")
for i, v in enumerate([val_acc, test_acc]):
    plt.text(i, v + 0.02, f"{v:.4f}", ha='center')
plt.tight_layout()
plt.savefig(os.path.join(MODEL_DIR, "accuracy_comparison.png"))
plt.close()

# ========== FEATURE IMPORTANCE ==========
# Get feature names from vectorizer
feature_names = vectorizer.get_feature_names_out()
clf = pipeline.named_steps['clf']
importances = clf.feature_importances_

# Top 20 features
indices = np.argsort(importances)[-20:]
top_features = [feature_names[i] for i in indices]

plt.figure(figsize=(8,6))
plt.barh(range(len(indices)), importances[indices], color='teal')
plt.yticks(range(len(indices)), top_features)
plt.xlabel("Importance")
plt.title("Top 20 Character n‑gram Features")
plt.tight_layout()
plt.savefig(os.path.join(MODEL_DIR, "feature_importance.png"))
plt.close()

# ========== SAVE MODEL ==========
joblib.dump(pipeline, os.path.join(MODEL_DIR, "random_forest_pipeline.joblib"))
print("\nModel, reports, and plots saved successfully.")