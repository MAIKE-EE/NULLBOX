"""
DATASET CLEANER for Security Classification
Cleans mislabeled samples and ensures data quality
"""

import pandas as pd
import re
import os
from pathlib import Path

def is_valid_normal(text):
    """Check if text is truly normal (no attack patterns)"""
    if not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    # SQL injection patterns
    sql_patterns = [
        r'union.*select', r'select.*from', r'insert.*into', 
        r'delete.*from', r'update.*set', r'drop.*table',
        r'create.*table', r'alter.*table', r'truncate.*table',
        r'exec.*xp_', r'exec.*sp_', r'waitfor.*delay',
        r'pg_sleep', r'benchmark', r'sleep\s*\(', 
        r'--\s*$', r'/\*.*\*/', r'or\s+1\s*=\s*1',
        r'and\s+1\s*=\s*1', r'@@version', r'version\s*\('
    ]
    
    # XSS patterns
    xss_patterns = [
        r'<script', r'javascript:', r'onerror=', r'onload=', 
        r'onclick=', r'onmouseover=', r'onfocus=',
        r'alert\s*\(', r'prompt\s*\(', r'confirm\s*\(',
        r'<img.*src=', r'<iframe', r'<svg', r'<object',
        r'<embed', r'<applet', r'<meta.*refresh',
        r'document\.', r'window\.', r'location\.',
        r'eval\s*\(', r'expression\s*\(', r'<body.*onload='
    ]
    
    # Command injection patterns
    cmd_patterns = [
        r';.*ls', r';.*cat', r';.*rm', r';.*wget', 
        r';.*curl', r';.*nc', r';.*netcat',
        r'\|\s*sh', r'\|\s*bash', r'\|\s*cmd',
        r'\$\s*\(', r'`.*`', r'&&.*', r'\|\|.*',
        r'exec\s*\(', r'system\s*\(', r'passthru\s*\(',
        r'shell_exec\s*\(', r'proc_open\s*\(',
        r'popen\s*\(', r'pcntl_exec\s*\('
    ]
    
    # Combined attack patterns
    all_attack_patterns = sql_patterns + xss_patterns + cmd_patterns
    
    # Check for any attack pattern
    for pattern in all_attack_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False
    
    # Additional checks for suspicious content in "normal" text
    suspicious_sequences = [
        r'1=1', r'1=2', r'0=0',  # Common SQL test patterns
        r'union\s+all', r'order\s+by', r'group\s+by',
        r'having\s+1=1', r'where\s+1=1',
        r'char\s*\(', r'concat\s*\(', r'substring\s*\(',
        r'load_file\s*\(', r'into\s+outfile', r'into\s+dumpfile',
        r'utl_http', r'utl_inaddr', r'utl_file',
        r'xp_cmdshell', r'xp_regread', r'xp_dirtree',
        r'sp_configure', r'sp_addlogin', r'sp_addsrvrolemember'
    ]
    
    for seq in suspicious_sequences:
        if re.search(seq, text_lower, re.IGNORECASE):
            return False
    
    # Check for excessive special characters in normal text
    special_chars = ['<', '>', ';', '=', "'", '"', '(', ')', '[', ']', '{', '}', '@', '#', '$', '%', '&', '*', '|', '\\', '/']
    special_count = sum(1 for char in text if char in special_chars)
    
    # Normal text shouldn't have too many special characters
    if special_count > max(3, len(text) * 0.1):  # More than 10% or 3 chars
        return False
    
    return True

