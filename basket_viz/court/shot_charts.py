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
            df = df[df["PLAYER"] == player_name]
        if team_name:
            df = df[df["TEAM"] == team_name]
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
            # edgecolors=edge_color,  # Set the border color
            # linewidths=edge_thickness,
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

    # def sized_hexbin(self, ax, hc):
    #         offsets = hc.get_offsets()
    #         orgpath = hc.get_paths()[0]
    #         verts = orgpath.vertices
    #         values = hc.get_array()
    #         ma = values.max()
    #         patches = []

    #         for offset, val in zip(offsets, values):
    #             v1 = verts * val / ma + offset
    #             path = Path(v1, orgpath.codes)
    #             patch = PathPatch(path)
    #             patches.append(patch)

    #         pc = PatchCollection(patches, cmap=hc.get_cmap(), edgecolor="k")
    #         pc.set_array(values)
    #         ax.add_collection(pc)
    #         hc.remove()

    # def sized_hexbin(self, ax, hc, size_values=None, scaling_factor=0.8, min_size=0.1):
    #     """
    #     Adjust the size of hexagons based on the provided size_values (e.g., frequency).
    #     If size_values is None, it will use the values in the hexbin collection (efficiency).

    #     Args:
    #     - ax: Matplotlib axis object.
    #     - hc: Hexbin collection.
    #     - size_values: Array of values used to scale the hexagons. If None, use hc.get_array().
    #     - scaling_factor: A factor to control the overall scaling of hexagons.
    #     - min_size: The minimum size of a hexagon (for very low frequency values).
    #     """
    #     offsets = hc.get_offsets()  # Hexagon centers
    #     orgpath = hc.get_paths()[0]  # The original hexagon path
    #     verts = orgpath.vertices  # Vertices of the hexagons

    #     # Use efficiency values if no custom size_values array is provided
    #     if size_values is None:
    #         size_values = hc.get_array()

    #     # Logarithmic scaling for size values
    #     size_values = np.array(size_values)
    #     log_size_values = np.log1p(
    #         size_values
    #     )  # Log scaling to make small sizes smaller

    #     # Get dynamic upper bound for normalization (based on the max size_value)
    #     size_min = log_size_values.min()
    #     size_max = log_size_values.max()

    #     # Instead of a fixed max (1.5), use a dynamic max based on the distribution of size values
    #     dynamic_max_size = (
    #         2 * scaling_factor
    #     )  # Dynamic upper bound (you can adjust the factor)

    #     # Normalize log-transformed size values to the range [min_size, dynamic_max_size]
    #     normalized_sizes = (log_size_values - size_min) / (size_max - size_min) * (
    #         dynamic_max_size - min_size
    #     ) + min_size

    #     patches = []

    #     # Create hexagons with sizes scaled based on the normalized size values
    #     for offset, size in zip(offsets, normalized_sizes):
    #         v1 = verts * size + offset  # Scale vertices based on size_values
    #         print("Offset:", offset)
    #         print("Size:", size)
    #         print("Scaled vertices (v1):", v1)
    #         path = Path(v1, orgpath.codes)
    #         patch = PathPatch(path)
    #         patches.append(patch)

    #     # Use the original color array (efficiency) from the hexbin collection to set color
    #     color_values = hc.get_array()  # This keeps the color tied to efficiency values

    #     # Create PatchCollection and add to the axis
    #     pc = PatchCollection(patches, cmap=hc.get_cmap(), edgecolor="k")
    #     pc.set_array(color_values)  # Set color based on original efficiency values
    #     ax.add_collection(pc)

    #     # Remove the original hexbin collection (but preserve the color array)
    #     hc.remove()

    # def sized_hexbin(
    #     self, hc, ax, offsets, size_values, efficiency_values, max_size=1.5
    # ):
    #     """
    #     Adjust the size of hexagons based on the provided size_values (e.g., frequency),
    #     and color them based on efficiency_values, ensuring the hexagons scale correctly
    #     without moving their position on the plot.

    #     Args:
    #     - ax: Matplotlib axis object.
    #     - offsets: Array of hexagon centers (x, y coordinates) on the plot.
    #     - size_values: Array of values used to scale the hexagons (e.g., shot frequencies).
    #     - efficiency_values: Array of values used to color the hexagons (e.g., shooting efficiency).
    #     - max_size: The maximum hexagon size.
    #     """
    #     print("orgpaths")
    #     orgpath = hc.get_paths()[0]  # Get the original hexagon path
    #     print("verts")

    #     verts = orgpath.vertices  # Vertices of the hexagons

    #     # Normalize size_values between 0 and max_size
    #     print("size_values")
    #     size_values = np.array(size_values)
    #     size_min = np.min(size_values[size_values > 0])  # Ignore zero frequencies
    #     size_max = np.max(size_values)
    #     print(size_min, size_max)
    #     size_values = size_values[size_values > 0]
    #     # Normalize sizes to the range [0, 1] and rescale to max_size
    #     normalized_sizes = (size_values - size_min) / (size_max - size_min)
    #     scaled_sizes = normalized_sizes * (
    #         max_size - 0.1
    #     )  # Scale to desired range [0.1, max_size]

    #     patches = []

    #     # Calculate the center of the hexagon to avoid moving the position
    #     print("hex_center")
    #     hex_center = np.mean(verts, axis=0)

    #     # Create hexagons with sizes scaled based on the normalized sizes
    #     for offset, real_size, size in zip(offsets, size_values, scaled_sizes):
    #         # Scale the hexagon vertices relative to its center and then apply offset
    #         print("entered loop")
    #         v1 = (verts - hex_center) * size + offset

    #         # Print statements for debugging (optional)
    #         print("Offset:", offset)
    #         print("Real size:", real_size)
    #         print("Size:", size)
    #         print("Hexagon center:", hex_center)
    #         print("Scaled vertices (v1):", v1)

    #         # Create path and patch
    #         path = Path(v1, orgpath.codes)
    #         patch = PathPatch(path)
    #         patches.append(patch)

    #     # Use efficiency_values to set color for the hexagons
    #     color_values = np.array(
    #         efficiency_values
    #     )  # Ensure efficiency values are in an array

    #     # Create PatchCollection and add to the axis
    #     pc = PatchCollection(patches, cmap="RdYlGn", edgecolor="k")
    #     pc.set_array(color_values)  # Set color based on efficiency values
    #     ax.add_collection(pc)

    #     # Add a colorbar to show efficiency
    #     plt.colorbar(pc, ax=ax, label="Efficiency")

    # def sized_hexbin(
    #     self, hc, ax, offsets, size_values, efficiency_values, max_size=1.5
    # ):
    #     """
    #     Adjust the size of hexagons based on the provided size_values (e.g., frequency),
    #     and color them based on efficiency_values, ensuring the hexagons scale correctly
    #     without moving their position on the plot.

    #     Args:
    #     - hc: The original hexbin collection.
    #     - ax: Matplotlib axis object.
    #     - offsets: Array of hexagon centers (x, y coordinates) on the plot.
    #     - size_values: Array of values used to scale the hexagons (e.g., shot frequencies).
    #     - efficiency_values: Array of values used to color the hexagons (e.g., shooting efficiency).
    #     - max_size: The maximum hexagon size.
    #     """

    #     orgpath = hc.get_paths()[0]  # Get the original hexagon path
    #     verts = orgpath.vertices  # Vertices of the hexagons

    #     # Remove zero size values from size_values and their corresponding offsets and efficiency values
    #     valid_indices = size_values > 0
    #     size_values_filtered = size_values[valid_indices]
    #     offsets_filtered = offsets[valid_indices]
    #     efficiency_values_filtered = efficiency_values[valid_indices]

    #     # Normalize size_values between 0 and max_size
    #     size_min = np.min(size_values_filtered)  # After filtering zero frequencies
    #     size_max = np.max(size_values_filtered)

    #     # Normalize sizes to the range [0, 1] and rescale to max_size
    #     normalized_sizes = (size_values_filtered - size_min) / (size_max - size_min)
    #     scaled_sizes = (
    #         normalized_sizes * (max_size - 0.1) + 0.1
    #     )  # Scale to range [0.1, max_size]

    #     patches = []

    #     # Calculate the center of the hexagon to avoid moving the position
    #     hex_center = np.mean(verts, axis=0)

    #     # Create hexagons with sizes scaled based on the normalized sizes
    #     for offset, size in zip(offsets_filtered, scaled_sizes):
    #         # Scale the hexagon vertices relative to its center and then apply offset
    #         v1 = (verts - hex_center) * size + offset

    #         # Create path and patch
    #         path = Path(v1, orgpath.codes)
    #         patch = PathPatch(path)
    #         patches.append(patch)

    #     # Use efficiency_values to set color for the hexagons
    #     color_values = np.array(
    #         efficiency_values_filtered
    #     )  # Ensure efficiency values are in an array

    #     # Create PatchCollection and add to the axis
    #     pc = PatchCollection(patches, cmap="RdYlGn", edgecolor="k")
    #     pc.set_array(color_values)  # Set color based on efficiency values
    #     ax.add_collection(pc)

    #     # Add a colorbar to show efficiency
    #     plt.colorbar(pc, ax=ax, label="Shooting Efficiency")
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
        pc = PatchCollection(patches, cmap="RdYlGn", edgecolor="k")
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

    # def _divide_hexbins(self, numerator_hexbin, denominator_hexbin):
    #     numerator_values = numerator_hexbin.get_array()
    #     denominator_values = denominator_hexbin.get_array()

    #     # ratio_values = np.divide(
    #     #     numerator_values,
    #     #     denominator_values,
    #     #     out=np.zeros_like(numerator_values),
    #     #     where=denominator_values != 0,
    #     # )

    #     print(numerator_hexbin.get_array())
    #     print(denominator_hexbin.get_array())
    #     ratio_values = numerator_hexbin.get_array() / denominator_hexbin.get_array()

    #     offsets = denominator_hexbin.get_offsets()

    #     return offsets, ratio_values

    def plot_hexbin_data(self, offsets, values, mincnt=0, title=None):
        """
        Plot the efficiency using ax.hexbin with data from hexbin_data_with_coords.
        """
        # Unpack the coordinates and efficiency values
        # coords, efficiency = zip(*hexbin_data_with_coords)
        # coords = np.array(coords)  # Convert to numpy array for easier indexing
        # efficiency = np.array(efficiency)  # Efficiency values

        # # Create the plot
        fig, ax = plt.subplots(figsize=self.config["figsize"])

        # # Plot the hexagons using ax.hexbin()
        # efficiency_hexbin = self.add_hexbin(
        #     ax, coords=coords, values=efficiency, gridsize=gridsize, cmap=cmap
        # )

        edge_color = "white"
        edge_thickness = 2

        # zero_value_indices = np.where(values == 0)[0]
        # print(
        #     f"Hexagons with zero values: {zero_value_indices}"
        # )  # You can store or log this

        # # Set hexagons with 0 values to NaN so they won't be plotted
        values_filtered = np.array(values)
        values_filtered[values_filtered == 0] = np.nan
        vmax_value = np.nanmax(values_filtered)  # Max of non-zero values

        hc = ax.hexbin(
            offsets[:, 0],
            offsets[:, 1],
            gridsize=self.config["gridsize"],
            edgecolors=edge_color,
            linewidths=edge_thickness,
            C=values_filtered,
            extent=self.config["hexagon_extent"],
            cmap=self.config["cmap"],
            mincnt=mincnt,
            norm=SymLogNorm(
                linthresh=1e-2, linscale=1, vmin=0.1, vmax=vmax_value
            ),  # Adjust thresholds
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

    def plot_hexbin_with_size_and_color(
        self,
        df,
        offsets_col,
        efficiency_col,
        frequency_col,
        player_name,
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

        # Extract data for the given player
        player_data = df[df["player_name"] == player_name]

        # Access the arrays from the DataFrame
        offsets = player_data[offsets_col].values[
            0
        ]  # Assuming offsets are stored as a list of (x, y) tuples
        efficiency_values = np.array(
            player_data[efficiency_col].values[0]
        )  # 0 to 1 values
        frequency_values = np.array(
            player_data[frequency_col].values[0]
        )  # Frequency values for hexagon size

        # Filter zero efficiency values (set to NaN)
        efficiency_values_filtered = np.copy(efficiency_values)
        efficiency_values_filtered[efficiency_values_filtered == 0] = np.nan
        vmax_value = np.nanmax(
            efficiency_values_filtered
        )  # Max of non-zero efficiency values

        # Also filter frequency values, setting zero frequencies to NaN
        frequency_values_filtered = np.copy(frequency_values)
        # frequency_values_filtered[frequency_values_filtered == 0] = np.nan

        # Plot hexagons with filtered efficiency as color
        hc = ax.hexbin(
            offsets[:, 0],
            offsets[:, 1],
            gridsize=self.config["gridsize"],
            edgecolors="none",  # Prevent the edges from drawing
            linewidths=0,
            C=efficiency_values_filtered,  # Use filtered efficiency for color
            extent=self.config["hexagon_extent"],
            cmap=self.config["cmap"],  # Your colormap
            mincnt=mincnt,
            norm=SymLogNorm(linthresh=1e-2, linscale=1, vmin=0.1, vmax=vmax_value),
        )

        # Remove the original hexbin collection
        hc.remove()

        # Call the sized_hexbin function to adjust hexagon sizes based on filtered frequency
        frequency_values_filtered = np.copy(frequency_values)
        frequency_values_filtered[frequency_values_filtered == 0] = -1

        self.sized_hexbin(
            hc,
            ax,
            offsets=offsets,
            size_values=frequency_values_filtered,
            efficiency_values=efficiency_values_filtered,
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

    # Combine all steps into a single method for convenience

    def get_player_hexbin_data(self, df, player_name):
        """
        Filters the dataframe for a specific player and returns a dataframe
        with columns: player_name, offsets, values_made, values_missed, values_all.
        """
        # Filter the dataframe by player name
        df_player = df[df["PLAYER"] == player_name]

        # Separate made and missed shots
        fg_made, fg_miss = self.get_fg_made_miss(df_player)

        # Get the hexbin offsets and values for made shots
        made_hc = self.get_hexbin_from_data_points(fg_made)
        values_made = made_hc.get_array()
        offsets_made = made_hc.get_offsets()

        # Get the hexbin offsets and values for missed shots
        miss_hc = self.get_hexbin_from_data_points(fg_miss)
        values_missed = miss_hc.get_array()
        offsets_missed = miss_hc.get_offsets()

        # Get the hexbin offsets and values for all shots
        all_hc = self.get_hexbin_from_data_points(df_player)
        values_all = all_hc.get_array()
        offsets_all = all_hc.get_offsets()

        # this is for the case when there was only a few shots in a hexbin and they were misses
        adjustment = np.where(values_all != 0, 1, 0) * 0.001
        adjusted_values_made = values_made + adjustment

        ratio_values = adjusted_values_made / values_all

        # Create a dataframe to return
        shot_data = {
            "player_name": [player_name],
            "offsets": [offsets_all],
            "values_made": [values_made],
            "values_missed": [values_missed],
            "values_all": [values_all],
            "values_ratio": [ratio_values],
        }

        result_df = pd.DataFrame(shot_data)

        plt.close()  # Close the plots to avoid displaying them during function call

        return result_df

    def get_hexbin_data_for_dataframe(self, df):
        """
        Processes the shot data for all players and returns a dataframe containing:
        player_name, offsets, values_made, values_missed, values_all.
        """
        players = df["PLAYER"].unique()
        all_players_data = []

        # Loop over each player and get shot data
        for player_name in players:
            player_data = self.get_player_hexbin_data(df, player_name)
            all_players_data.append(player_data)

        # Concatenate all the players' data into a single dataframe
        all_players_df = pd.concat(all_players_data, ignore_index=True)

        return all_players_df

    def _normalize_totals(self, all_players_df, metric="made"):
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
        total_values = np.zeros_like(all_players_df[metrics[metric]].values[0])
        # total_values_all = np.zeros_like(all_players_df["values_all"].values[0])

        # Calculate the total values across all players
        for _, row in all_players_df.iterrows():
            total_values += row[metrics[metric]]
            # total_values_all += row["values_all"]

        # Create a new dataframe to store the normalized values
        normalized_data = []

        for _, row in all_players_df.iterrows():
            player_name = row["player_name"]
            offsets = row["offsets"]
            values = row[metrics[metric]]
            # values_all = row["values_all"]

            # Normalize the player's values by the league totals
            normalized_values = np.divide(
                values,
                total_values,
                out=np.zeros_like(values),
                where=total_values != 0,
            )
            # normalized_values_all = np.divide(
            #     values_all,
            #     total_values_all,
            #     out=np.zeros_like(values_all),
            #     where=total_values_all != 0,
            # )

            normalized_data.append(
                {
                    "player_name": player_name,
                    "offsets": offsets,
                    f"normalized_values_{metric}": normalized_values,
                    # "normalized_values_all": normalized_values_all,
                }
            )

        # Return a dataframe containing the normalized values for all players
        normalized_df = pd.DataFrame(normalized_data)

        return normalized_df

    def minmax_scale_normalized_values(self, normalized_df):
        """
        Applies Min-Max scaling to normalized values for each hexbin to see who performs the best per bin.

        Returns a dataframe with scaled values for each player.
        """
        # Initialize lists to store scaled values
        scaled_data = []

        # Retrieve the offsets (bins) from the first player row
        offsets = normalized_df["offsets"].values[0]

        # Initialize MinMaxScaler
        scaler = MinMaxScaler()

        # We will loop over each bin (for each player) and apply Min-Max scaling
        for bin_idx in range(len(offsets)):
            # Collect the bin values for all players for 'values_made' and 'values_all'
            values_made_for_bin = np.array(
                [
                    row["normalized_values_made"][bin_idx]
                    for _, row in normalized_df.iterrows()
                ]
            )
            values_all_for_bin = np.array(
                [
                    row["normalized_values_all"][bin_idx]
                    for _, row in normalized_df.iterrows()
                ]
            )

            # Reshape to 2D arrays for scaling
            values_made_for_bin = values_made_for_bin.reshape(-1, 1)
            values_all_for_bin = values_all_for_bin.reshape(-1, 1)

            # Scale the values using MinMaxScaler
            scaled_values_made_for_bin = scaler.fit_transform(
                values_made_for_bin
            ).flatten()
            scaled_values_all_for_bin = scaler.fit_transform(
                values_all_for_bin
            ).flatten()

            # Store the scaled values back in a list
            scaled_data.append(
                {
                    "bin_idx": bin_idx,
                    "scaled_values_made": scaled_values_made_for_bin,
                    "scaled_values_all": scaled_values_all_for_bin,
                }
            )

        # Convert the scaled data into a dataframe
        for idx, row in normalized_df.iterrows():
            player_name = row["player_name"]
            offsets = row["offsets"]

            scaled_values_made = np.array(
                [
                    scaled_data[bin_idx]["scaled_values_made"][idx]
                    for bin_idx in range(len(offsets))
                ]
            )
            scaled_values_all = np.array(
                [
                    scaled_data[bin_idx]["scaled_values_all"][idx]
                    for bin_idx in range(len(offsets))
                ]
            )

            normalized_df.at[idx, "scaled_values_made"] = scaled_values_made
            normalized_df.at[idx, "scaled_values_all"] = scaled_values_all

        return normalized_df

    # def plot_shooting_efficiency_heatmap(
    #     self,
    #     df,
    #     player_name=None,
    #     team_name=None,
    #     game_id=None,
    #     title=None,
    #     gridsize=15,
    #     custom_cmap=None,
    # ):
    #     # Get made and missed field goals
    #     fg_made, fg_miss = self.get_fg_made_miss(df, player_name, team_name, game_id)

    #     # Concatenate made and missed shots
    #     shots_df = pd.concat([fg_made.assign(made=1), fg_miss.assign(made=0)])

    #     # Use the same hexbin to calculate both total attempts and made shots
    #     self.fig, ax = plt.subplots(figsize=self.config["figsize"])

    #     # Create hexbin to count total shots and made shots
    #     hexbin = ax.hexbin(
    #         shots_df[self.config["coord_x"]],
    #         shots_df[self.config["coord_y"]],
    #         C=shots_df["made"],
    #         reduce_C_function=np.sum,
    #         gridsize=gridsize,
    #         cmap=custom_cmap or plt.cm.viridis,
    #         extent=self.config["hexagon_extent"],
    #     )

    #     # Use the "norm" argument to normalize efficiency (shots made / total shots)
    #     attempts_hexbin = ax.hexbin(
    #         shots_df[self.config["coord_x"]],
    #         shots_df[self.config["coord_y"]],
    #         gridsize=gridsize,
    #         cmap=plt.cm.gray_r,
    #         extent=self.config["hexagon_extent"],
    #         alpha=0.0,  # Invisible plot, just to count total attempts
    #     )

    #     # Now calculate efficiency
    #     attempts = attempts_hexbin.get_array()
    #     made = hexbin.get_array()

    # Avoid division by zero by replacing zeros with a very small number
    # efficiency = np.divide(
    #     made, attempts, out=np.zeros_like(made), where=attempts != 0
    # )

    # # Re-plot with efficiency
    # efficiency_hexbin = ax.hexbin(
    #     shots_df[self.config["coord_x"]],
    #     shots_df[self.config["coord_y"]],
    #     C=efficiency,
    #     gridsize=gridsize,
    #     cmap=custom_cmap or plt.cm.viridis,
    #     extent=self.config["hexagon_extent"],
    # )

    # # Add a color bar for shooting efficiency
    # plt.colorbar(efficiency_hexbin, ax=ax, label="Shooting Efficiency")

    # self.draw_court(ax)
    # ax.set_xlim([-800, 800])
    # ax.set_ylim([-200, 1300])

    # if title:
    #     ax.set_title(
    #         title,
    #         fontsize=self.config["title"]["fontsize"],
    #         fontweight=self.config["title"]["fontweight"],
    #         color=self.config["title"]["color"],
    #     )

    # plt.show()


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
