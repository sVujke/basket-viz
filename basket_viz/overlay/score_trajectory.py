import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline


# # df["distance"] = df.apply(
# #     lambda row: np.sqrt(row["COORD_X"] ** 2 + row["COORD_Y"] ** 2), axis=1
# # )
# # df["ACTION_RESULT"] = df["ID_ACTION"].apply(
# #     lambda x: "hit" if x in ["2FGM", "3FGM", "FTM"] else "miss"
# # )

# # # Filter out players that appear less than 200 times
# # player_counts = df["PLAYER"].value_counts()
# # df = df[df["PLAYER"].isin(player_counts[player_counts >= 200].index)]

# # # Convert distance from cm to meters
# # df["DISTANCE_METERS"] = df["distance"] / 100
# # df = df[df["DISTANCE_METERS"] < 10]

# # # Create bins every 0.5 meters
# # bins = np.arange(0, 10, 0.5)
# # bin_labels = pd.IntervalIndex.from_breaks(bins, closed="right")
# # df["BIN"] = pd.cut(df["DISTANCE_METERS"], bins, labels=bin_labels)

# # # Calculate league average efficiency for each bin
# # league_efficiency = (
# #     df.groupby("BIN")["ACTION_RESULT"]
# #     .apply(lambda x: (x == "hit").sum() / len(x))
# #     .reindex(bin_labels, fill_value=0)
# #     .reset_index()
# # )


# def create_smooth_line(x, y):
#     # Replace NaN values with zero
#     y = np.nan_to_num(y, nan=0.0)
#     x_smooth = np.linspace(x.min(), x.max(), 300)
#     spl = make_interp_spline(x, y, k=3)  # k=3 for cubic spline
#     y_smooth = spl(x_smooth)
#     return x_smooth, y_smooth


# def plot_player_trajectory(
#     player_data, column, color, alpha=1.0, linewidth=1.5, label=None
# ):
#     x = np.array([bin.mid for bin in player_data["BIN"]])
#     y = player_data[column].values

#     # Create smooth lines using spline interpolation
#     x_smooth, y_smooth = create_smooth_line(x, y)

#     plt.plot(
#         x_smooth, y_smooth, color=color, alpha=alpha, linewidth=linewidth, label=label
#     )


# def plot_trajectory(
#     df,
#     selected_players,
#     colors,
#     v_lines={},
#     column="normalized_player_shots_relative_to_league",
#     h_lines={},
#     hide_yticks=False,
# ):
#     plt.figure(figsize=(10, 6))

#     # Plot all players in gray with low opacity
#     for player in df["PLAYER"].unique():
#         if player not in selected_players:
#             player_data = df[df["PLAYER"] == player]
#             plot_player_trajectory(player_data, column, color="gray", alpha=0.3)

#     # Plot selected players in chosen colors
#     for player in selected_players:
#         player_data = df[df["PLAYER"] == player]
#         color = colors[selected_players.index(player)]
#         plot_player_trajectory(
#             player_data, column, color=color, linewidth=4, label=player
#         )

#     if v_lines:
#         for vline, label in v_lines.items():
#             plt.axvline(x=vline, color="black", linestyle="--")
#             plt.text(
#                 vline,
#                 plt.ylim()[0] - 0.1,
#                 label,
#                 ha="center",
#                 va="top",
#                 color="black",
#                 fontsize=12,
#             )
#     if h_lines:
#         for hline, label in h_lines.items():
#             plt.axhline(y=hline, color="black", linestyle="--")
#             plt.text(
#                 plt.xlim()[0] - 0.1,
#                 hline,
#                 label,
#                 ha="left",
#                 va="center",
#                 color="black",
#                 fontsize=12,
#             )

#     plt.xlabel("Distance from Basket (meters)", fontsize=18, labelpad=25)
#     plt.ylabel("Field Goals")
#     plt.title(
#         "Normalized Field Goals Relative to Rest of Euroleague 23/24", fontsize=20
#     )
#     plt.grid(True)

#     if hide_yticks:
#         plt.gca().yaxis.set_ticks([])

#     plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Selected Players")
#     plt.tight_layout()

#     # Increase font size and adjust margins for x-axis labels
#     plt.xticks(fontsize=12)
#     plt.gca().xaxis.set_tick_params(labelsize=12)
#     plt.subplots_adjust(bottom=0.2)

