import pandas as pd 
import os

def generate_pure_fastest_laps():
    print("Processing the data to build the golden-laps file (including lap time)...")
    
    raw_data_dir = 'raw_data'
    processed_data_dir = 'processed_data'
    output_file = os.path.join(processed_data_dir, 'pure_fastest_laps_telemetry.csv')
    
    os.makedirs(processed_data_dir, exist_ok=True)
    
    tracks = ['Monza', 'Singapore', 'Spa', 'Suzuka']
    all_pure_data = []
    
    for track in tracks:
        print(f"Processing track: {track}...")
        
        # Load the files
        laps_df = pd.read_csv(os.path.join(raw_data_dir, f'{track}_raw_laps.csv'))
        loc_df = pd.read_csv(os.path.join(raw_data_dir, f'{track}_raw_location.csv'))
        tel_df = pd.read_csv(os.path.join(raw_data_dir, f'{track}_raw_telemetry.csv'))
        
        # Tolerant ISO8601 parsing, to avoid crashes on millisecond formats
        laps_df['date_start'] = pd.to_datetime(laps_df['date_start'], format='ISO8601')
        loc_df['date'] = pd.to_datetime(loc_df['date'], format='ISO8601')
        tel_df['date'] = pd.to_datetime(tel_df['date'], format='ISO8601')
        
        # 1. Drop pit-out laps
        valid_laps = laps_df[~laps_df['is_pit_out_lap'].isin([True, 'True', 'true', 1])].copy()
        
        # 2. Detect and drop pit-in laps 
        laps_df['next_lap_is_pit_out'] = laps_df.groupby('driver_number')['is_pit_out_lap'].shift(-1)
        pit_in_mask = laps_df['next_lap_is_pit_out'].isin([True, 'True', 'true', 1]) | laps_df['lap_duration'].isna()
        
        # Combine the filters
        valid_laps = valid_laps[~valid_laps.index.isin(laps_df[pit_in_mask].index)]
        
        # 3. Pick the fastest clean lap (pure lap) for each driver
        fastest_laps_indices = valid_laps.groupby('driver_number')['lap_duration'].idxmin()
        fastest_laps = valid_laps.loc[fastest_laps_indices]
        
        # Merge the telemetry and GPS data for the selected pure laps
        for _, lap in fastest_laps.iterrows():
            driver = lap['driver_number']
            
            start_time = lap['date_start']
            end_time = start_time + pd.to_timedelta(lap['lap_duration'], unit='s')
            
            # Filter to the relevant time window and sort by time
            driver_loc = loc_df[(loc_df['driver_number'] == driver) & 
                                (loc_df['date'] >= start_time) & 
                                (loc_df['date'] <= end_time)].sort_values('date')
                                
            driver_tel = tel_df[(tel_df['driver_number'] == driver) & 
                                (tel_df['date'] >= start_time) & 
                                (tel_df['date'] <= end_time)].sort_values('date')
            
            if driver_loc.empty or driver_tel.empty:
                continue
                
            # Merge on the nearest timestamp
            merged_lap = pd.merge_asof(driver_tel, driver_loc[['date', 'x', 'y']], 
                                       on='date', direction='nearest')
            
            merged_lap['Track'] = track
            
            # -- change starts here --
            # Attach the lap time to every row before saving
            merged_lap['lap_duration'] = lap['lap_duration']
            
            # Keep the relevant columns (lap_duration added to the list)
            final_columns = ['Track', 'driver_number', 'lap_duration', 'x', 'y', 'speed', 'brake', 'throttle', 'n_gear']
            merged_lap = merged_lap[final_columns]
            
            all_pure_data.append(merged_lap)
            
    # Save the final file
    if all_pure_data:
        final_df = pd.concat(all_pure_data, ignore_index=True)
        final_df.to_csv(output_file, index=False)
        print(f"Processing finished. File saved to: {output_file}")
        return final_df
    else:
        print("No valid data found to merge.")
        return None


generate_pure_fastest_laps()