def is_valid_attack(text, attack_type):
    """Check if attack sample looks like a real attack"""
    if not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    if attack_type == 'SQLInjection':
        sql_patterns = [
            r'union.*select', r'select.*from', r'insert.*into', 
            r'delete.*from', r'update.*set', r'drop.*table',
            r'create.*table', r'alter.*table', r'truncate.*table',
            r'exec.*xp_', r'exec.*sp_', r'waitfor.*delay',
            r'pg_sleep', r'benchmark', r'sleep\s*\(', 
            r'--\s*$', r'/\*.*\*/', r'or\s+1\s*=\s*1',
            r'and\s+1\s*=\s*1', r'@@version', r'version\s*\(',
            r'information_schema', r'sysobjects', r'syscolumns',
            r'concat\s*\(', r'char\s*\(', r'substring\s*\(',
            r'group_concat\s*\(', r'order\s+by', r'group\s+by',
            r'having\s+1=1', r'where\s+1=1'
        ]
        return any(re.search(p, text_lower, re.IGNORECASE) for p in sql_patterns)
    
    elif attack_type == 'XSS':
        xss_patterns = [
            r'<script', r'javascript:', r'onerror=', r'onload=', 
            r'onclick=', r'onmouseover=', r'onfocus=',
            r'alert\s*\(', r'prompt\s*\(', r'confirm\s*\(',
            r'<img.*src=', r'<iframe', r'<svg', r'<object',
            r'<embed', r'<applet', r'<meta.*refresh',
            r'document\.', r'window\.', r'location\.',
            r'eval\s*\(', r'expression\s*\(', r'<body.*onload=',
            r'<div.*on', r'<a.*on', r'<input.*on',
            r'<form.*on', r'<button.*on', r'<select.*on'
        ]
        return any(re.search(p, text_lower, re.IGNORECASE) for p in xss_patterns)
    
    elif attack_type == 'CommandInjection':
        cmd_patterns = [
            r';.*ls', r';.*cat', r';.*rm', r';.*wget', 
            r';.*curl', r';.*nc', r';.*netcat', r';.*ping',
            r';.*nslookup', r';.*whoami', r';.*id',
            r'\|\s*sh', r'\|\s*bash', r'\|\s*cmd', r'\|\s*powershell',
            r'\$\s*\(', r'`.*`', r'&&.*', r'\|\|.*',
            r'exec\s*\(', r'system\s*\(', r'passthru\s*\(',
            r'shell_exec\s*\(', r'proc_open\s*\(',
            r'popen\s*\(', r'pcntl_exec\s*\(',
            r'Runtime\.getRuntime\(\)\.exec'
        ]
        return any(re.search(p, text_lower, re.IGNORECASE) for p in cmd_patterns)
    
    return True

def clean_dataset(input_path, output_path=None):
    """
    Clean the dataset by removing mislabeled samples
    
    Parameters:
    -----------
    input_path : str
        Path to input CSV file
    output_path : str
        Path to save cleaned dataset (optional)
    
    Returns:
    --------
    pandas.DataFrame : Cleaned dataset
    """
    
    print("=" * 70)
    print("🧹 SECURITY DATASET CLEANER")
    print("=" * 70)
    
    # Set default output path
    if output_path is None:
        input_dir = Path(input_path).parent
        input_name = Path(input_path).stem
        output_path = str(input_dir / f"{input_name}_CLEANED.csv")
    
    print(f"\n📂 Loading dataset from: {input_path}")
    
    try:
        df = pd.read_csv(input_path)
        print(f"   ✅ Loaded {len(df):,} samples")
    except Exception as e:
        print(f"   ❌ Error loading file: {e}")
        return None
    
    # Display initial stats
    print("\n📊 INITIAL DATASET STATISTICS:")
    labels = ['SQLInjection', 'XSS', 'CommandInjection', 'Normal']
    
    for label in labels:
        if label in df.columns:
            count = df[df[label] == 1.0].shape[0]
            percentage = (count / len(df)) * 100
            print(f"   {label}: {count:,} samples ({percentage:.1f}%)")
        else:
            print(f"   ❌ {label} column not found")
    
    # Clean the data
    print("\n🧼 CLEANING DATASET...")
    clean_data = []
    removed = 0
    removed_by_category = {label: 0 for label in labels}
    
    for idx, row in df.iterrows():
        text = str(row['Sentence']) if 'Sentence' in row else str(row.iloc[0])
        
        # Check if it's labeled as Normal
        if 'Normal' in row and row['Normal'] == 1.0:
            if is_valid_normal(text):
                clean_data.append(row)
            else:
                removed += 1
                removed_by_category['Normal'] += 1
        
        # Check if it's labeled as an attack
        else:
            is_valid_sample = True
            attack_found = False
            
            # Check each attack type
            for attack_type in ['SQLInjection', 'XSS', 'CommandInjection']:
                if attack_type in row and row[attack_type] == 1.0:
                    attack_found = True
                    if not is_valid_attack(text, attack_type):
                        is_valid_sample = False
                        removed_by_category[attack_type] += 1
                    break
            
            # If labeled as attack but no attack pattern found
            if attack_found and is_valid_sample:
                clean_data.append(row)
            elif not attack_found:
                # Not labeled as anything? Skip it
                removed += 1
            else:
                removed += 1
    
    # Create cleaned DataFrame
    clean_df = pd.DataFrame(clean_data)
    
    print(f"\n✅ CLEANING COMPLETE:")
    print(f"   Original samples: {len(df):,}")
    print(f"   Cleaned samples: {len(clean_df):,}")
    print(f"   Samples removed: {removed:,} ({removed/len(df)*100:.1f}%)")
    
    if removed > 0:
        print("\n   Removed by category:")
        for label, count in removed_by_category.items():
            if count > 0:
                print(f"     {label}: {count:,} samples")
    
    # Show cleaned distribution
    print("\n📊 CLEANED DATASET STATISTICS:")
    for label in labels:
        if label in clean_df.columns:
            count = clean_df[clean_df[label] == 1.0].shape[0]
            if len(clean_df) > 0:
                percentage = (count / len(clean_df)) * 100
                print(f"   {label}: {count:,} samples ({percentage:.1f}%)")
    
    # Save cleaned dataset
    print(f"\n💾 Saving cleaned dataset to: {output_path}")
    
    # Create directory if it doesn't exist
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    clean_df.to_csv(output_path, index=False)
    print(f"   ✅ Successfully saved {len(clean_df):,} samples")
    
    # Show some examples of what was kept
    print(f"\n🔍 SAMPLE OF CLEANED DATA:")
    for i in range(min(3, len(clean_df))):
        text = clean_df.iloc[i]['Sentence']
        active_labels = []
        for label in labels:
            if label in clean_df.columns and clean_df.iloc[i][label] == 1.0:
                active_labels.append(label)
        
        print(f"\n   Sample {i+1}:")
        print(f"   Text: {text[:100]}...")
        print(f"   Labels: {', '.join(active_labels)}")
    
    print("\n" + "=" * 70)
    print("🎉 DATASET CLEANING COMPLETE!")
    print("=" * 70)
    
    return clean_df

