import pandas as pd
import numpy as np
import os
from pathlib import Path

def create_balanced_dataset():
    """
    Create a balanced dataset with:
    - 2500 SQL Injection samples
    - 2500 XSS samples  
    - 1500 Command Injection samples
    - 3500 Normal samples
    Total: 10,000 samples
    """
    
    print("=" * 70)
    print("SECURITY DATASET BALANCING TOOL")
    print("=" * 70)
    
    # File paths
    input_path = r"D:\NULLBOX\ML\Data\processed\combined_data_CLEANED.csv"
    output_path = r"D:\NULLBOX\ML\Data\processed\balanced_security_dataset_10k.csv"
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Target distribution
    TARGET_COUNTS = {
        'SQLInjection': 2500,
        'XSS': 2500,
        'CommandInjection': 1500,
        'Normal': 3500
    }
    
    # Step 1: Load the dataset
    print(f"\n LOADING DATASET")
    print(f"   Input: {input_path}")
    
    try:
        df = pd.read_csv(input_path)
        print(f"    Successfully loaded {len(df):,} samples")
    except FileNotFoundError:
        print(f"    File not found: {input_path}")
        print(f"\n   Searching for file...")
        
        # Try to find the file
        search_path = Path(r"D:\NULLBOX\ML\Data\raw")
        if search_path.exists():
            files = list(search_path.glob("*.csv"))
            print(f"   Found CSV files in {search_path}:")
            for f in files:
                print(f"     - {f.name}")
        
        print(f"\n   Please check the file path and try again.")
        return None
    except Exception as e:
        print(f"   ❌ Error loading file: {e}")
        return None
    
    # Step 2: Show initial statistics
    print(f"\n INITIAL DATASET STATISTICS")
    print(f"   Total samples: {len(df):,}")
    
    labels = ['SQLInjection', 'XSS', 'CommandInjection', 'Normal']
    print("\n   Label distribution:")
    for label in labels:
        if label in df.columns:
            count = df[df[label] == 1.0].shape[0]
            percentage = (count / len(df)) * 100
            print(f"     {label}: {count:,} samples ({percentage:.1f}%)")
        else:
            print(f"      {label} column not found in dataset")
    
    # Step 3: Check column names
    print(f"\n🔍 DATASET STRUCTURE")
    print(f"   Columns: {list(df.columns)}")
    print(f"   First sample: {df.iloc[0]['Sentence'][:100]}...")
    
    # Step 4: Check for multi-label samples
    if all(label in df.columns for label in labels):
        df['num_labels'] = df[labels].sum(axis=1)
        multi_label = df[df['num_labels'] > 1].shape[0]
        single_label = df[df['num_labels'] == 1].shape[0]
        print(f"\n   Single-label samples: {single_label:,} ({single_label/len(df)*100:.1f}%)")
        print(f"   Multi-label samples: {multi_label:,} ({multi_label/len(df)*100:.1f}%)")
    else:
        print(f"\n     Missing some label columns, cannot check multi-label samples")
    
    # Step 5: Extract samples for each category
    print(f"\n  EXTRACTING BALANCED SAMPLES")
    
    sampled_dfs = []
    sample_details = {}
    
    for label, target_count in TARGET_COUNTS.items():
        print(f"\n   Processing {label} (target: {target_count} samples)...")
        
        if label not in df.columns:
            print(f"      Column '{label}' not found in dataset!")
            continue
        
        # Get all samples with this label = 1
        label_samples = df[df[label] == 1.0].copy()
        print(f"     Found {len(label_samples):,} total samples with {label} label")
        
        if len(label_samples) == 0:
            print(f"       No samples found for {label}!")
            continue
        
        if len(label_samples) < target_count:
            print(f"       Only {len(label_samples)} samples available, using all")
            sampled = label_samples
        else:
            # Try to get pure samples first (only this label)
            if 'num_labels' in df.columns:
                pure_samples = label_samples[label_samples['num_labels'] == 1]
                print(f"     Pure {label} samples: {len(pure_samples):,}")
                
                if len(pure_samples) >= target_count:
                    # We have enough pure samples
                    sampled = pure_samples.sample(n=target_count, random_state=42, replace=False)
                    print(f"     Selected {target_count} pure {label} samples")
                else:
                    # Need to add some multi-label samples
                    print(f"     Need {target_count - len(pure_samples)} more samples...")
                    sampled = pure_samples
                    
                    # Get multi-label samples with this label
                    multi_samples = label_samples[label_samples['num_labels'] > 1]
                    needed = target_count - len(pure_samples)
                    
                    if len(multi_samples) >= needed:
                        additional = multi_samples.sample(n=needed, random_state=42, replace=False)
                        sampled = pd.concat([sampled, additional])
                        print(f"     Added {len(additional)} multi-label {label} samples")
                    else:
                        # Use all multi-label and fill with any available
                        sampled = pd.concat([sampled, multi_samples])
                        print(f"     Added all {len(multi_samples)} multi-label samples")
            else:
                # Just take random samples if we can't check purity
                sampled = label_samples.sample(n=target_count, random_state=42, replace=False)
                print(f"     Selected {target_count} random {label} samples")
        
        sampled_dfs.append(sampled)
        sample_details[label] = len(sampled)
        print(f"      Selected {len(sampled)} {label} samples")
    
    # Step 6: Combine all samples
    print(f"\n🔗 COMBINING SAMPLES...")
    
    if not sampled_dfs:
        print("    No samples were selected!")
        return None
    
    combined = pd.concat(sampled_dfs, ignore_index=True)
    
    # Remove duplicates
    before = len(combined)
    combined = combined.drop_duplicates(subset=['Sentence'])
    after = len(combined)
    
    if before != after:
        print(f"   Removed {before - after} duplicate samples")
    
    print(f"   Combined dataset has {len(combined):,} unique samples")
    
    # Step 7: Fill missing samples if needed
    total_needed = sum(TARGET_COUNTS.values())
    
    if len(combined) < total_needed:
        print(f"\n FILLING MISSING SAMPLES...")
        print(f"   Need {total_needed - len(combined)} more samples")
        
        # Get samples not yet selected
        used_indices = set(combined.index) if 'index' in combined.columns else set()
        remaining = df[~df.index.isin(used_indices)]
        
        if len(remaining) > 0:
            needed = total_needed - len(combined)
            additional = remaining.sample(n=min(needed, len(remaining)), random_state=42)
            combined = pd.concat([combined, additional], ignore_index=True)
            print(f"   Added {len(additional)} random samples")
    
    # Step 8: Shuffle the dataset
    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Step 9: Verify final distribution
    print(f"\n FINAL DATASET VERIFICATION")
    print(f"   Total samples: {len(combined):,}")
    
    print("\n   Final distribution:")
    for label in labels:
        if label in combined.columns:
            count = combined[combined[label] == 1.0].shape[0]
            target = TARGET_COUNTS.get(label, 0)
            status = "✓" if count >= target * 0.9 else "⚠️"
            print(f"     {status} {label}: {count} / {target} samples")
    
    # Step 10: Save the dataset
    print(f"\n SAVING DATASET...")
    print(f"   Output: {output_path}")
    
    # Remove helper columns
    columns_to_drop = ['num_labels', 'index', 'level_0'] if 'num_labels' in combined.columns else []
    columns_to_drop = [col for col in columns_to_drop if col in combined.columns]
    
    if columns_to_drop:
        combined = combined.drop(columns=columns_to_drop)
    
    combined.to_csv(output_path, index=False)
    print(f"    Successfully saved {len(combined):,} samples")
    
    # Step 11: Create train/val/test splits
    print(f"\n CREATING DATA SPLITS...")
    create_train_val_test_splits(combined, output_dir)
    
    print(f"\n" + "=" * 70)
    print(" BALANCED DATASET CREATION COMPLETE!")
    print("=" * 70)
    
    return combined

