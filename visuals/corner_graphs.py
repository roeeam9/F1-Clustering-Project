import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import numpy as np
import os

def plot_corner_validation_map(track_name, file_path='data/processed_data/New_Qualifying_fastest_laps_telemetry_with_corners.csv'):
    
    absolute_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        print(f"[!] Error: File not found at {absolute_path}")
        return

    df = pd.read_csv(file_path)
    track_data = df[df['Track'] == track_name]
    
    if track_data.empty:
        print(f"[!] No data found for track: {track_name}")
        return

    # Extract single lap
    first_driver = track_data['driver_number'].iloc[0]
    single_lap = track_data[track_data['driver_number'] == first_driver].copy()

    single_lap['x'] = pd.to_numeric(single_lap['x'], errors='coerce')
    single_lap['y'] = pd.to_numeric(single_lap['y'], errors='coerce')
    
    # Parses booleans correctly in case the file stores them as text
    def safe_bool(val):
        if isinstance(val, bool): return val
        if isinstance(val, str): return val.strip().lower() in ['true', '1', 't']
        return bool(val)
        
    single_lap['is_corner'] = single_lap['is_corner'].apply(safe_bool)
    single_lap = single_lap.dropna(subset=['x', 'y'])

    # ========================================================
    # Clean the data at the lap boundaries
    # The start/finish line is always on a straight, so the telemetry points 
    # at the start and end of the lap are forced to False
    # ========================================================
    if track_name=='Monza':
        if len(single_lap) > 100:  # make sure there is enough data
            corner_col_idx = single_lap.columns.get_loc('is_corner')
        # 40 rows is roughly 3-4 seconds of driving at high speed
            single_lap.iloc[:30, corner_col_idx] = False
            single_lap.iloc[-5:, corner_col_idx] = False
    # ========================================================

    # Close the loop
    single_lap = pd.concat([single_lap, single_lap.iloc[[0]]], ignore_index=True)

    # Apply track rotation
    if track_name in ['Monza', 'Spa']:
        temp_x = single_lap['x'].copy()
        single_lap['x'] = -single_lap['y']
        single_lap['y'] = temp_x
        
    elif track_name == 'Suzuka':
        angle = np.radians(45)
        c, s = np.cos(angle), np.sin(angle)
        temp_x, temp_y = single_lap['x'].copy(), single_lap['y'].copy()
        single_lap['x'] = temp_x * c - temp_y * s
        single_lap['y'] = temp_x * s + temp_y * c

    print(f"Creating Corner Validation Map for {track_name} (Driver {first_driver})...")

    # Prepare data for LineCollection
    x = single_lap['x'].values
    y = single_lap['y'].values
    is_corner = single_lap['is_corner'].values

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Set segment colors based on the boolean column
    segment_colors = ['#8B4513' if corner else '#E0E0E0' for corner in is_corner[:-1]]

    # Create the plot
    fig, ax = plt.subplots(figsize=(16, 12))
    
    lc = LineCollection(segments, colors=segment_colors, linewidths=10, 
                        capstyle='round', joinstyle='round', zorder=5)
    ax.add_collection(lc)
    
    # Theme Setup 
    bg_color = 'white'
    ax.set_facecolor(bg_color)
    fig.patch.set_facecolor(bg_color)
    
    ax.set_title(f"F1 Telemetry: {track_name} Corner Validation", fontsize=20, fontweight='bold', color='#111111')
    ax.set_xlabel("X Position (meters)", color='#333333')
    ax.set_ylabel("Y Position (meters)", color='#333333')

    ax.axis('equal') 
    ax.tick_params(colors='#333333')
    ax.grid(True, linestyle='-', alpha=0.15, color='gray')
    
    margin = 5000
    ax.set_xlim(x.min() - margin, x.max() + margin)
    ax.set_ylim(y.min() - margin, y.max() + margin)

    # --- Custom Legend ---
    legend_elements = [
        Line2D([0], [0], color='#8B4513', lw=8, label='Corner (is_corner = True)'),
        Line2D([0], [0], color='#E0E0E0', lw=8, label='Straight (is_corner = False)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', 
              fontsize=14, facecolor='white', edgecolor='#CCCCCC', labelcolor='#333333')

    plt.tight_layout(pad=2.5)
    plt.savefig('corner_validation_map.png', dpi=300, bbox_inches='tight')
    plt.show()

# Run the validation
#plot_corner_validation_map('Monza')
plot_corner_validation_map('Singapore')
#plot_corner_validation_map('Spa')
#plot_corner_validation_map('Suzuka')