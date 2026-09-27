import pandas as pd
import os

def calculate_accurate_telemetry_statistics():
    print("--- Calculating Accurate Telemetry Statistics ---")
    
    input_file = 'processed_data/New_Qualifying_fastest_laps_telemetry.csv'
    output_dir = 'Pre_Clustering_Visualizations'
    output_file = os.path.join(output_dir, 'Accurate_Telemetry_Statistics_Summary.csv')
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print("  -> Loading telemetry file...")
        df = pd.read_csv(input_file)
        print(f"  [OK] Loaded dataset with {len(df)} rows.")
    except FileNotFoundError:
        print(f"  [!] Error: Could not find '{input_file}'.")
        return

    # ==========================================
    # Normalise the column names
    # ==========================================
    # Lower-case every column name (RPM -> rpm, Speed -> speed)
    df.columns = df.columns.str.lower()
    
    # Special case for the FastF1 gear column (ngear -> n_gear)
    if 'ngear' in df.columns:
        df.rename(columns={'ngear': 'n_gear'}, inplace=True)

    # ==========================================
    # Filtering stage - physical sanity checks for a fast lap
    # ==========================================
    print("  -> Filtering sensor glitches and invalid data points...")
    
    if 'speed' in df.columns:
        df = df[df['speed'] > 30]
        
    if 'n_gear' in df.columns:
        df = df[df['n_gear'] >= 1]
        
    if 'rpm' in df.columns:
        df = df[df['rpm'] > 4000]
        
    if 'throttle' in df.columns:
        df['throttle'] = df['throttle'].clip(lower=0, upper=100)
    
    if 'brake' in df.columns:
        if df['brake'].dtype == bool:
            df['brake'] = df['brake'].astype(int) * 100
        df['brake'] = df['brake'].clip(lower=0, upper=100)

    # Compute the statistics
    features_to_analyze = ['rpm', 'speed', 'n_gear', 'throttle', 'brake', 'x', 'y', 'z']
    valid_features = [col for col in features_to_analyze if col in df.columns]

    if not valid_features:
        print("  [!] Error: No target columns found after renaming. Check your CSV format.")
        print(f"  Available columns are: {df.columns.tolist()}")
        return

    print("  -> Calculating Min, Max, Mean, Median, and Standard Deviation...")
    stats_list = []
    
    for feature in valid_features:
        feature_data = df[feature].dropna() 
        
        stats_list.append({
            'Telemetry_Feature': feature,
            'Minimum': round(feature_data.min(), 4),
            'Maximum': round(feature_data.max(), 4),
            'Mean': round(feature_data.mean(), 4),
            'Median': round(feature_data.median(), 4),
            'Standard_Deviation': round(feature_data.std(), 4)
        })
        
    stats_df = pd.DataFrame(stats_list)
    stats_df.to_csv(output_file, index=False)
    
    print(f"\n--- Process Complete ---")
    print(f"  [SUCCESS] Accurate statistical summary saved to: {output_file}")
    print("\n  Preview of Statistics:")
    print(stats_df.to_string(index=False))

calculate_accurate_telemetry_statistics()