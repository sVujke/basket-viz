from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import pandas as pd
import matplotlib.animation as animation
from IPython.display import HTML
import os
from basket_viz.court.euroleague_team_configs import team_configs
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
import numpy as np
from matplotlib.collections import RegularPolyCollection
from matplotlib.colors import LogNorm
from matplotlib.colors import SymLogNorm


from sklearn.preprocessing import MinMaxScaler
import numpy as np


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
            "made_action_ids": ["2FGM", "3FGM", "FTM"],
            "missed_action_ids": ["2FGA", "3FGA", "FTA"],
            "sort_col": "UTC",
            "animation_interval": 100,
            "animation_repeat_delay": 1000,
            "animation_blit": True,
            "hexagon_extent": (-800, 800, -200, 1300),
            "title": {
                "fontsize": 15,
                "fontweight": "bold",
                "color": "black",
            },
            "gridsize": 15,
            "cmap": "RdYlGn",
            "edge_color": "white",
            "edge_thickness": 2,
            "player_column_name": "PLAYER",
            "team_column_name": "TEAM",
            "entity_type": "player",
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
            ax.set_title(
                title,
                fontsize=self.config["title"]["fontsize"],
                fontweight=self.config["title"]["fontweight"],
                color=self.config["title"]["color"],
            )

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
        shots.sort_values(by=self.config["sort_col"], ascending=True, inplace=True)

        fig, ax = plt.subplots(figsize=self.config["figsize"])
        fig.patch.set_facecolor(self.config["court_background_color"])
        self.draw_court(ax)
        plt.xlim([-800, 800])
        plt.ylim([-200, 1300])

        if title:
            ax.set_title(
                title,
                fontsize=self.config["title"]["fontsize"],
                fontweight=self.config["title"]["fontweight"],
                color=self.config["title"]["color"],
            )
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

        made_action_ids = self.config["made_action_ids"]
        missed_action_ids = self.config["missed_action_ids"]

        if player_name:
            df = df[df[self.config["player_column_name"]] == player_name]
        if team_name:
            df = df[df[self.config["team_column_name"]] == team_name]
        if game_id:
            df = df[df["GAME_ID"] == game_id]

        fg_made = df[df["ID_ACTION"].isin(made_action_ids)]
        fg_miss = df[df["ID_ACTION"].isin(missed_action_ids)]
        return fg_made, fg_miss

    def euroleague_field_goal_dots(
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

    def get_hexbin_from_data_points(self, data):

        hc = plt.hexbin(
            data[self.config["coord_x"]],
            data[self.config["coord_y"]],
            gridsize=self.config["gridsize"],
            extent=self.config["hexagon_extent"],
            mincnt=0,
        )
        plt.close()
        return hc

    def get_hexbin_from_offset_values(self, ax, offsets, values):

        hc = ax.hexbin(
            offsets[:, 0],
            offsets[:, 1],
            gridsize=self.config["gridsize"],
            C=np.array(values),
            extent=self.config["hexagon_extent"],
        )
        plt.close()
        return ax, hc

    def create_custom_cmap(self):
        colors = [
            (1, 1, 1),
            (0.8, 1, 0.8),
            (0.6, 1, 0.6),
            (0.4, 1, 0.4),
            (0.2, 1, 0.2),
            (0, 1, 0),
        ]
        return LinearSegmentedColormap.from_list("custom_cmap", colors, N=256)

    def plot_field_goal_heatmap(
        self,
        shots_df,
        title=None,
        cmap=plt.cm.gist_heat_r,
        gridsize=15,
        custom_cmap=None,
        sized=False,
    ):
        if custom_cmap is not None:
            cmap = custom_cmap

        self.fig, ax = plt.subplots(figsize=self.config["figsize"])

        hexbin = ax.hexbin(
            shots_df[self.config["coord_x"]],
            shots_df[self.config["coord_y"]],
            gridsize=gridsize,
            cmap=cmap,
            extent=self.config["hexagon_extent"],
        )

        if sized:
            self.sized_hexbin(ax, hexbin)
        else:
            plt.colorbar(hexbin, ax=ax, label="Shot Frequency")

        self.draw_court(ax)
        ax.set_xlim([-800, 800])
        ax.set_ylim([-200, 1300])

        if title:
            ax.set_title(
                title,
                fontsize=self.config["title"]["fontsize"],
                fontweight=self.config["title"]["fontweight"],
                color=self.config["title"]["color"],
            )

        plt.show()

    def sized_hexbin(
        self,
        hc,
        ax,
        offsets,
        size_values,
        efficiency_values,
        min_size=0.2,
        max_size=1.5,
        scaling_factor=0.8,
    ):
        """
        Adjust the size of hexagons based on the provided size_values (e.g., frequency),
        and color them based on efficiency_values, ensuring the hexagons scale correctly
        without moving their position on the plot. Uses logarithmic scaling for size.

        Args:
        - hc: The original hexbin collection.
        - ax: Matplotlib axis object.
        - offsets: Array of hexagon centers (x, y coordinates) on the plot.
        - size_values: Array of values used to scale the hexagons (e.g., shot frequencies).
        - efficiency_values: Array of values used to color the hexagons (e.g., shooting efficiency).
        - min_size: Minimum size of hexagons.
        - max_size: Maximum size of hexagons (dynamic upper bound).
        - scaling_factor: A factor to control the overall scaling of hexagons.
        """

        # Remove zero size values from size_values and their corresponding offsets and efficiency values
        valid_indices = size_values > 0
        size_values_filtered = size_values[valid_indices]
        offsets_filtered = offsets[valid_indices]
        efficiency_values_filtered = efficiency_values[valid_indices]

        orgpath = hc.get_paths()[0]  # Get the original hexagon path
        verts = orgpath.vertices  # Vertices of the hexagons

        # Logarithmic scaling for size values
        size_values_filtered = np.log1p(
            size_values_filtered
        )  # Log scaling to make small sizes smaller

        # Get dynamic upper bound for normalization (based on the max size_value)
        size_min = np.min(size_values_filtered)
        size_max = np.max(size_values_filtered)

        # Dynamic upper bound using max_size parameter
        dynamic_max_size = max_size * scaling_factor

        # Normalize log-transformed size values to the range [min_size, dynamic_max_size]
        normalized_sizes = (size_values_filtered - size_min) / (size_max - size_min) * (
            dynamic_max_size - min_size
        ) + min_size

        patches = []
        hex_center = np.mean(verts, axis=0)  # Calculate the center of the hexagon

        # Create hexagons with sizes scaled based on the normalized sizes
        for offset, size in zip(offsets_filtered, normalized_sizes):
            # Scale the hexagon vertices relative to its center and then apply offset
            v1 = (verts - hex_center) * size + offset
            path = Path(v1, orgpath.codes)
            patch = PathPatch(path)
            patches.append(patch)

        # Use efficiency_values to set color for the hexagons
        color_values = np.array(efficiency_values_filtered)

        # Create PatchCollection and add to the axis
        pc = PatchCollection(patches, cmap=self.config["cmap"], edgecolor="k")
        pc.set_array(color_values)  # Set color based on efficiency values
        ax.add_collection(pc)

        # Remove the original hexbin collection (optional)
        if hc in ax.collections:
            hc.remove()  # Remove safely if it exists in the list of artists

        # Avoid adding multiple colorbars
        if not hasattr(ax, "_colorbar"):
            cbar = plt.colorbar(pc, ax=ax, label="Shooting Efficiency")
            ax._colorbar = cbar

    # Remove the original hexbin collection (but preserve the color array)

    def euroleague_field_goal_heatmap(
        self,
        df,
        player_name=None,
        team_name=None,
        game_id=None,
        title=None,
        gridsize=15,
        custom_cmap=None,
        sized=False,
    ):
        fg_made, fg_miss = self.get_fg_made_miss(df, player_name, team_name, game_id)

        if self.config["plot_shots"] == "all":
            shots_df = pd.concat([fg_made, fg_miss])
        elif self.config["plot_shots"] == "made":
            shots_df = fg_made
        elif self.config["plot_shots"] == "miss":
            shots_df = fg_miss

        self.plot_field_goal_heatmap(
            shots_df,
            title=title,
            gridsize=gridsize,
            custom_cmap=custom_cmap,
            sized=sized,
        )

    def plot_hexbin(self, offsets, values, mincnt=0, title=None):
        """
        Plot the efficiency using ax.hexbin with data from hexbin_data_with_coords.
        """
        # # Create the plot
        fig, ax = plt.subplots(figsize=self.config["figsize"])

        # # Set hexagons with 0 values to NaN so they won't be plotted
        values_filtered = np.array(values)
        values_filtered[values_filtered == 0] = np.nan
        vmax_value = np.nanmax(values_filtered)  # Max of non-zero values

        hc = ax.hexbin(
            offsets[:, 0],
            offsets[:, 1],
            gridsize=self.config["gridsize"],
            edgecolors=self.config["edge_color"],
            linewidths=self.config["edge_thickness"],
            C=values_filtered,
            extent=self.config["hexagon_extent"],
            cmap=self.config["cmap"],
            mincnt=mincnt,
            norm=SymLogNorm(linthresh=1e-2, linscale=1, vmin=0.1, vmax=vmax_value),
        )

        plt.colorbar(hc, ax=ax, label="Shooting Efficiency")

        # Draw the court and set limits
        self.draw_court(ax)
        ax.set_xlim([-800, 800])
        ax.set_ylim([-200, 1300])

        ax.set_aspect("equal")

        if title:
            ax.set_title(
                title,
                fontsize=self.config["title"]["fontsize"],
                fontweight=self.config["title"]["fontweight"],
                color=self.config["title"]["color"],
            )

        plt.show()

    def plot_entity_hexbin(
        self, df, offsets_col, color_col, entity_name, mincnt=0, title=None
    ):

        entity_type = self.config["entity_type"]
        # Extract data for the chosen entity (player or team)
        if entity_type == "player":
            entity_data = df[df["player_name"] == entity_name]
        elif entity_type == "team":
            entity_data = df[df["team_name"] == entity_name]

        # Access the arrays from the DataFrame
        offsets = entity_data[offsets_col].values[
            0
        ]  # Assuming offsets are stored as a list of (x, y) tuples
        color_values = np.array(entity_data[color_col].values[0])  # 0 to 1 values

        self.plot_hexbin(offsets=offsets, values=color_values, mincnt=mincnt)

    def plot_entity_hexbin_sized(
        self,
        df,
        offsets_col,
        color_col,
        size_col,
        entity_name,
        mincnt=0,
        title=None,
        min_size=0.2,
        max_size=1.0,
        scaling_factor=0.7,
    ):
        """
        Plot a hexbin where color represents shooting efficiency (0-1) and size represents shot frequency.

        Args:
        - df: DataFrame containing the relevant data.
        - offsets_col: The name of the column containing the offsets (x, y).
        - efficiency_col: The name of the column containing shooting efficiency values (0 to 1).
        - frequency_col: The name of the column containing frequency values for hexagon size.
        - player_name: The player's name to filter the data.
        - mincnt: Minimum count for hexagons.
        - title: Title for the plot.
        """
        fig, ax = plt.subplots(figsize=self.config["figsize"])

        entity_type = self.config["entity_type"]
        # Extract data for the chosen entity (player or team)
        if entity_type == "player":
            entity_data = df[df["player_name"] == entity_name]
        elif entity_type == "team":
            entity_data = df[df["team_name"] == entity_name]

        # Access the arrays from the DataFrame
        offsets = entity_data[offsets_col].values[
            0
        ]  # Assuming offsets are stored as a list of (x, y) tuples
        color_values = np.array(entity_data[color_col].values[0])  # 0 to 1 values
        size_values = np.array(
            entity_data[size_col].values[0]
        )  # Frequency values for hexagon size

        # Filter zero efficiency values (set to NaN)
        color_values_filtered = np.copy(color_values)
        color_values_filtered[color_values_filtered == 0] = np.nan
        vmax_value = np.nanmax(
            color_values_filtered
        )  # Max of non-zero efficiency values

        # Plot hexagons with filtered efficiency as color
        hc = ax.hexbin(
            offsets[:, 0],
            offsets[:, 1],
            gridsize=self.config["gridsize"],
            edgecolors="none",  # Prevent the edges from drawing
            linewidths=0,
            C=color_values_filtered,  # Use filtered efficiency for color
            extent=self.config["hexagon_extent"],
            cmap=self.config["cmap"],  # Your colormap
            mincnt=mincnt,
            norm=SymLogNorm(linthresh=1e-2, linscale=1, vmin=0.1, vmax=vmax_value),
        )

        # Remove the original hexbin collection
        hc.remove()

        # Call the sized_hexbin function to adjust hexagon sizes based on filtered frequency
        size_values_filtered = np.copy(size_values)
        size_values_filtered[size_values_filtered == 0] = -1

        self.sized_hexbin(
            hc,
            ax,
            offsets=offsets,
            size_values=size_values_filtered,
            efficiency_values=color_values_filtered,
            max_size=max_size,
            min_size=min_size,
            scaling_factor=scaling_factor,
        )

        # Draw the court and set limits
        self.draw_court(ax)
        ax.set_xlim([-800, 800])
        ax.set_ylim([-200, 1300])

        ax.set_aspect("equal")

        if title:
            ax.set_title(
                title,
                fontsize=self.config["title"]["fontsize"],
                fontweight=self.config["title"]["fontweight"],
                color=self.config["title"]["color"],
            )

        plt.show()

    def get_entity_hexbin_data(self, df, entity_name):
        """
        Filters the dataframe for a specific player and returns a dataframe
        with columns: player_name, offsets, values_made, values_missed, values_all.
        """
        # Filter the dataframe by player name
        entity_type = self.config["entity_type"]

        if entity_type == "player":
            df_entity = df[df[self.config["player_column_name"]] == entity_name]
        elif entity_type == "team":
            df_entity = df[df[self.config["team_column_name"]] == entity_name]

        # Separate made and missed shots
        fg_made, fg_miss = self.get_fg_made_miss(df_entity)

        # Get the hexbin offsets and values for made shots
        made_hc = self.get_hexbin_from_data_points(fg_made)
        values_made = made_hc.get_array()

        # Get the hexbin offsets and values for missed shots
        miss_hc = self.get_hexbin_from_data_points(fg_miss)
        values_missed = miss_hc.get_array()

        # Get the hexbin offsets and values for all shots
        all_hc = self.get_hexbin_from_data_points(df_entity)
        values_all = all_hc.get_array()
        offsets_all = all_hc.get_offsets()

        # this is for the case when there was only a few shots in a hexbin and they were misses
        adjustment = np.where(values_all != 0, 1, 0) * 0.001
        adjusted_values_made = values_made + adjustment

        ratio_values = adjusted_values_made / values_all

        # Create a dataframe to return
        shot_data = {
            f"{entity_type}_name": [entity_name],
            "offsets": [offsets_all],
            "values_made": [values_made],
            "values_missed": [values_missed],
            "values_all": [values_all],
            "values_ratio": [ratio_values],
        }

        result_df = pd.DataFrame(shot_data)

        plt.close()  # Close the plots to avoid displaying them during function call

        return result_df

    def get_all_entity_hexbin_data(self, df):
        """
        Processes the shot data for all players and returns a dataframe containing:
        player_name or team name, offsets, values_made, values_missed, values_all.
        """
        entity_type = self.config["entity_type"]

        if entity_type == "player":
            unique_entities = df[self.config["player_column_name"]].unique()
        elif entity_type == "team":
            unique_entities = df[self.config["team_column_name"]].unique()

        entities_data = []

        # Loop over each player/team and get shot data
        for entity_name in unique_entities:
            entity_data = self.get_entity_hexbin_data(df, entity_name)
            entities_data.append(entity_data)

        # Concatenate all the entities into a single dataframe
        all_players_df = pd.concat(entities_data, ignore_index=True)

        return all_players_df

    def _normalize_totals(self, all_entities_df, metric="made"):
        """
        Calculates the totals for all players' values and normalizes the performance
        of each player against the rest of the league.

        Returns a dataframe with the normalized values for each player.
        """
        metrics = {
            "made": "values_made",
            "missed": "values_missed",
            "all": "values_all",
        }
        # Initialize arrays to store totals
        total_values = np.zeros_like(all_entities_df[metrics[metric]].values[0])

        # Calculate the total values across all players
        for _, row in all_entities_df.iterrows():
            total_values += row[metrics[metric]]
            # total_values_all += row["values_all"]

        # Create a new dataframe to store the normalized values
        normalized_data = []

        entity_type = self.config["entity_type"]

        for _, row in all_entities_df.iterrows():
            entity_name = row[f"{entity_type}_name"]
            offsets = row["offsets"]
            values = row[metrics[metric]]

            # Normalize the player's values by the league totals
            normalized_values = np.divide(
                values,
                total_values,
                out=np.zeros_like(values),
                where=total_values != 0,
            )

            normalized_data.append(
                {
                    f"{entity_type}_name": entity_name,
                    "offsets": offsets,
                    f"normalized_values_{metric}": normalized_values,
                }
            )

        # Return a dataframe containing the normalized values for all players
        normalized_df = pd.DataFrame(normalized_data)

        return normalized_df

    def _minmax_scale_normalized_values(self, normalized_df, metric="made"):
        """
        Applies Min-Max scaling to normalized values for each hexbin to see who performs the best per bin.
        Returns a dataframe with scaled values for each player.
        """
        # Initialize MinMaxScaler
        scaler = MinMaxScaler()

        # Iterate over each row in the dataframe
        for idx, row in normalized_df.iterrows():
            # Extract the values for the given metric (either "made" or others)
            values = row[f"normalized_values_{metric}"]

            # Apply masking if needed (assuming masked arrays are already present)
            masked_values = np.ma.masked_array(values).compressed()

            # Reshape the array for scaling
            masked_values_reshaped = masked_values.reshape(-1, 1)

            # Apply Min-Max scaling
            scaled_values = scaler.fit_transform(masked_values_reshaped).flatten()

            # Set fill value for masked array
            np.ma.set_fill_value(values, 0)

            # Put scaled values back in place (ignoring masked elements)
            values[~values.mask] = scaled_values

            # Update the DataFrame with the scaled values
            normalized_df.at[idx, f"normalized_values_{metric}"] = values

        return normalized_df


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
