import pandas as pd
import matplotlib.pyplot as plt
from basket_viz.export_util.fig_export import LocalExport


class Differentials:
    def __init__(self, figsize=(12, 10), **kwargs):
        self.figsize = figsize
        self.kwargs = kwargs
        self.fig = None
        self.ani = None

        # Default parameters for visual configuration
        self.hline_color = kwargs.get("hline_color", "blue")
        self.hline_linewidth = kwargs.get("hline_linewidth", 2)
        self.hline_alpha = kwargs.get("hline_alpha", 1.0)

        self.point_marker_color = kwargs.get("point_marker_color", "red")
        self.point_marker_style = kwargs.get("point_marker_style", "o")

        self.reference_line_color = kwargs.get("reference_line_color", "black")
        self.reference_line_width = kwargs.get("reference_line_width", 0.5)
        self.reference_line_alpha = kwargs.get("reference_line_alpha", 1.0)

        self.fontsize = kwargs.get("fontsize", 12)
        self.title_fontsize = kwargs.get("title_fontsize", 16)
        self.label_fontsize = kwargs.get("label_fontsize", 14)

    def plot_differentials(
        self,
        df,
        stat_col="point_difference",
        xlabel="Stat Difference",
        title="Team Stat Differentials",
    ):
        """Plots horizontal lines for the given stat in the DataFrame."""
        # Ensure the figure is created with the given size
        self.fig = plt.figure(figsize=self.figsize)

        for index, row in df.iterrows():
            plt.hlines(
                y=row["team"],
                xmin=min(0, row[stat_col]),
                xmax=max(0, row[stat_col]),
                color=self.hline_color,
                linewidth=self.hline_linewidth,
                alpha=self.hline_alpha,
            )
            # Mark the end of the line with a point
            plt.plot(
                [row[stat_col]],  # x-coordinate as a list
                [row["team"]],  # y-coordinate as a list
                color=self.point_marker_color,
                marker=self.point_marker_style,
            )

        # Plot reference line at 0
        plt.axvline(
            0,
            color=self.reference_line_color,
            linewidth=self.reference_line_width,
            alpha=self.reference_line_alpha,
        )

        # Set labels and title with customizable font sizes
        plt.xlabel(xlabel, fontsize=self.label_fontsize)
        plt.title(title, fontsize=self.title_fontsize)

        # Grid settings for the x-axis
        plt.grid(axis="x", linestyle="--", alpha=0.5)

        plt.tight_layout()

    def display_chart(self):
        """Display the radar chart and any additional elements (e.g., images)."""
        plt.show()

    def save(self, directory="output", file_name="radar_chart", file_format=None):
        LocalExport.save_plot(
            fig=self.fig,
            ani=self.ani,
            directory=directory,
            file_name=file_name,
            file_format=file_format,
        )