#     plt.show()


# # Define selected players and their colors
# selected_players = ["NEDOVIC, NEMANJA", "LESSORT, MATHIAS"]
# colors = ["blue", "green"]

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from matplotlib.animation import FuncAnimation


class PlotConfig:
    def __init__(self, fontsize=12, color="gray", linewidth=1.5, alpha=1.0):
        self.fontsize = fontsize
        self.color = color
        self.linewidth = linewidth
        self.alpha = alpha


class TrajectoryPlotter:
    def __init__(self, df, config=PlotConfig()):
        self.df = df
        self.config = config
        self.fig = None
        self.ani = None

    def create_smooth_line(self, x, y):
        # Replace NaN values with zero
        y = np.nan_to_num(y, nan=0.0)
        x_smooth = np.linspace(x.min(), x.max(), 300)
        spl = make_interp_spline(x, y, k=3)  # k=3 for cubic spline
        y_smooth = spl(x_smooth)
        return x_smooth, y_smooth

    def plot_trajectory_data(
        self, data, column, color, alpha=1.0, linewidth=1.5, label=None
    ):
        x = np.array([bin.mid for bin in data["BIN"]])
        y = data[column].values

        # Create smooth lines using spline interpolation
        x_smooth, y_smooth = self.create_smooth_line(x, y)

        plt.plot(
            x_smooth,
            y_smooth,
            color=color,
            alpha=alpha,
            linewidth=linewidth,
            label=label,
        )

    def plot_trajectory(
        self,
        selected_players,
        colors,
        v_lines={},
        h_lines={},
        column="normalized_player_shots_relative_to_league",
        hide_yticks=False,
        xlabel="Distance from Basket (meters)",
        ylabel="Field Goals",
        title="Normalized Field Goals Relative to Rest of Euroleague 23/24",
    ):
        self.fig = plt.figure(figsize=(10, 6))

        # Plot all players in gray with low opacity
        for player in self.df["PLAYER"].unique():
            if player not in selected_players:
                player_data = self.df[self.df["PLAYER"] == player]
                self.plot_trajectory_data(player_data, column, color="gray", alpha=0.3)

        # Plot selected players in chosen colors
        for player in selected_players:
            player_data = self.df[self.df["PLAYER"] == player]
            color = colors[selected_players.index(player)]
            self.plot_trajectory_data(
                player_data, column, color=color, linewidth=4, label=player
            )

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

        plt.xlabel(xlabel, fontsize=18, labelpad=25)
        plt.ylabel(ylabel)
        plt.title(title, fontsize=20)
        plt.grid(True)

        if hide_yticks:
            plt.gca().yaxis.set_ticks([])

        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Selected Players")
        plt.tight_layout()

        # Increase font size and adjust margins for x-axis labels
        plt.xticks(fontsize=12)
        plt.gca().xaxis.set_tick_params(labelsize=12)
        plt.subplots_adjust(bottom=0.2)

        plt.show()

    # def plot_trajectory_animated(
    #     self,
    #     selected_players,
    #     colors,
    #     column="normalized_player_shots_relative_to_league",
    #     hide_yticks=False,
    #     xlabel="Distance from Basket (meters)",
    #     ylabel="Field Goals",
    #     title="Normalized Field Goals Relative to Rest of Euroleague 23/24",
    # ):
    #     self.fig, ax = plt.subplots(figsize=(10, 6))

    #     # Plot all players in gray with low opacity
    #     for player in self.df["PLAYER"].unique():
    #         if player not in selected_players:
    #             player_data = self.df[self.df["PLAYER"] == player]
    #             self.plot_trajectory_data(player_data, column, color="gray", alpha=0.3)

    #     lines = []
    #     for player in selected_players:
    #         (line,) = ax.plot(
    #             [],
    #             [],
    #             label=player,
    #             color=colors[selected_players.index(player)],
    #             linewidth=4,
    #         )
    #         lines.append(line)

    #     def init():
    #         ax.set_xlim(0, max(bin.mid for bin in self.df["BIN"]))
    #         ax.set_ylim(self.df[column].min(), self.df[column].max())
    #         ax.set_xlabel(xlabel, fontsize=18, labelpad=25)
    #         ax.set_ylabel(ylabel)
    #         ax.set_title(title, fontsize=20)
    #         ax.grid(True)
    #         if hide_yticks:
    #             ax.yaxis.set_ticks([])
    #         return lines

    #     def update(frame):
    #         for line, player in zip(lines, selected_players):
    #             player_data = self.df[self.df["PLAYER"] == player]
    #             x = np.array([bin.mid for bin in player_data["BIN"]])
    #             y = player_data[column].values
    #             x_smooth, y_smooth = self.create_smooth_line(x, y)
    #             line.set_data(x_smooth[:frame], y_smooth[:frame])
    #         return lines

    #     self.ani = FuncAnimation(
    #         self.fig, update, frames=300, init_func=init, blit=True, repeat=False
    #     )
    #     plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Selected Players")
    #     plt.tight_layout()
    #     plt.show()

    def plot_trajectory_animated(
        self,
        selected_players,
        colors,
        column="normalized_player_shots_relative_to_league",
        v_lines=None,
        h_lines=None,
        hide_yticks=False,
        xlabel="Distance from Basket (meters)",
        ylabel="Field Goals",
        title="Normalized Field Goals Relative to Rest of Euroleague 23/24",
        frames_per_player=300,
        speed=1,
    ):
        self.fig, ax = plt.subplots(figsize=(10, 6))

        # Plot all players in gray with low opacity
        for player in self.df["PLAYER"].unique():
            if player not in selected_players:
                player_data = self.df[self.df["PLAYER"] == player]
                self.plot_trajectory_data(player_data, column, color="gray", alpha=0.3)

        lines = []
        for player in selected_players:
            (line,) = ax.plot(
                [],
                [],
                label=player,
                color=colors[selected_players.index(player)],
                linewidth=4,
            )
            lines.append(line)

        def init():
            ax.set_xlim(0, max(bin.mid for bin in self.df["BIN"]))
            ax.set_ylim(self.df[column].min() - 0.2, self.df[column].max() + 0.2)
            ax.set_xlabel(xlabel, fontsize=18, labelpad=25)
            ax.set_ylabel(ylabel)
            ax.set_title(title, fontsize=20)
            ax.grid(True)
            if hide_yticks:
                ax.yaxis.set_ticks([])

            if v_lines:
                for vline, label in v_lines.items():
                    plt.axvline(x=vline, color="black", linestyle="--")
                    plt.text(
                        vline,
                        ax.get_ylim()[0] - 0.1,
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
                        ax.get_xlim()[0] - 0.1,
                        hline,
                        label,
                        ha="left",
                        va="center",
                        color="black",
                        fontsize=12,
                    )

            return lines

        total_frames = frames_per_player * len(selected_players)

        def update(frame):
            player_index = frame // frames_per_player
            local_frame = frame % frames_per_player
            if player_index < len(selected_players):
                line = lines[player_index]
                player = selected_players[player_index]
                player_data = self.df[self.df["PLAYER"] == player]
                x = np.array([bin.mid for bin in player_data["BIN"]])
                y = player_data[column].values
                x_smooth, y_smooth = self.create_smooth_line(x, y)
                line.set_data(x_smooth[:local_frame], y_smooth[:local_frame])
            return lines

        interval = 1000 / speed  # Interval in milliseconds, adjusted by speed
        self.ani = FuncAnimation(
            self.fig,
            update,
            frames=total_frames,
            init_func=init,
            blit=True,
            repeat=False,
            interval=interval,
        )

        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), title="Selected Players")
        plt.tight_layout()
        plt.show()

    def save_plot(self, directory="output", file_name="trajectory", file_format=None):
        if not os.path.exists(directory):
            os.makedirs(directory)

        if self.ani is not None:
            if file_format is None:
                file_format = "mp4"
            full_path = os.path.join(directory, f"{file_name}.{file_format}")
            if file_format == "gif":
                self.ani.save(full_path, writer="pillow")
            elif file_format == "mp4":
                self.ani.save(full_path, writer="ffmpeg")
            else:
                raise ValueError(
                    f"Unsupported file format for animation: {file_format}"
                )
            print(f"Saved animation to {full_path}")

        elif self.fig is not None and self.ani is None:
            if file_format is None:
                file_format = "png"
            full_path = os.path.join(directory, f"{file_name}.{file_format}")
            self.fig.savefig(full_path)
            print(f"Saved figure to {full_path}")

        else:
            raise ValueError("No plot or animation available to save.")


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
