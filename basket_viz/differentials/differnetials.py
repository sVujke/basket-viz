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
        self.xtick_label_fontsize = kwargs.get("xtick_label_fontsize", 12)
        self.ytick_label_fontsize = kwargs.get("ytick_label_fontsize", 12)
        self.annotation_fontsize = kwargs.get("annotation_fontsize", 10)

    def plot_differentials(
        self,
        df,
        stat_col="point_difference",
        value_left_col="value_left",
        value_right_col="value_right",
        xlabel="Stat Difference",
        ylabel="Teams",
        title="Team Stat Differentials",
    ):
        """Plots horizontal lines for the given stat in the DataFrame and annotates values."""
        # Create a new figure with the specified size
        self.fig = plt.figure(figsize=self.figsize)

        for index, row in df.iterrows():
            # Draw the horizontal line
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

            # Annotate the values on both ends of the line
            plt.text(
                min(0, row[stat_col]) - 0.5,  # Slightly to the left of the line start
                row["team"],
                f"{row[value_left_col]}",
                va="center",
                ha="right",
                fontsize=self.annotation_fontsize,
                color=self.hline_color,
            )
            plt.text(
                max(0, row[stat_col]) + 0.5,  # Slightly to the right of the line end
                row["team"],
                f"{row[value_right_col]}",
                va="center",
                ha="left",
                fontsize=self.annotation_fontsize,
                color=self.hline_color,
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
        plt.ylabel(ylabel, fontsize=self.label_fontsize)
        plt.title(title, fontsize=self.title_fontsize)

        # Configure tick label font sizes
        plt.xticks(fontsize=self.xtick_label_fontsize)
        plt.yticks(fontsize=self.ytick_label_fontsize)

        # Grid settings for the x-axis
        plt.grid(axis="x", linestyle="--", alpha=0.5)

        # Adjust layout
        plt.tight_layout()

    def display_chart(self):
        """Display the radar chart and any additional elements (e.g., images)."""
        if self.fig is not None:
            self.fig.show()
        else:
            print("No chart to display. Please call 'plot_differentials' first.")

    def save(self, directory="output", file_name="radar_chart", file_format=None):
        if self.fig is not None:
            LocalExport.save_plot(
                fig=self.fig,
                ani=self.ani,
                directory=directory,
                file_name=file_name,
                file_format=file_format,
            )
        else:
            print("No chart to save. Please call 'plot_differentials' first.")
