# from math import pi

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.path import Path
# from matplotlib.offsetbox import OffsetImage, AnnotationBbox
# import matplotlib.image as mpimg
# from PIL import Image, ImageDraw
# from basket_viz.img_util.img_patcher import ImagePatcher


# def draw_radar(
#     ax, values, angles, line_color, line_width, fill_radar, radar_fill_color
# ):
#     """Helper function to draw a single radar chart on the given axis."""
#     values += values[:1]
#     ax.plot(angles, values, color=line_color, linewidth=line_width, linestyle="solid")
#     if fill_radar:
#         fill_color = radar_fill_color if radar_fill_color else line_color
#         ax.fill(angles, values, color=fill_color, alpha=0.25)


# def setup_radar_chart(
#     ax,
#     columns,
#     angles,
#     background_color,
#     grid,
#     grid_color,
#     grid_linewidth,
#     grid_border_color,
#     grid_border_linewidth,
#     label_color,
#     label_fontsize,
#     value_color,
#     value_fontsize,
# ):
#     """Helper function to set up the radar chart's aesthetics."""
#     ax.spines["polar"].set_color(grid_border_color)
#     ax.spines["polar"].set_linewidth(grid_border_linewidth)
#     ax.set_facecolor(background_color)
#     ax.set_xticks(angles[:-1])
#     ax.set_xticklabels(columns, color=label_color, fontsize=label_fontsize)
#     ax.tick_params(colors=value_color, labelsize=value_fontsize)
#     if grid:
#         ax.grid(True, color=grid_color, linewidth=grid_linewidth)
#     else:
#         ax.grid(False)


# def add_player_images(fig, ax, player_images, player_names, line_colors):
#     """Helper function to add player images below the radar chart with colored names."""
#     for i, (img_path, player_name, color) in enumerate(
#         zip(player_images, player_names, line_colors)
#     ):
#         # Calculate the position for the image
#         position = (0.3 + i * 0.4, -0.2)

#         # Add the circular image using the existing add_circular_image function
#         add_circular_image(
#             ax,
#             img_path,
#             zoom=0.4,
#             img_size=(300, 300),
#             position=position,
#             border_color=color,
#             border_width=5,
#             text=player_name,
#             text_color=color,
#             text_size=16,
#         )

#         # Add player name below the image
#         # fig.text(0.3 + i * 0.4, -0.23, player_name, ha='center', color=color, fontsize=14)


# def compare_radars(
#     dataframe,
#     columns,
#     player_names,
#     player_images,
#     line_colors=None,
#     line_widths=2,
#     background_color="white",
#     grid=True,
#     grid_color="black",
#     grid_linewidth=1,
#     fill_radars=True,
#     radar_fill_colors=None,
#     figure_bg_color=None,
#     title_color="green",
#     title_fontsize=20,
#     label_color="black",
#     label_fontsize=12,
#     value_color="black",
#     value_fontsize=10,
#     grid_border_color="white",
#     grid_border_linewidth=1,
#     figsize=(12, 10),
#     **kwargs
# ):
#     """Creates a radar chart comparing multiple players on the same chart."""
#     num_vars = len(columns)
#     angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
#     angles += angles[:1]

#     fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
#     if figure_bg_color:
#         fig.patch.set_facecolor(figure_bg_color)

#     setup_radar_chart(
#         ax,
#         columns,
#         angles,
#         background_color,
#         grid,
#         grid_color,
#         grid_linewidth,
#         grid_border_color,
#         grid_border_linewidth,
#         label_color,
#         label_fontsize,
#         value_color,
#         value_fontsize,
#     )

#     for i, player_name in enumerate(player_names):
#         df_player = dataframe[dataframe["player"] == player_name][columns]
#         values = df_player.iloc[0].tolist()

#         color = line_colors[i] if line_colors else "blue"
#         width = line_widths[i] if isinstance(line_widths, list) else line_widths

#         draw_radar(
#             ax,
#             values,
#             angles,
#             color,
#             width,
#             fill_radars,
#             radar_fill_colors[i] if radar_fill_colors else color,
#         )

#     # plt.title(", ".join(player_names), size=title_fontsize, color=title_color, y=1.05)

#     # Add player images and names below the radar chart
#     add_player_images(fig, ax, player_images, player_names, line_colors)

#     plt.show()


# # Example usage
# # Generate example dataframe
# np.random.seed(0)
# data = {
#     "player": ["Player 1", "Player 2", "Player 3"],
#     "stat1": np.random.randint(50, 100, 3),
#     "stat2": np.random.randint(50, 100, 3),
#     "stat3": np.random.randint(50, 100, 3),
#     "stat4": np.random.randint(50, 100, 3),
#     "stat5": np.random.randint(50, 100, 3),
# }

# df = pd.DataFrame(data)

# # Define paths to player images
# player_images = ["path_to_player1_image.jpg", "path_to_player2_image.jpg"]
# img_path_v = "/Users/stef/Documents/dev/basket-viz/notebooks/media/veseli.jpeg"


