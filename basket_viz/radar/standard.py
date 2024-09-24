from math import pi
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from basket_viz.img_util.img_patcher import ImagePatcher
from basket_viz.img_util.img_processor import ImageProcessor


class RadarChart:
    def __init__(self, dataframe, columns, **kwargs):
        self.dataframe = dataframe
        self.columns = columns
        self.kwargs = kwargs
        self.fig, self.ax = None, None  # To store the figure and axis after plotting
        self.player_images = []

    def draw_radar(
        self, ax, values, angles, line_color, line_width, fill_radar, radar_fill_color
    ):
        """Helper function to draw a single radar chart on the given axis."""
        values += values[:1]
        ax.plot(
            angles, values, color=line_color, linewidth=line_width, linestyle="solid"
        )
        if fill_radar:
            fill_color = radar_fill_color if radar_fill_color else line_color
            ax.fill(angles, values, color=fill_color, alpha=0.25)

    def setup_radar_chart(self, ax, angles):
        """Helper function to set up the radar chart's aesthetics."""
        # Unpack customization parameters
        background_color = self.kwargs.get("background_color", "white")
        grid = self.kwargs.get("grid", True)
        grid_color = self.kwargs.get("circular_grid_color", "black")
        grid_linewidth = self.kwargs.get("circular_grid_linewidth", 1)
        grid_border_color = self.kwargs.get("grid_border_color", "white")
        grid_border_linewidth = self.kwargs.get("grid_border_linewidth", 1)
        label_color = self.kwargs.get("label_color", "black")
        label_fontsize = self.kwargs.get("label_fontsize", 12)
        value_color = self.kwargs.get("value_color", "black")
        value_fontsize = self.kwargs.get("value_fontsize", 10)

        ax.spines["polar"].set_color(grid_border_color)
        ax.spines["polar"].set_linewidth(grid_border_linewidth)
        ax.set_facecolor(background_color)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self.columns, color=label_color, fontsize=label_fontsize)
        ax.tick_params(colors=value_color, labelsize=value_fontsize)

        # Set figure background color if specified
        figure_bg_color = self.kwargs.get("figure_bg_color", None)
        if figure_bg_color:
            self.fig.patch.set_facecolor(figure_bg_color)

        if grid:
            ax.grid(True, color=grid_color, linewidth=grid_linewidth)
        else:
            ax.grid(False)

    def add_player_image(self, img_path):
        """Adds a circular player image in the center of the radar chart."""
        border_color = self.kwargs.get("img_border_color", "white")
        border_width = self.kwargs.get("img_border_width", 20)
        background_color = self.kwargs.get("img_background_color", None)
        if self.ax and img_path:
            ellipse_coords = (10, 10, 290, 290)
            text_params = {"ha": "center", "va": "bottom", "text_offset_y": 0.15}

            patcher = ImagePatcher(
                img_path,
                img_size=(300, 300),
                ellipse_coords=ellipse_coords,
                text_params=text_params,
            )

            patcher.add_circular_image(
                self.ax,
                zoom=0.5,
                position=(0.5, 0.5),
                border_color=border_color,
                border_width=border_width,
            )

    def plot_radar(self, player_name):
        """Creates the radar chart without the image."""
        # Prepare the radar chart data
        df = self.dataframe
        df = df[df["player"] == player_name]
        df = df[self.columns]

        values = df.iloc[0].tolist()
        num_vars = len(self.columns)
        angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
        angles += angles[:1]

        # Set up the radar chart figure and axis
        figsize = self.kwargs.get("figsize", (12, 10))
        self.fig, self.ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

        # Set up the radar chart aesthetics
        self.setup_radar_chart(self.ax, angles)

        # Plot the values on the radar chart
        line_color = self.kwargs.get("line_color", "blue")
        line_width = self.kwargs.get("line_width", 2)
        fill_radar = self.kwargs.get("fill_radar", True)
        radar_fill_color = self.kwargs.get("radar_fill_color", None)

        self.draw_radar(
            self.ax,
            values,
            angles,
            line_color,
            line_width,
            fill_radar,
            radar_fill_color,
        )

        # Add the title
        title_color = self.kwargs.get("title_color", "green")
        title_fontsize = self.kwargs.get("title_fontsize", 20)
        plt.title(player_name, size=title_fontsize, color=title_color, y=1.05)

    def _process_player_image(self, player_name, output_path):
        url = self.dataframe[self.dataframe["player"] == player_name][
            "player.imageUrl"
        ].values[0]

        processor = ImageProcessor()

        processor.download(url)

        width, height = processor.image.size
        processor.crop(0, 0, width, height // 1.4)
        processor.save(output_path)

        return output_path

    def add_comparison_images(self, start_x=0.2, spacing=0.3, y_offset=-0.2):
        """Adds player images and names below the radar chart with configurable positions."""
        if not self.ax:
            return

        for player_name in self.player_names:
            img_path = self._process_player_image(player_name, f"{player_name}.png")
            self.player_images.append(img_path)

        num_images = len(self.player_images)

        # Calculate starting x position to center the images
        if num_images > 1:
            start_x = 0.5 - (spacing * (num_images - 1)) / 2

        for i, (img_path, player_name, color) in enumerate(
            zip(self.player_images, self.player_names, self.line_colors)
        ):
            # Calculate the position for each image
            position = (start_x + i * spacing, y_offset)

            # Add the circular image
            patcher = ImagePatcher(
                img_path,
                img_size=(300, 300),
                ellipse_coords=(10, 10, 290, 290),
                text_params={"ha": "center", "va": "bottom", "text_offset_y": 0.15},
            )
            patcher.add_circular_image(
                self.ax, zoom=0.4, position=position, border_color=color
            )

            # Add player name below the image
            self.ax.text(
                position[0],
                position[1] - 0.15,
                player_name,
                ha="center",
                color=color,
                fontsize=14,
                transform=self.ax.transAxes,
            )

    def compare_radars(
        self,
        player_names,
        line_colors=None,
        line_widths=2,
        fill_radars=True,
        radar_fill_colors=None,
        figure_bg_color=None,
        figsize=(12, 10),
    ):
        """Creates a radar chart comparing multiple players on the same chart."""
        # Store the players' names, images, and colors for later use
        self.player_names = player_names
        self.line_colors = line_colors if line_colors else ["blue"] * len(player_names)

        num_vars = len(self.columns)
        angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
        angles += angles[:1]

        # Set up the radar chart figure and axis
        self.fig, self.ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
        if figure_bg_color:
            self.fig.patch.set_facecolor(figure_bg_color)

        # Set up the radar chart aesthetics
        self.setup_radar_chart(self.ax, angles)

        for i, player_name in enumerate(player_names):
            df_player = self.dataframe[self.dataframe["player"] == player_name][
                self.columns
            ]
            values = df_player.iloc[0].tolist()

            color = self.line_colors[i]
            width = line_widths[i] if isinstance(line_widths, list) else line_widths

            self.draw_radar(
                self.ax,
                values,
                angles,
                color,
                width,
                fill_radars,
                radar_fill_colors[i] if radar_fill_colors else color,
            )

    def display_chart(self):
        """Display the radar chart and any additional elements (e.g., images)."""
        plt.show()


if __name__ == "__main__":
    pass