def quick_analysis(filepath):
    """Quick analysis of dataset quality"""
    print(f"\n🔍 QUICK ANALYSIS: {filepath}")
    
    try:
        df = pd.read_csv(filepath)
    except:
        print(f"   ❌ Could not read file")
        return
    
    print(f"   Total samples: {len(df):,}")
    
    # Check for suspicious samples
    suspicious_count = 0
    for idx, row in df.iterrows():
        text = str(row['Sentence'])
        
        if row['Normal'] == 1.0:
            # Check if "Normal" contains attack patterns
            if not is_valid_normal(text):
                suspicious_count += 1
    
    print(f"   Suspicious 'Normal' samples: {suspicious_count:,} ({suspicious_count/len(df)*100:.1f}%)")
    
    # Show examples of suspicious samples
    if suspicious_count > 0:
        print(f"\n   Examples of suspicious 'Normal' samples:")
        count = 0
        for idx, row in df.iterrows():
            if row['Normal'] == 1.0 and not is_valid_normal(str(row['Sentence'])):
                print(f"     {str(row['Sentence'])[:80]}...")
                count += 1
                if count >= 3:
                    break

def main():
    """Main function"""
    print("\n🚀 Starting dataset cleaning process...")
    
    # Define paths
    input_file = r"D:\NULLBOX\ML\Data\raw\combined_data_whole.csv"
    output_file = r"D:\NULLBOX\ML\Data\processed\combined_data_CLEANED.csv"
    
    # Run cleaning
    cleaned_df = clean_dataset(input_file, output_file)
    
    if cleaned_df is not None:
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Your cleaned dataset is ready at: {output_file}")
        print(f"   2. Now run the balanced dataset creator on the CLEANED data")
        print(f"   3. Use: balanced_dataset_creator.py on the cleaned file")
        
        # Quick analysis of original vs cleaned
        print(f"\n🔍 COMPARISON ANALYSIS:")
        quick_analysis(input_file)
        quick_analysis(output_file)

if __name__ == "__main__":
    main()