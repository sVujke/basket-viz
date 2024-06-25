import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import pandas as pd
from basket_viz.relationships import team_configs


def calculate_shots_summary(data):
    shots_summary = (
        data.groupby("PLAYER")["ID_ACTION"].value_counts().unstack(fill_value=0)
    )
    shots_summary["Total_Shots"] = shots_summary.sum(axis=1)
    shots_summary["Shots_Made"] = shots_summary.get("2FGM", 0) + shots_summary.get(
        "3FGM", 0
    )
    shots_summary["Shots_Missed"] = (
        shots_summary.get("2FGA", 0)
        + shots_summary.get("3FGA", 0)
        - shots_summary["Shots_Made"]
    )
    return shots_summary[["Total_Shots", "Shots_Made"]].reset_index()


def calculate_average_line(data):
    overall_scatter_data = (
        data.groupby("PLAYER")["ID_ACTION"].value_counts().unstack(fill_value=0)
    )
    overall_scatter_data["Total_Shots"] = overall_scatter_data.sum(axis=1)
    overall_scatter_data["Shots_Made"] = overall_scatter_data.get(
        "2FGM", 0
    ) + overall_scatter_data.get("3FGM", 0)
    m, b = np.polyfit(
        overall_scatter_data["Total_Shots"], overall_scatter_data["Shots_Made"], 1
    )
    return m, b


