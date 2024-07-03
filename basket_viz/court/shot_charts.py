from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import pandas as pd
import matplotlib.animation as animation
from IPython.display import HTML
import os
from basket_viz.court.euroleague_team_configs import team_configs
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path


class ShotChart:
    def __init__(self, config=None, use_team_config=None):
        default_config = {
            "color_map": {"made": "#66B2FF", "miss": "#FF6F61"},
            "marker_size": 10,
            "marker_style": {"made": "o", "miss": "x"},
            "figsize": (10, 7),
            "court_line_color": "black",
            "line_width": 1,
            "outer_lines": True,
            "court_background_color": "white",
            "plot_shots": "all",  # options: 'all', 'made', 'miss'
            "coord_x": "COORD_X",
            "coord_y": "COORD_Y",
            "sort_col": "UTC",
            "animation_interval": 100,
            "animation_repeat_delay": 1000,
            "animation_blit": True,
            "hexagon_extent": (-800, 800, -200, 1300),
        }

        if use_team_config and use_team_config in team_configs:
            team_config = team_configs[use_team_config]
            self.config = {**default_config, **team_config, **(config or {})}
        else:
            self.config = {**default_config, **(config or {})}

        self.fig = None
        self.ani = None

    def set_config_param(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
            else:
                raise KeyError(
                    f"Config parameter '{key}' is not a valid config option."
                )

    def get_config(self):
        return self.config

    def draw_court(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=self.config["figsize"])
            fig.patch.set_facecolor(self.config["court_background_color"])
            ax.set_facecolor(self.config["court_background_color"])

        court_elements = self._create_court_elements()
        for element in court_elements:
            ax.add_patch(element)

        ax.set_xlim(-800, 800)
        ax.set_ylim(-200, 1500)
        ax.set_aspect(1)
        ax.axis("off")

        return ax

    def plot_field_goal_scatter(self, made, miss, title=None):
        fig, ax = plt.subplots(figsize=self.config["figsize"])
        fig.patch.set_facecolor(self.config["court_background_color"])

        self.draw_court(ax)

        coord_x = self.config["coord_x"]
        coord_y = self.config["coord_y"]

        if self.config["plot_shots"] in ["all", "made"]:
            ax.plot(
                made[coord_x],
                made[coord_y],
                "o",
                label="Made",
                color=self.config["color_map"]["made"],
                markersize=self.config["marker_size"],
            )

        if self.config["plot_shots"] in ["all", "miss"]:
            ax.plot(
                miss[coord_x],
                miss[coord_y],
                "x",
                label="Missed",
                color=self.config["color_map"]["miss"],
                markersize=self.config["marker_size"],
            )

        ax.legend(loc="upper right", bbox_to_anchor=(0.95, 0.95), prop={"size": 14})
        ax.set_xlim([-800, 800])
        ax.set_ylim([-200, 1300])
        if title:
            ax.set_title(title)

        self.fig = fig
        self.ani = None
        plt.show()

    def _create_court_elements(self):
        color = self.config["court_line_color"]
        lw = self.config["line_width"]

        hoop = self._create_hoop(color, lw)
        backboard = self._create_backboard(color, lw)
        outer_box, inner_box = self._create_paint(color, lw)
        top_free_throw, bottom_free_throw = self._create_free_throw_arcs(color, lw)
        restricted = self._create_restricted_zone(color, lw)
        corner_three_a, corner_three_b, three_arc = self._create_three_point_line(
            color, lw
        )
        center_outer_arc = self._create_center_court(color, lw)
        outer_lines = (
            self._create_outer_lines(color, lw) if self.config["outer_lines"] else None
        )

        court_elements = [
            hoop,
            backboard,
            outer_box,
            inner_box,
            restricted,
            top_free_throw,
            bottom_free_throw,
            corner_three_a,
            corner_three_b,
            three_arc,
            center_outer_arc,
        ]
        if outer_lines:
            court_elements.append(outer_lines)

        return court_elements

    def _create_hoop(self, color, lw):
        return Circle((0, 0), radius=45.72 / 2, linewidth=lw, color=color, fill=False)

    def _create_backboard(self, color, lw):
        return Rectangle((-90, -157.5 + 120), 180, -1, linewidth=lw, color=color)

    def _create_paint(self, color, lw):
        outer_box = Rectangle(
            (-490 / 2, -157.5), 490, 580, linewidth=lw, color=color, fill=False
        )
        inner_box = Rectangle(
            (-360 / 2, -157.5), 360, 580, linewidth=lw, color=color, fill=False
        )
        return outer_box, inner_box

    def _create_free_throw_arcs(self, color, lw):
        top_free_throw = Arc(
            (0, 580 - 157.5),
            360,
            360,
            theta1=0,
            theta2=180,
            linewidth=lw,
            color=color,
            fill=False,
        )
        bottom_free_throw = Arc(
            (0, 580 - 157.5),
            360,
            360,
            theta1=180,
            theta2=0,
            linewidth=lw,
            color=color,
            linestyle="dashed",
        )
        return top_free_throw, bottom_free_throw

    def _create_restricted_zone(self, color, lw):
        return Arc(
            (0, 0), 2 * 125, 2 * 125, theta1=0, theta2=180, linewidth=lw, color=color
        )

    def _create_three_point_line(self, color, lw):
        corner_three_a = Rectangle(
            (-750 + 90, -157.5), 0, 305, linewidth=lw, color=color
        )
        corner_three_b = Rectangle(
            (750 - 90, -157.5), 0, 305, linewidth=lw, color=color
        )
        three_arc = Arc(
            (0, 0), 2 * 675, 2 * 675, theta1=12, theta2=167.5, linewidth=lw, color=color
        )
        return corner_three_a, corner_three_b, three_arc

    def _create_center_court(self, color, lw):
        return Arc(
            (0, 1400 - 157.5),
            2 * 180,
            2 * 180,
            theta1=180,
            theta2=0,
            linewidth=lw,
            color=color,
        )

    def _create_outer_lines(self, color, lw):
        return Rectangle(
            (-750, -157.5), 1500, 1400, linewidth=lw, color=color, fill=False
        )

    # TODO
    # refactor field_goal_scatter_temporal to use the config [x]
    # add euroleague wraper to plot player or team shots [x]
    # add output settings [x]
    # add getter for config [x]
    # add team configs [x]
    # refactor temporal to work both with mp4 and gif [x]
    # refactor the config - separate court, marker, title elements
    # add docstrings
    # add type hints
    # add display animation in jupyter notebook [x]

    def plot_field_goal_scatter_temporal(self, made, miss, title=None):
        made["Result"] = "Made"
        miss["Result"] = "Missed"
        shots = pd.concat([made, miss])
        shots.sort_values(by=self.config["sort_col"], inplace=True)

        fig, ax = plt.subplots(figsize=self.config["figsize"])
        fig.patch.set_facecolor(self.config["court_background_color"])
        self.draw_court(ax)
        plt.xlim([-800, 800])
        plt.ylim([-200, 1300])
        if title:
            plt.title(title)

        made_shots_x, made_shots_y = [], []
        missed_shots_x, missed_shots_y = [], []
        ims = []

        coord_x = self.config["coord_x"]
        coord_y = self.config["coord_y"]
        marker_style_made = self.config["marker_style"]["made"]
        marker_style_miss = self.config["marker_style"]["miss"]

        for _, shot in shots.iterrows():
            if shot["Result"] == "Made":
                made_shots_x.append(shot[coord_x])
                made_shots_y.append(shot[coord_y])
            else:
                missed_shots_x.append(shot[coord_x])
                missed_shots_y.append(shot[coord_y])

            im = ax.plot(
                made_shots_x,
                made_shots_y,
                marker_style_made,
                color=self.config["color_map"]["made"],
                markersize=self.config["marker_size"],
                label="Made",
            )
            im += ax.plot(
                missed_shots_x,
                missed_shots_y,
                marker_style_miss,
                color=self.config["color_map"]["miss"],
                markerfacecolor="none",
                markersize=self.config["marker_size"],
                label="Missed",
            )
            ims.append(im)

            self.ani = animation.ArtistAnimation(
                fig,
                ims,
                interval=self.config["animation_interval"],
                blit=self.config["animation_blit"],
                repeat_delay=self.config["animation_repeat_delay"],
            )
            self.fig = fig  # Store the figure in the object

    def show_animation(self):
        if self.ani is not None:
            return HTML(self.ani.to_jshtml())
        else:
            raise ValueError("No animation available to show.")

    def save_plot(self, directory="output", file_name="shot_chart", file_format=None):
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

    def get_fg_made_miss(self, df, player_name=None, team_name=None, game_id=None):
        if player_name:
            df = df[df["PLAYER"] == player_name]
        if team_name:
            df = df[df["TEAM"] == team_name]
        if game_id:
            df = df[df["GAME_ID"] == game_id]

        fg_made = df[df["ID_ACTION"].isin(["2FGM", "3FGM"])]
        fg_miss = df[df["ID_ACTION"].isin(["2FGA", "3FGA"])]
        return fg_made, fg_miss

    def euroleague_player_shot_chart(
        self,
        df,
        player_name=None,
        team_name=None,
        game_id=None,
        temporal=False,
        title=None,
    ):
        fg_made, fg_miss = self.get_fg_made_miss(df, player_name, team_name, game_id)

        if temporal:
            self.plot_field_goal_scatter_temporal(fg_made, fg_miss, title=title)
        else:
            self.plot_field_goal_scatter(fg_made, fg_miss, title=title)

    # def plot_field_goal_heatmap(
    #     self, shots_df, title=None, cmap=plt.cm.gist_heat_r, gridsize=15
    # ):
    #     joint_shot_chart = sns.jointplot(
    #         x=shots_df[self.config["coord_x"]],
    #         y=shots_df[self.config["coord_y"]],
    #         kind="hex",
    #         space=0,
    #         color=cmap(0.2),
    #         cmap=cmap,
    #         joint_kws={"gridsize": gridsize},
    #     )
    #     ax = joint_shot_chart.ax_joint
    #     self.draw_court(ax)
    #     ax.set_xlim([-800, 800])
    #     ax.set_ylim([-200, 1300])
    #     if title:
    #         ax.set_title(title)
    #     plt.show()

    def get_hexbin(self, data):

        return plt.hexbin(
            data[self.coord_x],
            data[self.coord_y],
            gridsize=self.gridsize,
            extent=self.config["hexagon_extent"],
            mincnt=1,
        )

    def get_hexbins_ratio(self, hexbin_numerator, hexbin_denominator):
        return hexbin_numerator.get_array() / hexbin_denominator.get_array()

    def plot_field_goal_heatmap(
        self,
        shots_df,
        title=None,
        cmap=plt.cm.gist_heat_r,
        gridsize=15,
        custom_cmap=None,
    ):
        # Create a JointGrid
        joint_shot_chart = sns.JointGrid(
            x=shots_df[self.config["coord_x"]],
            y=shots_df[self.config["coord_y"]],
            data=shots_df,
        )

        joint_shot_chart.figure.set_size_inches(self.config["figsize"])

        if custom_cmap is None:
            # Define a default custom colormap
            # Define a custom colormap
            colors = [
                (1, 1, 1),
                (0.8, 1, 0.8),
                (0.6, 1, 0.6),
                (0.4, 1, 0.4),
                (0.2, 1, 0.2),
                (0, 1, 0),
            ]  # White -> Light green -> Darker green
            custom_cmap = LinearSegmentedColormap.from_list(
                "custom_cmap", colors, N=256
            )

        # Plot the hexbin plot on the JointGrid
        joint_shot_chart = joint_shot_chart.plot_joint(
            plt.hexbin,
            gridsize=gridsize,
            cmap=custom_cmap,
            extent=self.config["hexagon_extent"],
        )

        # Set limits and add court
        ax = joint_shot_chart.ax_joint
        self.draw_court(ax)
        ax.set_xlim([-800, 800])
        ax.set_ylim([-200, 1300])

        joint_shot_chart.ax_marg_x.remove()
        joint_shot_chart.ax_marg_y.remove()

        if title:
            ax.set_title(title)

        plt.show()

    def plot_field_goal_heatmap_sized(
        self,
        shots_df,
        title=None,
        gridsize=15,
        custom_cmap=None,
    ):
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=self.config["figsize"])

        if custom_cmap is None:
            # Define a default custom colormap
            colors = [
                (1, 1, 1),
                (0.8, 1, 0.8),
                (0.6, 1, 0.6),
                (0.4, 1, 0.4),
                (0.2, 1, 0.2),
                (0, 1, 0),
            ]  # White -> Light green -> Darker green
            custom_cmap = LinearSegmentedColormap.from_list(
                "custom_cmap", colors, N=256
            )

        # Create the hexbin plot
        hexbin = ax.hexbin(
            shots_df[self.config["coord_x"]],
            shots_df[self.config["coord_y"]],
            gridsize=gridsize,
            cmap=custom_cmap,
            extent=self.config["hexagon_extent"],
        )
        # plt.close()  # Close the hexbin plot to avoid showing it

        # Function to create sized hexbin
        def sized_hexbin(ax, hc):
            offsets = hc.get_offsets()
            orgpath = hc.get_paths()[0]
            verts = orgpath.vertices
            values = hc.get_array()
            ma = values.max()
            patches = []
            for offset, val in zip(offsets, values):
                v1 = verts * val / ma + offset
                path = Path(v1, orgpath.codes)
                patch = PathPatch(path)
                patches.append(patch)

            pc = PatchCollection(patches, cmap=hc.get_cmap(), edgecolor="k")
            pc.set_array(values)
            ax.add_collection(pc)
            hc.remove()

        # Apply the sized hexbin function
        sized_hexbin(ax, hexbin)
        plt.colorbar(hexbin, ax=ax, label="Shot Frequency")

        # Set limits and add court
        self.draw_court(ax)
        ax.set_xlim([-800, 800])
        ax.set_ylim([-200, 1300])

        if title:
            ax.set_title(title)

        plt.show()


# Example usage
if __name__ == "__main__":
    # Assuming `made_shots` and `missed_shots` are pandas DataFrames with shot data
    made_shots = pd.DataFrame(
        {"COORD_X": [100, 200, 300], "COORD_Y": [200, 300, 400], "UTC": [1, 2, 3]}
    )
    missed_shots = pd.DataFrame(
        {"COORD_X": [150, 250, 350], "COORD_Y": [250, 350, 450], "UTC": [1, 2, 3]}
    )

    shot_chart = ShotChart()
    shot_chart.plot_field_goal_scatter(
        made_shots, missed_shots, title="Field Goals Scatter Plot"
    )
    shot_chart.plot_field_goal_scatter_temporal(
        made_shots, missed_shots, title="Field Goals Scatter Plot Temporal"
    )
