import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from matplotlib.animation import FuncAnimation


class TrajectoryPlotter:
    def __init__(self, config=None):
        default_params = {
            "subject_col": "PLAYER",
            "vlines": {"color": "black", "linestyle": "--"},
            "hlines": {"color": "black", "linestyle": "--"},
            "xlabel_params": {"fontsize": 18, "labelpad": 25},
            "ylabel_params": {"fontsize": 18, "labelpad": 25},
            "title_params": {"fontsize": 20},
            "item_line_params": {"linewidth": 4},
            "background_line_params": {"color": "gray", "alpha": 0.3},
            "vlines_text_params": {
                "ha": "center",
                "va": "top",
                "color": "black",
                "fontsize": 12,
            },
            "hlines_text_params": {
                "ha": "left",
                "va": "center",
                "color": "black",
                "fontsize": 12,
            },
            "legend_params": {
                "loc": "center left",
                "bbox_to_anchor": (1, 0.5),
                "title": "Selected Players",
            },
            "grid": True,
            "figsize": (10, 6),
        }

        self.params = default_params
        if config:
            self.params.update(config)

        self.fig = None
        self.ani = None

    def get_params(self):
        return self.params

    def set_params(self, **kwargs):
        self.params.update(kwargs)

    def create_smooth_line(self, x, y):
        y = np.nan_to_num(y, nan=0.0)
        x_smooth = np.linspace(x.min(), x.max(), 300)
        spl = make_interp_spline(x, y, k=3)
        y_smooth = spl(x_smooth)
        return x_smooth, y_smooth

    def plot_trajectory_data(
        self, data, column, color, alpha=1.0, linewidth=1.5, label=None
    ):
        x = np.array([bin.mid for bin in data["BIN"]])
        y = data[column].values
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
        df,
        selected_items,
        colors,
        v_lines={},
        h_lines={},
        column="normalized_player_shots_relative_to_league",
        hide_yticks=False,
        xlabel="Distance from Basket (meters)",
        ylabel="Field Goals",
        title="Normalized Field Goals Relative to Rest of Euroleague 23/24",
    ):
        self.fig = plt.figure(figsize=self.params["figsize"])

        for item in df[self.params["subject_col"]].unique():
            if item not in selected_items:
                item_data = df[df[self.params["subject_col"]] == item]
                self.plot_trajectory_data(
                    item_data, column, **self.params["background_line_params"]
                )

        for item in selected_items:
            item_data = df[df[self.params["subject_col"]] == item]
            color = colors[selected_items.index(item)]
            self.plot_trajectory_data(
                item_data,
                column,
                color=color,
                **self.params["item_line_params"],
                label=item,
            )

        if v_lines:
            for vline, label in v_lines.items():
                plt.axvline(x=vline, **self.params["vlines"])
                plt.text(
                    vline,
                    plt.ylim()[0] - 0.1,
                    label,
                    **self.params["vlines_text_params"],
                )

        if h_lines:
            for hline, label in h_lines.items():
                plt.axhline(y=hline, **self.params["hlines"])
                plt.text(
                    plt.xlim()[0] - 0.1,
                    hline,
                    label,
                    **self.params["hlines_text_params"],
                )

        plt.xlabel(xlabel, **self.params["xlabel_params"])
        plt.ylabel(ylabel, **self.params["ylabel_params"])
        plt.title(title, **self.params["title_params"])
        plt.grid(self.params["grid"])

        if hide_yticks:
            plt.gca().yaxis.set_ticks([])

        plt.legend(**self.params["legend_params"])
        plt.tight_layout()

        plt.xticks(fontsize=12)
        plt.gca().xaxis.set_tick_params(labelsize=12)
        plt.subplots_adjust(bottom=0.2)

        plt.show()

    def plot_trajectory_animated(
        self,
        df,
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
        self.fig, ax = plt.subplots(figsize=self.params["figsize"])

        # Plot all players in gray with low opacity
        for player in df[self.params["subject_col"]].unique():
            if player not in selected_players:
                player_data = df[df[self.params["subject_col"]] == player]
                self.plot_trajectory_data(
                    player_data, column, **self.params["background_line_params"]
                )

        lines = []
        for player in selected_players:
            (line,) = ax.plot(
                [],
                [],
                label=player,
                color=colors[selected_players.index(player)],
                **self.params["item_line_params"],
            )
            lines.append(line)

        def init():
            ax.set_xlim(0, max(bin.mid for bin in df["BIN"]))
            ax.set_ylim(df[column].min() - 0.2, df[column].max() + 0.2)
            ax.set_xlabel(xlabel, **self.params["xlabel_params"])
            ax.set_ylabel(ylabel, **self.params["ylabel_params"])
            ax.set_title(title, **self.params["title_params"])
            ax.grid(self.params["grid"])
            if hide_yticks:
                ax.yaxis.set_ticks([])

            if v_lines:
                for vline, label in v_lines.items():
                    plt.axvline(x=vline, **self.params["vlines"])
                    plt.text(
                        vline,
                        ax.get_ylim()[0] - 0.1,
                        label,
                        **self.params["vlines_text_params"],
                    )

            if h_lines:
                for hline, label in h_lines.items():
                    plt.axhline(y=hline, **self.params["hlines"])
                    plt.text(
                        ax.get_xlim()[0] - 0.1,
                        hline,
                        label,
                        **self.params["hlines_text_params"],
                    )

            return lines

        total_frames = frames_per_player * len(selected_players)

        def update(frame):
            player_index = frame // frames_per_player
            local_frame = frame % frames_per_player
            if player_index < len(selected_players):
                line = lines[player_index]
                player = selected_players[player_index]
                player_data = df[df[self.params["subject_col"]] == player]
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

        plt.legend(**self.params["legend_params"])
        plt.tight_layout()
        plt.close()

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


if __name__ == "__main__":
    pass
# TODO:
# 1. Separate computation logic from plotting logic [x]
# 2. Add docstrings to functions []
# 3. Add type hints to functions []
# 4. Add class - config, setter, getter, [x]
# 5. Add hline to plots [x]
# 6. make the plot generalizable to any dataset and column names [x]
# 7. make redundant code less redundant
