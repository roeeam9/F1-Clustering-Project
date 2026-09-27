import pandas as pd
import matplotlib.pyplot as plt
from archive.access_to_api import OpenF1Client

def plot_racing_lines_robust():
    print("Loading corner data...")
    api = OpenF1Client()
    df_corners = pd.read_csv("../archive/F1_4_Races_All_Corners.csv")
    df_corners['start_time'] = pd.to_datetime(df_corners['start_time'], format='ISO8601')

    # Focus on a single race (e.g. 9558 - Silverstone) to save API calls
    target_session = 9558
    df_session = df_corners[df_corners['session_key'] == target_session]

    # Pick 6 different corners from that race
    # Drop duplicate timestamps so the same corner is not taken twice
    df_sample = df_session.drop_duplicates(subset=['start_time']).iloc[[10, 20, 30, 40, 50, 60]]

    # Pick 3 notable drivers to keep the plot readable (Hamilton, Verstappen, Leclerc)
    drivers = [44, 1, 16] 
    colors = ['#00D2BE', '#FF8700', '#DC0000']
    names = ['Hamilton (44)', 'Verstappen (1)', 'Leclerc (16)']

    # ==========================================
    # Fetch the data once for the whole race instead of once per corner
    # ==========================================
    print("Fetching location data (This will take a few seconds but ensures no crashes)...")
    loc_data_cache = {}
    
    for drv in drivers:
        print(f" -> Downloading path for driver {drv}...")
        df_loc = api.get_location(target_session, drv)
        if not df_loc.empty:
            df_loc['date'] = pd.to_datetime(df_loc['date'], format='ISO8601')
            loc_data_cache[drv] = df_loc

    # ==========================================
    # Plotting
    # ==========================================
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for i, (_, corner) in enumerate(df_sample.iterrows()):
        ax = axes[i]
        start_t = corner['start_time']
        
        # Time window: one second before the corner and four seconds after
        t_start = start_t - pd.Timedelta(seconds=1)
        t_end = start_t + pd.Timedelta(seconds=4)

        # Draw the grey "asphalt" from the first driver's data
        base_drv = drivers[0]
        if base_drv in loc_data_cache:
            df_base = loc_data_cache[base_drv]
            df_base_zoom = df_base[(df_base['date'] >= t_start) & (df_base['date'] <= t_end)]
            if not df_base_zoom.empty:
                # Thick line standing in for the track surface
                ax.plot(df_base_zoom['x'], df_base_zoom['y'], color='#E8E8E8', linewidth=30, solid_capstyle='round', zorder=1)

        # Draw each driver's racing line
        for drv, color, name in zip(drivers, colors, names):
            if drv in loc_data_cache:
                df_drv = loc_data_cache[drv]
                df_zoom = df_drv[(df_drv['date'] >= t_start) & (df_drv['date'] <= t_end)]
                
                if not df_zoom.empty:
                    ax.plot(df_zoom['x'], df_zoom['y'], color=color, linewidth=2.5, 
                            label=name if i == 0 else "", zorder=2)

        ax.set_title(f"Corner {i+1} | Apex Speed: {int(corner['apex_speed'])} km/h", fontsize=14)
        ax.axis('equal') # keeps the track from being distorted
        ax.set_xticks([]) # hide the axis numbers for a cleaner look
        ax.set_yticks([])

    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=3, fontsize=14)
    plt.suptitle(f"Racing Lines Comparison - Session {target_session}", fontsize=22, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_racing_lines_robust()