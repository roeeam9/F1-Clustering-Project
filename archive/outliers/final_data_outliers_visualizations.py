import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_outlier_visualizations():
    print("--- Generating Outlier Visualizations ---")
    
    # Path to the final feature file
    input_file = 'processed_data/Qualifying_final_clustering_matrix.csv'
    
    # Output directory for the generated images
    output_dir = 'outlier_visualizations'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        df = pd.read_csv(input_file)
        print(f"  [OK] Loaded dataset with {len(df)} rows.")
    except FileNotFoundError:
        print(f"  [!] Error: Could not find '{input_file}'.")
        return

    # Features to inspect, using the updated column names
    features = [
        'entry_speed', 'apex_speed', 'exit_speed', 'speed_drop',
        'braking_pct_before_apex', 'trail_braking_pct', 
        'throttle_app_pct_after_apex', 'coasting_pct', 
        'braking_time_pct', 'average_throttle', 'min_gear', 'average_speed'
    ]
    
    # Verify the columns exist in the file
    available_features = [f for f in features if f in df.columns]
    
    if not available_features:
        print("  [!] Error: Could not find the specified columns. Check column names.")
        return

    # Clean visual style
    sns.set_theme(style="whitegrid")
    
    for feature in available_features:
        # New figure
        plt.figure(figsize=(12, 6))
        
        # 1. Boxplot - points beyond the whiskers are the outliers
        sns.boxplot(x='track', y=feature, data=df, palette="Set2", width=0.5, fliersize=6)
        
        # 2. Overlay the individual points (jitter) to show where the data is dense
        sns.stripplot(x='track', y=feature, data=df, color=".25", alpha=0.3, size=3, jitter=True)
        
        # Titles
        clean_title = feature.replace("_", " ").title()
        plt.title(f'Outlier Detection: {clean_title} by Track', fontsize=16, fontweight='bold')
        plt.xlabel('Track', fontsize=12)
        plt.ylabel(clean_title, fontsize=12)
        
        # Save the image
        file_name = f"Outliers_{feature}.png"
        output_path = os.path.join(output_dir, file_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  [+] Saved: {file_name}")

    print(f"\n--- Process Complete ---")
    print(f"  [SUCCESS] All outlier visualizations saved to the '{output_dir}' folder.")

create_outlier_visualizations()