# # def add_circular_image(
# #     ax,
# #     img_path,
# #     zoom=0.5,
# #     img_size=(300, 300),
# #     position=(0.5, 0.5),
# #     border_color=None,
# #     border_width=20,
# #     text=None,
# #     text_color="black",
# #     text_size=16,
# # ):
# #     """
# #     Adds a circular image with an optional border to the given axis at the specified position.

# #     Parameters:
# #     - ax: The axis to which the image should be added.
# #     - img_path: The path to the image file.
# #     - zoom: The zoom level for the image.
# #     - img_size: The size to which the image should be resized.
# #     - position: The (x, y) position where the image should be placed.
# #     - border_color: Color of the circular border (if any).
# #     - border_width: The width of the border.
# #     """
# #     # Load the image and resize it with better quality
# #     img = Image.open(img_path).convert("RGBA")
# #     img = img.resize(img_size, Image.LANCZOS)  # Resize to a specified size

# #     # Create a circular mask
# #     mask = Image.new("L", img.size, 0)
# #     draw = ImageDraw.Draw(mask)
# #     draw.ellipse((0, 0) + img.size, fill=255)
# #     img.putalpha(mask)

# #     # Add a circular border if specified
# #     if border_color and border_width > 0:
# #         # Create a new image that includes the border
# #         border_size = (img_size[0] + border_width * 2, img_size[1] + border_width * 2)
# #         border_img = Image.new("RGBA", border_size)
# #         border_draw = ImageDraw.Draw(border_img)

# #         # Draw the border ellipse on the larger image
# #         border_draw.ellipse(
# #             (
# #                 border_width // 2,
# #                 border_width // 2,
# #                 border_size[0] - border_width // 2,
# #                 border_size[1] - border_width // 2,
# #             ),
# #             outline=border_color,
# #             width=border_width,
# #         )

# #         # Paste the original image onto the center of the border image
# #         border_img.paste(img, (border_width, border_width), img)
# #         img = border_img

# #     # Convert to numpy array and create an OffsetImage
# #     img = np.array(img)
# #     imagebox = OffsetImage(img, zoom=zoom)

# #     # Create an AnnotationBbox and position it at the specified position
# #     ab = AnnotationBbox(
# #         imagebox,
# #         position,
# #         frameon=False,
# #         xycoords="axes fraction",
# #         boxcoords="axes fraction",
# #         pad=0,
# #     )

# #     # Add the image to the plot
# #     ax.add_artist(ab)

# #     if text:
# #         ax.text(
# #             position[0],
# #             position[1] - 0.21,
# #             text,
# #             ha="center",
# #             va="top",
# #             fontsize=16,
# #             color=text_color,
# #             transform=ax.transAxes,
# #         )


# # Call the compare_radars function
# # compare_radars(
# #     dataframe=df,
# #     columns=["stat1", "stat2", "stat3", "stat4", "stat5"],
# #     player_names=["Player 1", "Player 2"],
# #     player_images=[img_path, img_path_v],  # List of paths to the player images
# #     line_colors=["green", "red"],
# #     line_widths=[2, 3],
# #     radar_fill_colors=["blue", "red"],
# #     figsize=(10, 8),
# # )


# def radar_chart(
#     dataframe,
#     columns,
#     player_name,
#     line_color="blue",
#     line_width=2,
#     background_color="white",
#     grid=True,
#     grid_color="black",
#     grid_linewidth=1,
#     img_path=None,
#     fill_radar=True,
#     radar_fill_color=None,
#     figure_bg_color=None,
#     title_color="green",
#     title_fontsize=20,
#     label_color="black",
#     label_fontsize=12,
#     value_color="black",
#     value_fontsize=10,
#     grid_border_color="white",
#     grid_border_linewidth=1,
#     figsize=(12, 10),
#     **kwargs
# ):
#     """
#     Creates a radar chart with various customization options.

#     Parameters:
#     - dataframe: The dataframe containing the data to plot.
#     - columns: List of columns to include in the radar chart.
#     - player_name: Title of the radar chart.
#     - line_color: Color of the radar chart lines.
#     - line_width: Width of the radar chart lines.
#     - background_color: Color of the radar chart background.
#     - grid: Whether to display the grid.
#     - grid_color: Color of the grid lines.
#     - grid_linewidth: Width of the grid lines.
#     - img_path: Path to the image to be added to the center of the radar chart.
#     - fill_radar: Whether to fill the radar chart or only draw the border.
#     - radar_fill_color: Color to fill the radar chart (if fill_radar is True).
#     - figure_bg_color: Background color for the entire figure.
#     - title_color: Color of the title text.
#     - title_fontsize: Font size of the title text.
#     - label_color: Color of the column labels.
#     - label_fontsize: Font size of the column labels.
#     - value_color: Color of the values on the grid.
#     - value_fontsize: Font size of the values on the grid.
#     - **kwargs: Additional keyword arguments for customization.
#     """

#     # Filter the dataframe based on the provided columns
#     df = dataframe[columns]

#     # Extract values from the first row of the dataframe for the given columns
#     values = df.iloc[0].tolist()

#     # Number of variables we're plotting
#     num_vars = len(columns)

