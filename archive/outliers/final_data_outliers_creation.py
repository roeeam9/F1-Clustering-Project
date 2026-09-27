import pandas as pd
import os

def calculate_feature_statistics():
    print("--- Calculating Feature Statistics ---")
    
    # Path to the final feature file (read only)
    input_file = 'processed_data/Qualifying_final_clustering_matrix.csv'
    
    # Output directory and the new file to be created
    output_dir = 'Driver Performance Metrics'
    output_file = os.path.join(output_dir, 'Feature_Statistics_Summary.csv')
    
    # Create the output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        df = pd.read_csv(input_file)
        print(f"  [OK] Loaded dataset with {len(df)} rows.")
    except FileNotFoundError:
        print(f"  [!] Error: Could not find '{input_file}'.")
        return

    # Numeric columns to profile (identifier columns excluded)
    features_to_analyze = [
        'entry_speed', 
        'apex_speed', 
        'exit_speed', 
        'speed_drop',
        'braking_pct_before_apex', 
        'trail_braking_pct', 
        'throttle_app_pct_after_apex', 
        'coasting_pct', 
        'braking_time_pct', 
        'average_throttle', 
        'min_gear', 
        'average_speed'
    ]
    
    # Verify the columns exist in the file
    missing_cols = [col for col in features_to_analyze if col not in df.columns]
    if missing_cols:
         print(f"  [!] Warning: Missing columns {missing_cols}. They will be skipped.")
         features_to_analyze = [col for col in features_to_analyze if col in df.columns]

    print("  -> Calculating Min, Max, Mean, Median, and Variance...")
    
    # Compute the statistics
    stats_list = []
    
    for feature in features_to_analyze:
        # dropna guards against calculation errors on the rare empty cell
        feature_data = df[feature].dropna() 
        
        stats_list.append({
            'Feature_Name': feature,
            'Minimum': round(feature_data.min(), 4),
            'Maximum': round(feature_data.max(), 4),
            'Mean (Average)': round(feature_data.mean(), 4),
            'Median': round(feature_data.median(), 4),
            'Variance': round(feature_data.var(), 4)
        })
        
    # Build a DataFrame from the results
    stats_df = pd.DataFrame(stats_list)
    
    # Write to the new file; the source file is left untouched
    stats_df.to_csv(output_file, index=False)
    
    print(f"\n--- Process Complete ---")
    print(f"  [SUCCESS] Statistical summary safely saved to: {output_file}")
    
    # Short printout so the results are visible immediately
    print("\n  Preview of Statistics:")
    print(stats_df.to_string(index=False))

#calculate_feature_statistics()