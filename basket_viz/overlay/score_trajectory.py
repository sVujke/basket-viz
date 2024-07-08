import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline


df = pd.read_csv('/Users/stef/Documents/dev/basket-viz/notebooks/data/shot_data_2022.csv')
df['distance'] = df.apply(lambda row: np.sqrt(row['COORD_X']**2 + row['COORD_Y']**2), axis=1)
df['ACTION_RESULT'] = df["ID_ACTION"].apply(lambda x: 'hit' if x in ['2FGM', '3FGM', 'FTM'] else 'miss')

# Filter out players that appear less than 200 times
player_counts = df['PLAYER'].value_counts()
df = df[df['PLAYER'].isin(player_counts[player_counts >= 200].index)]

# Convert distance from cm to meters
df['DISTANCE_METERS'] = df['distance'] / 100
df = df[df['DISTANCE_METERS'] < 10]

# Create bins every 0.5 meters
bins = np.arange(0, 10, 0.5)
bin_labels = pd.IntervalIndex.from_breaks(bins, closed='right')
df['BIN'] = pd.cut(df['DISTANCE_METERS'], bins, labels=bin_labels)

# Calculate league average efficiency for each bin
league_efficiency = df.groupby('BIN')['ACTION_RESULT'].apply(lambda x: (x == 'hit').sum() / len(x)).reindex(bin_labels, fill_value=0).reset_index()

# Function to calculate and plot efficiency for each player
def plot_efficiency(df, league_efficiency, selected_players, colors):
    plt.figure(figsize=(10, 6))

    all_players = df['PLAYER'].unique()
    
    for player in all_players:
        player_df = df[df['PLAYER'] == player]
        
        # Calculate efficiency for each bin
        player_efficiency = player_df.groupby('BIN')['ACTION_RESULT'].apply(lambda x: (x == 'hit').sum() / len(x)).reindex(bin_labels, fill_value=0).reset_index()
        
        # Normalize player efficiency against league average efficiency
        player_efficiency['NORMALIZED_EFFICIENCY'] = player_efficiency['ACTION_RESULT'] / league_efficiency['ACTION_RESULT']
        # Normalize player efficiency against league average efficiency

# Normalize the NORMALIZED_EFFICIENCY to a 0 to 1 range
        player_efficiency['NORMALIZED_EFFICIENCY'] = (player_efficiency['NORMALIZED_EFFICIENCY'] - player_efficiency['NORMALIZED_EFFICIENCY'].min()) / (player_efficiency['NORMALIZED_EFFICIENCY'].max() - player_efficiency['NORMALIZED_EFFICIENCY'].min())

        
        # Prepare data for smooth plotting
        x = np.array([bin.mid for bin in player_efficiency['index']])
        y = player_efficiency['NORMALIZED_EFFICIENCY'].values
        
        # Replace NaN values with zero
        y = np.nan_to_num(y, nan=0.0)
        
        # Create smooth lines using spline interpolation
        x_smooth = np.linspace(x.min(), x.max(), 200)
        spl = make_interp_spline(x, y, k=3)  # k=3 for cubic spline
        y_smooth = spl(x_smooth)
        
        # Clip the interpolated values to be between 0 and 2 for better visualization
        y_smooth = np.clip(y_smooth, 0, 2)
        
        # Plot all players in gray with low opacity
        if player not in selected_players:
            plt.plot(x_smooth, y_smooth, color='gray', alpha=0.3)
        else:
            # Plot selected players in chosen colors
            color = colors[selected_players.index(player)]
            plt.plot(x_smooth, y_smooth, label=player, color=color, linewidth=2)
            print(player_efficiency)

    plt.ylim(-0.25, 1.25)
    plt.xlabel('Distance from Rim (meters)')
    plt.ylabel('Normalized Efficiency')
    plt.title('Normalized Efficiency Binned per Every Half Meter')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Define selected players and their colors
selected_players = ['NEDOVIC, NEMANJA', 'LESSORT, MATHIAS']
colors = ['blue', 'green']

# Plot efficiency
plot_efficiency(df, league_efficiency, selected_players, colors)