#     # Compute angle for each axis
#     angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
#     angles += angles[:1]

#     # Initialize the radar chart
#     fig, ax = plt.subplots(figsize=(figsize), subplot_kw=dict(polar=True))

#     # Set figure background color if specified
#     if figure_bg_color:
#         fig.patch.set_facecolor(figure_bg_color)

#     # Assuming ax is your polar plot axis
#     ax.spines["polar"].set_color(grid_border_color)  # Set the color of the outer circle
#     ax.spines["polar"].set_linewidth(
#         grid_border_linewidth
#     )  # Set the width of the outer circle

#     # Draw one axis per variable + add labels
#     plt.xticks(angles[:-1], columns, color=label_color, fontsize=label_fontsize)

#     # Draw ylabels with specified color and fontsize
#     ax.tick_params(colors=value_color, labelsize=value_fontsize)

#     # Set background color
#     ax.set_facecolor(background_color)

#     # Set grid visibility and customization
#     if grid:
#         ax.grid(
#             True,
#             color=grid_color,
#             linewidth=grid_linewidth,
#         )
#     else:
#         ax.grid(False)

#     # Plot the values
#     values += values[:1]
#     ax.plot(angles, values, color=line_color, linewidth=line_width, linestyle="solid")

#     # Fill the radar chart if specified
#     if fill_radar:
#         fill_color = radar_fill_color if radar_fill_color else line_color
#         ax.fill(angles, values, color=fill_color, alpha=0.25)

#     # Add a title with custom color and fontsize
#     plt.title(player_name, size=title_fontsize, color=title_color, y=1.05)
#     # Add the circular image to the center using the separate function (if provided)
#     if img_path:
#         ellipse_coords = (10, 10, 290, 290)
#         text_params = {"ha": "center", "va": "bottom", "text_offset_y": 0.15}

#         patcher = ImagePatcher(
#             img_path,
#             img_size=(300, 300),
#             ellipse_coords=ellipse_coords,
#             text_params=text_params,
#         )

#         patcher.add_circular_image(ax, zoom=0.4, position=(0.5, 0.5))
#     plt.show()


# if __name__ == "__main__":
#     pass

from math import pi
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from basket_viz.img_util.img_patcher import ImagePatcher


class RadarChart:
    def __init__(self, dataframe, columns, player_name, **kwargs):
        self.dataframe = dataframe
        self.columns = columns
        self.player_name = player_name
        self.kwargs = kwargs
        self.fig, self.ax = None, None  # To store the figure and axis after plotting

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
        grid_color = self.kwargs.get("grid_color", "black")
        grid_linewidth = self.kwargs.get("grid_linewidth", 1)
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

        if grid:
            ax.grid(True, color=grid_color, linewidth=grid_linewidth)
        else:
            ax.grid(False)

    def add_player_image(self, img_path):
        """Adds a circular player image in the center of the radar chart."""
        if self.ax and img_path:
            ellipse_coords = (10, 10, 290, 290)
            text_params = {"ha": "center", "va": "bottom", "text_offset_y": 0.15}

            patcher = ImagePatcher(
                img_path,
                img_size=(300, 300),
                ellipse_coords=ellipse_coords,
                text_params=text_params,
            )

            patcher.add_circular_image(self.ax, zoom=0.4, position=(0.5, 0.5))

    def plot_radar(self):
        """Creates the radar chart without the image."""
        # Prepare the radar chart data
        df = self.dataframe[self.columns]
        values = df.iloc[0].tolist()
        num_vars = len(self.columns)
        angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
        angles += angles[:1]

        # Set up the radar chart figure and axis
        figsize = self.kwargs.get("figsize", (12, 10))
        self.fig, self.ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

        # Set figure background color if specified
        figure_bg_color = self.kwargs.get("figure_bg_color", None)
        if figure_bg_color:
            self.fig.patch.set_facecolor(figure_bg_color)

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
        plt.title(self.player_name, size=title_fontsize, color=title_color, y=1.05)

    def add_comparison_images(self, start_x=0.2, spacing=0.3, y_offset=-0.2):
        """Adds player images and names below the radar chart with configurable positions."""
        if not self.ax:
            return

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
        player_images,
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
        self.player_images = player_images
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


# Example usage
if __name__ == "__main__":
    # Generate example dataframe
    pass
    # np.random.seed(0)
    # data = {
    #     "player": ["Player 1"],
    #     "stat1": np.random.randint(50, 100, 1),
    #     "stat2": np.random.randint(50, 100, 1),
    #     "stat3": np.random.randint(50, 100, 1),
    #     "stat4": np.random.randint(50, 100, 1),
    #     "stat5": np.random.randint(50, 100, 1),
    # }

    # df = pd.DataFrame(data)

    # # Path to the player image
    # img_path = "/path/to/player_image.jpg"

    # # Create a RadarChart object and plot the radar chart
    # radar_chart = RadarChart(
    #     dataframe=df,
    #     player_name="Player 1",
    #     line_color="blue",
    #     radar_fill_color="lightblue",
    #     img_path=img_path,
    # )

    # radar_chart.plot_radar()