def create_train_val_test_splits(df, output_dir, test_size=0.2, val_size=0.1):
    """
    Create train, validation, and test splits
    """
    from sklearn.model_selection import train_test_split
    
    # First split: train+val vs test
    train_val, test = train_test_split(
        df, test_size=test_size, random_state=42, stratify=None
    )
    
    # Second split: train vs val
    train, val = train_test_split(
        train_val, test_size=val_size/(1-test_size), random_state=42, stratify=None
    )
    
    # Save splits
    train_path = output_dir / "balanced_security_train.csv"
    val_path = output_dir / "balanced_security_val.csv"
    test_path = output_dir / "balanced_security_test.csv"
    
    train.to_csv(train_path, index=False)
    val.to_csv(val_path, index=False)
    test.to_csv(test_path, index=False)
    
    print(f"   Train set: {len(train):,} samples ({len(train)/len(df)*100:.1f}%)")
    print(f"   Val set: {len(val):,} samples ({len(val)/len(df)*100:.1f}%)")
    print(f"   Test set: {len(test):,} samples ({len(test)/len(df)*100:.1f}%)")
    
    print(f"\n   Saved to:")
    print(f"     • {train_path}")
    print(f"     • {val_path}")
    print(f"     • {test_path}")
    
    # Show distribution in each split
    print(f"\n   Distribution across splits:")
    labels = ['SQLInjection', 'XSS', 'CommandInjection', 'Normal']
    
    for split_name, split_df, split_path in [
        ("Train", train, train_path),
        ("Validation", val, val_path),
        ("Test", test, test_path)
    ]:
        print(f"\n     {split_name} set:")
        for label in labels:
            if label in split_df.columns:
                count = split_df[split_df[label] == 1.0].shape[0]
                if len(split_df) > 0:
                    percentage = count / len(split_df) * 100
                    print(f"       {label}: {count} ({percentage:.1f}%)")

def main():
    """Main function"""
    print("\n Starting dataset balancing process...")
    print(f"Target distribution:")
    print(f"  • SQL Injection: 2,500 samples")
    print(f"  • XSS: 2,500 samples")
    print(f"  • Command Injection: 1,500 samples")
    print(f"  • Normal: 3,500 samples")
    print(f"  • TOTAL: 10,000 samples")
    
    result = create_balanced_dataset()
    
    if result is not None:
        print(f"\n FINAL SUMMARY:")
        print(f"   Dataset saved to: D:\\NULLBOX\\ML\\Data\\processed\\")
        print(f"   Files created:")
        print(f"     1. balanced_security_dataset_10k.csv")
        print(f"     2. balanced_security_train.csv")
        print(f"     3. balanced_security_val.csv")
        print(f"     4. balanced_security_test.csv")
        
        print(f"\n   Sample preview:")
        print(f"   First 3 sentences:")
        for i in range(min(3, len(result))):
            sentence = result.iloc[i]['Sentence']
            labels = []
            for lbl in ['SQLInjection', 'XSS', 'CommandInjection', 'Normal']:
                if lbl in result.columns and result.iloc[i][lbl] == 1.0:
                    labels.append(lbl)
            print(f"   {i+1}. '{sentence[:80]}...'")
            print(f"      Labels: {', '.join(labels)}")
    else:
        print(f"\n Dataset creation failed. Please check the errors above.")

if __name__ == "__main__":
    main()