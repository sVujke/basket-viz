import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline


# df["distance"] = df.apply(
#     lambda row: np.sqrt(row["COORD_X"] ** 2 + row["COORD_Y"] ** 2), axis=1
# )
# df["ACTION_RESULT"] = df["ID_ACTION"].apply(
#     lambda x: "hit" if x in ["2FGM", "3FGM", "FTM"] else "miss"
# )

# # Filter out players that appear less than 200 times
# player_counts = df["PLAYER"].value_counts()
# df = df[df["PLAYER"].isin(player_counts[player_counts >= 200].index)]

# # Convert distance from cm to meters
# df["DISTANCE_METERS"] = df["distance"] / 100
# df = df[df["DISTANCE_METERS"] < 10]

# # Create bins every 0.5 meters
# bins = np.arange(0, 10, 0.5)
# bin_labels = pd.IntervalIndex.from_breaks(bins, closed="right")
# df["BIN"] = pd.cut(df["DISTANCE_METERS"], bins, labels=bin_labels)

# # Calculate league average efficiency for each bin
# league_efficiency = (
#     df.groupby("BIN")["ACTION_RESULT"]
#     .apply(lambda x: (x == "hit").sum() / len(x))
#     .reindex(bin_labels, fill_value=0)
#     .reset_index()
# )


def create_smooth_line(x, y):
    # Replace NaN values with zero
    y = np.nan_to_num(y, nan=0.0)
    x_smooth = np.linspace(x.min(), x.max(), 300)
    spl = make_interp_spline(x, y, k=3)  # k=3 for cubic spline
    y_smooth = spl(x_smooth)
    return x_smooth, y_smooth


def plot_player_trajectory(player_data, column, color, alpha=1.0, linewidth=1.5):
    x = np.array([bin.mid for bin in player_data["BIN"]])
    y = player_data[column].values

    # Create smooth lines using spline interpolation
    x_smooth, y_smooth = create_smooth_line(x, y)

    plt.plot(x_smooth, y_smooth, color=color, alpha=alpha, linewidth=linewidth)


def plot_trajectory(
    df,
    selected_players,
    colors,
    v_lines={},
    column="normalized_player_shots_relative_to_league",
    h_lines={},
    hide_yticks=False,
):
    plt.figure(figsize=(10, 6))

    # Plot all players in gray with low opacity
    for player in df["PLAYER"].unique():
        if player not in selected_players:
            player_data = df[df["PLAYER"] == player]
            plot_player_trajectory(player_data, column, color="gray", alpha=0.3)

    # Plot selected players in chosen colors
    for player in selected_players:
        player_data = df[df["PLAYER"] == player]
        color = colors[selected_players.index(player)]
        plot_player_trajectory(player_data, column, color=color, linewidth=4)

    if v_lines:
        for vline, label in v_lines.items():
            plt.axvline(x=vline, color="black", linestyle="--")
            plt.text(
                vline,
                plt.ylim()[0] - 0.1,
                label,
                ha="center",
                va="top",
                color="black",
                fontsize=12,
            )
    if h_lines:
        for hline, label in h_lines.items():
            plt.axhline(y=hline, color="black", linestyle="--")
            plt.text(
                plt.xlim()[0] - 0.1,
                hline,
                label,
                ha="left",
                va="center",
                color="black",
                fontsize=12,
            )

    plt.xlabel("Distance from Rim (meters)", fontsize=18, labelpad=25)
    plt.ylabel("Normalized Efficiency")
    plt.title("Normalized Efficiency Binned per Every Half Meter")
    plt.grid(True)

    if hide_yticks:
        plt.gca().yaxis.set_ticks([])

    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()

    # Increase font size and adjust margins for x-axis labels
    plt.xticks(fontsize=12)
    plt.gca().xaxis.set_tick_params(labelsize=12)
    plt.subplots_adjust(bottom=0.2)

    plt.show()


# Define selected players and their colors
selected_players = ["NEDOVIC, NEMANJA", "LESSORT, MATHIAS"]
colors = ["blue", "green"]

# Plot efficiency

if __name__ == "__main__":
    pass
# TODO:
# 1. Separate computation logic from plotting logic
# 2. Add docstrings to functions
# 3. Add type hints to functions
# 4. Add class - config, setter, getter,
# 5. Add hline to plots
# 6. make the plot generalizable to any dataset and column names
