import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_all_eda_visualizations():
    print("--- Starting Full EDA Visualization Suite ---")
    
    # 1. Paths
    input_file = 'processed_data/Qualifying_final_clustering_matrix.csv'
    output_dir = 'Pre_Clustering_Visualizations'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        df = pd.read_csv(input_file)
        print(f"  [OK] Loaded dataset with {len(df)} rows.")
    except FileNotFoundError:
        print(f"  [!] Error: Could not find '{input_file}'.")
        return

    # 2. Features, using the updated column names
    numeric_features = [
        'entry_speed', 'apex_speed', 'exit_speed', 'speed_drop',
        'braking_pct_before_apex', 'trail_braking_pct', 
        'throttle_app_pct_after_apex', 'coasting_pct', 
        'braking_time_pct', 'average_throttle', 'min_gear', 'average_speed'
    ]
    
    # Verify the columns exist in the file
    features = [f for f in numeric_features if f in df.columns]
    
    # Shared style for all the plots
    sns.set_theme(style="whitegrid")

    # ==========================================
    # Plot 1: Correlation Heatmap
    # ==========================================
    print("  -> [1/6] Generating Correlation Heatmap...")
    plt.figure(figsize=(14, 12))
    corr_matrix = df[features].corr()
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True, linewidths=.5)
    plt.title('Feature Correlation Matrix', fontsize=18, fontweight='bold')
    plt.savefig(os.path.join(output_dir, '1_Correlation_Heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # ==========================================
    # Plot 2: Feature Distributions
    # ==========================================
    print("  -> [2/6] Generating Feature Distributions...")
    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(20, 12))
    axes = axes.flatten()
    
    for i, col in enumerate(features):
        if i < len(axes):
            sns.histplot(df[col], kde=True, ax=axes[i], color='royalblue', bins=30)
            axes[i].set_title(col.replace('_', ' ').title(), fontweight='bold')
            axes[i].set_xlabel('')
            axes[i].set_ylabel('')
            
    plt.tight_layout()
    fig.suptitle('Distributions of Numerical Features', fontsize=22, fontweight='bold', y=1.03)
    plt.savefig(os.path.join(output_dir, '2_Feature_Distributions.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # ==========================================
    # Plot 3: Key Metrics Pairplot
    # ==========================================
    print("  -> [3/6] Generating Pairplot for Key Metrics...")
    key_metrics = ['apex_speed', 'speed_drop', 'braking_pct_before_apex', 'throttle_app_pct_after_apex']
    valid_metrics = [k for k in key_metrics if k in df.columns]
    
    if len(valid_metrics) == 4 and 'track' in df.columns:
        pairplot_df = df[['track'] + valid_metrics].copy()
        g = sns.pairplot(pairplot_df, hue='track', palette='tab10', corner=True, plot_kws={'alpha': 0.6})
        g.fig.suptitle('Pairwise Relationships (Colored by Track)', fontsize=18, fontweight='bold', y=1.02)
        plt.savefig(os.path.join(output_dir, '3_Key_Metrics_Pairplot.png'), dpi=300, bbox_inches='tight')
        plt.close()

    # ==========================================
    # Plot 4: Track Bias Violin Plots
    # ==========================================
    print("  -> [4/6] Generating Track Bias Violin Plots...")
    bias_features = ['apex_speed', 'braking_pct_before_apex', 'throttle_app_pct_after_apex', 'average_throttle']
    valid_bias = [f for f in bias_features if f in df.columns]
    
    if valid_bias and 'track' in df.columns:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        for i, feature in enumerate(valid_bias):
            sns.violinplot(x='track', y=feature, data=df, ax=axes[i], palette='muted', inner='quartile')
            axes[i].set_title(f'Track Bias: {feature.replace("_", " ").title()}', fontweight='bold')
            axes[i].set_xlabel('')
            axes[i].set_ylabel(feature.replace("_", " ").title())
                
        plt.tight_layout()
        fig.suptitle('Visualizing Track Bias (Why Scaling is Needed)', fontsize=20, fontweight='bold', y=1.03)
        plt.savefig(os.path.join(output_dir, '4_Track_Bias_Violin_Plots.png'), dpi=300, bbox_inches='tight')
        plt.close()

    # ==========================================
    # Plot 5: Categorical Bar Plot - corner count per track
    # ==========================================
    print("  -> [5/6] Generating Categorical Bar Plot (Counts)...")
    if 'track' in df.columns:
        plt.figure(figsize=(10, 6))
        ax = sns.countplot(x='track', data=df, palette='viridis', order=df['track'].value_counts().index)
        plt.title('Data Points per Track (Categorical Distribution)', fontsize=16, fontweight='bold')
        plt.xlabel('Track', fontsize=12)
        plt.ylabel('Number of Corners Recorded', fontsize=12)
        
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=11, color='black', xytext=(0, 5),
                        textcoords='offset points')
                        
        plt.savefig(os.path.join(output_dir, '5_Categorical_BarPlot_Counts.png'), dpi=300, bbox_inches='tight')
        plt.close()

    # ==========================================
    # Plot 6: Category Differences - speed comparison per track
    # ==========================================
    print("  -> [6/6] Generating Category Differences Bar Plot...")
    if all(c in df.columns for c in ['track', 'entry_speed', 'apex_speed']):
        plt.figure(figsize=(12, 6))
        speed_means = df.groupby('track')[['entry_speed', 'apex_speed']].mean().reset_index()
        speed_melted = pd.melt(speed_means, id_vars='track', var_name='Speed_Type', value_name='Speed_KMH')
        
        sns.barplot(x='track', y='Speed_KMH', hue='Speed_Type', data=speed_melted, palette='coolwarm')
        plt.title('Differences Between Categories: Average Speeds by Track', fontsize=16, fontweight='bold')
        plt.xlabel('Track', fontsize=12)
        plt.ylabel('Average Speed (km/h)', fontsize=12)
        
        handles, labels = plt.gca().get_legend_handles_labels()
        clean_labels = [l.replace('_', ' ').title() for l in labels]
        plt.legend(handles=handles, labels=clean_labels, title='Speed Metric')
        
        plt.savefig(os.path.join(output_dir, '6_Category_Differences_BarPlot.png'), dpi=300, bbox_inches='tight')
        plt.close()

    print(f"\n--- EDA Process Complete ---")
    print(f"  [SUCCESS] All 6 visualizations have been saved to the '{output_dir}' folder!")

generate_all_eda_visualizations()