class PlotRelationship:
    # TODO
    #  make functions to override configs in memory (adhoc)
    # parametrize
    # add docstrings
    # parametrize title
    # parametrize duration frames for output
    def __init__(
        self,
        use_team_config=True,
        fig_size=(10, 6),
        export_dir="./",
        output_format="mp4",
    ):
        self.team_configs = team_configs.team_configs
        self.export_dir = export_dir
        self.output_format = output_format
        # Default configurations
        self.line = {"color": "red", "width": 2, "alpha": 0.5, "style": "-"}
        self.markers = {"s": 30, "marker": "o", "color": "blue", "alpha": 0.5}
        self.names = {
            "color": "black",
            "fontsize": 8,
            "rotation": 0,
            "ha": "center",
        }
        self.labels = {"color": "black", "fontsize": 8}
        self.background = {"color": "white"}
        self.axes = {"color": "black", "fontsize": 10, "width": 1}

        self.use_team_config = use_team_config
        self.fig_size = fig_size

    def set_line_config(self, **kwargs):
        self.line.update(kwargs)

    def set_markers_config(self, **kwargs):
        self.markers.update(kwargs)

    def set_names_config(self, **kwargs):
        self.names.update(kwargs)

    def set_labels_config(self, **kwargs):
        self.labels.update(kwargs)

    def set_background_config(self, **kwargs):
        self.background.update(kwargs)

    def set_axes_config(self, **kwargs):
        self.axes.update(kwargs)

    def get_team_config(self, team_filter):
        config = {
            "line": self.line.copy(),
            "markers": self.markers.copy(),
            "names": self.names.copy(),
            "labels": self.labels.copy(),
            "background": self.background.copy(),
            "axes": self.axes.copy(),
        }
        if team_filter and team_filter in self.team_configs:
            team_config = self.team_configs[team_filter]
            for key in team_config:
                if key in config:
                    config[key].update(team_config[key])
        return config

    def plot_animated_relationship(
        self,
        data,
        team_filter=None,
        show_high_residuals=False,
        residual_threshold=5,
        keep_players=None,
        drop_players=None,
        display_only_last_names=False,
        file_name_sufix="",
    ):

        config = (
            self.get_team_config(team_filter)
            if self.use_team_config
            else {
                "line": self.line.copy(),
                "markers": self.markers.copy(),
                "names": self.names.copy(),
                "labels": self.labels.copy(),
                "background": self.background.copy(),
                "axes": self.axes.copy(),
            }
        )

        team_data = (
            data[data["TEAM"].str.strip() == team_filter] if team_filter else data
        )
        scatter_data = calculate_shots_summary(team_data)

        m, b = calculate_average_line(data)
        scatter_data["Average_Line"] = m * scatter_data["Total_Shots"] + b
        scatter_data["Residual"] = (
            scatter_data["Shots_Made"] - scatter_data["Average_Line"]
        )

        if show_high_residuals:
            scatter_data = scatter_data[
                abs(scatter_data["Residual"]) > residual_threshold
            ]

        if drop_players:
            scatter_data = scatter_data[~scatter_data["PLAYER"].isin(drop_players)]

        if keep_players:
            scatter_data = scatter_data[scatter_data["PLAYER"].isin(keep_players)]

        scatter_data = scatter_data.sort_values(by="Shots_Made")

        fig, ax = plt.subplots(figsize=self.fig_size)
        fig.patch.set_facecolor(config["background"]["color"])
        ax.set_facecolor(config["background"]["color"])
        ax.set_xlim(0, scatter_data["Total_Shots"].max() + 20)
        ax.set_ylim(0, scatter_data["Shots_Made"].max() + 10)
        ax.set_xlabel(
            "Total Shot Attempts",
            fontsize=config["labels"]["fontsize"],
            color=config["labels"]["color"],
        )
        ax.set_ylabel(
            "Shots Made",
            fontsize=config["labels"]["fontsize"],
            color=config["labels"]["color"],
        )
        ax.plot(
            scatter_data["Total_Shots"],
            m * scatter_data["Total_Shots"] + b,
            alpha=config["line"]["alpha"],
            color=config["line"]["color"],
            linestyle=config["line"]["style"],
            linewidth=config["line"]["width"],
            label="Average Line",
        )
        legend = ax.legend(
            # TODO parametrize this
            loc="upper left",
            prop={"size": 14},
            facecolor=config["background"]["color"],
        )
        ax.grid(False)

        scatter = ax.scatter([], [], **config["markers"])

        for spine in ax.spines.values():
            spine.set_color(config["axes"]["color"])
            spine.set_linewidth(config["axes"]["width"])

        ax.tick_params(
            axis="x",
            colors=config["axes"]["color"],
            labelsize=config["axes"]["fontsize"],
        )
        ax.tick_params(
            axis="y",
            colors=config["axes"]["color"],
            labelsize=config["axes"]["fontsize"],
        )

        def update(frame):
            scatter.set_offsets(
                scatter_data[["Total_Shots", "Shots_Made"]].values[:frame]
            )
            for i, player in scatter_data.iloc[:frame].iterrows():
                name = (
                    player["PLAYER"].split(",")[0]
                    if display_only_last_names
                    else player["PLAYER"]
                )
                ax.text(
                    player["Total_Shots"],
                    player["Shots_Made"],
                    name,
                    fontsize=config["names"]["fontsize"],
                    alpha=0.7,
                    rotation=config["names"]["rotation"],
                    verticalalignment="bottom",
                    horizontalalignment=config["names"]["ha"],
                    color=config["names"]["color"],
                    fontweight=config["names"]["fontweight"],
                )

        # frames = len(scatter_data)  # Total number of frames to animate
        # interval = (
        #     15 * 1000
        # ) / frames  # Interval in milliseconds to make the animation 15 seconds long

        # ani = FuncAnimation(fig, update, frames=frames, interval=interval, repeat=False)

        ani = FuncAnimation(
            fig, update, frames=len(scatter_data) + 4, interval=500, repeat=False
        )
        if self.output_format == "gif":
            ani.save(
                f"{self.export_dir}/{team_filter}_{file_name_sufix}.gif",
                writer="imagemagick",
            )
        elif self.output_format == "mp4":
            writer = FFMpegWriter(fps=1, metadata=dict(artist="Me"), bitrate=1800)
            ani.save(
                f"{self.export_dir}/{team_filter}_{file_name_sufix}.mp4", writer=writer
            )
        plt.setp(legend.get_texts(), color="white")
        plt.show()


# main block
if __name__ == "__main__":
    df = pd.read_csv("path_to_your_data.csv")  # Ensure to load your dataframe here
    plotter = PlotRelationship(use_team_config=True, fig_size=(14, 10))
    plotter.plot_animated_relationship(
        df,
        team_filter="IST",
        show_high_residuals=True,
        residual_threshold=1,
        keep_players=None,
        drop_players=["THOMPKINS, TREY", "KUZMIC, OGNJEN", "HANGA, ADAM"],
        display_only_last_names=True,
    )
