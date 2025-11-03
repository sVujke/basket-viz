"""Modular scatter relationship plot with configurable overlays and annotations."""

from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.offsetbox import AnnotationBbox
from PIL import Image

from basket_viz.export_util.fig_export import LocalExport
from basket_viz.img_util.img_processor import ImageProcessor


class PlotRelation:
    """Create configurable scatter relationship plots with optional player imagery."""

    def __init__(self, dataframe: pd.DataFrame, columns: Optional[Dict[str, str]] = None, **kwargs):
        self.df = dataframe.copy()
        self.columns = columns or {}
        self.kwargs = kwargs

        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None
        self.ani = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def plot_relationship(self, highlight_df: Optional[pd.DataFrame] = None) -> plt.Axes:
        """Render the base scatter relationship with optional highlight annotations."""

        self._validate_dataframe_columns(
            self.df,
            (
                self._get_column("x", "minutesPlayed"),
                self._get_column("y", "foulsDrawn"),
            ),
        )

        self.setup_chart()
        self.draw_base()
        self.draw_regression_line()

        if highlight_df is not None and not highlight_df.empty:
            self.add_player_annotations(highlight_df)

        self._apply_labels()
        self._apply_limits()
        self._apply_grid()

        self.fig.tight_layout()
        return self.ax

    def add_player_annotations(self, highlight_df: pd.DataFrame) -> None:
        """Add player headshots and labels for highlighted rows."""

        if highlight_df is None or highlight_df.empty:
            return

        if self.ax is None:
            raise ValueError("Axes not initialized. Call setup_chart() before adding annotations.")

        x_col = self._get_column("x", "minutesPlayed")
        y_col = self._get_column("y", "foulsDrawn")
        label_col = self._get_column("label", "PLAYER")
        image_col = self._get_column("image", "PLAYER_IMAGE")

        self._validate_dataframe_columns(highlight_df, (x_col, y_col, label_col, image_col), optional=True)

        text_padding = self.kwargs.get("name_vertical_padding", 0.4)

        for _, row in highlight_df.iterrows():
            image_url = row.get(image_col)
            if not image_url:
                continue

            processor = ImageProcessor()
            try:
                processor.download(image_url)
            except Exception:
                continue

            image = processor.get_image()
            if image is None:
                continue

            zoom, offset = self._resolve_image_position(image)

            try:
                offset_image = processor.to_offset_image(zoom=zoom)
            except ValueError:
                continue

            x_value = row.get(x_col)
            y_value = row.get(y_col)
            if pd.isna(x_value) or pd.isna(y_value):
                continue

            annotation = AnnotationBbox(offset_image, (x_value, y_value + offset), frameon=False)
            self.ax.add_artist(annotation)

            formatted_name = self._format_player_name(str(row.get(label_col, "")))
            if formatted_name:
                self.ax.text(
                    x_value,
                    y_value + offset - text_padding,
                    formatted_name,
                    ha=self.kwargs.get("name_ha", "center"),
                    va=self.kwargs.get("name_va", "top"),
                    fontsize=self.kwargs.get("name_fontsize", 7),
                    color=self.kwargs.get("name_color", "#222222"),
                )

    def display_chart(self) -> None:
        """Display the plotted figure."""

        if self.fig is None:
            raise ValueError("No figure has been created. Call plot_relationship() first.")
        plt.show()

    def save(
        self,
        directory: Optional[str] = None,
        file_name: Optional[str] = None,
        file_format: Optional[str] = None,
    ) -> None:
        """Persist the current figure using the shared export utility."""

        if self.fig is None and self.ani is None:
            raise ValueError("Nothing to save. Run plot_relationship() before calling save().")

        export_dir = directory or self.kwargs.get("export_directory", "output")
        export_name = file_name or self.kwargs.get("export_file_name", "relationship_plot")

        LocalExport.save_plot(
            fig=self.fig,
            ani=self.ani,
            directory=export_dir,
            file_name=export_name,
            file_format=file_format or self.kwargs.get("export_format"),
        )

    # ------------------------------------------------------------------
    # Setup & drawing helpers
    # ------------------------------------------------------------------
    def setup_chart(self) -> None:
        """Initialize the matplotlib figure and axis."""

        figure_size = self.kwargs.get("figure_size", (14, 10))
        top_margin = self.kwargs.get("top_margin", 0.85)
        figure_bg_color = self.kwargs.get("figure_bg_color", "white")
        axes_bg_color = self.kwargs.get("axes_bg_color", figure_bg_color)

        if self.fig is None or self.ax is None:
            self.fig, self.ax = plt.subplots(figsize=figure_size)
        else:
            self.ax.clear()
            self.fig.set_size_inches(*figure_size)

        self.fig.subplots_adjust(top=top_margin)
        self.fig.patch.set_facecolor(figure_bg_color)
        self.ax.set_facecolor(axes_bg_color)

    def draw_base(self) -> None:
        """Draw the scatter layer for the relationship plot."""

        x_col = self._get_column("x", "minutesPlayed")
        y_col = self._get_column("y", "foulsDrawn")

        scatter_df = self.df[[x_col, y_col]].dropna()

        self.ax.scatter(
            scatter_df[x_col],
            scatter_df[y_col],
            color=self.kwargs.get("scatter_color", "#CFCFCF"),
            alpha=self.kwargs.get("scatter_alpha", 0.7),
            s=self.kwargs.get("scatter_size", 30),
        )

    def draw_regression_line(self) -> None:
        """Draw a polynomial regression line across the scatter plot."""

        if not self.kwargs.get("show_regression", True):
            return

        x_col = self._get_column("x", "minutesPlayed")
        y_col = self._get_column("y", "foulsDrawn")

        numeric_df = self.df[[x_col, y_col]].dropna()
        if numeric_df.empty:
            return

        degree = int(self.kwargs.get("regression_degree", 1))
        x_values = numeric_df[x_col].to_numpy()
        y_values = numeric_df[y_col].to_numpy()

        coefficients = np.polyfit(x_values, y_values, degree)
        polynomial = np.poly1d(coefficients)

        x_min, x_max = x_values.min(), x_values.max()
        x_range = np.linspace(x_min, x_max, 100)
        y_range = polynomial(x_range)

        self.ax.plot(
            x_range,
            y_range,
            color=self.kwargs.get("regression_color", "black"),
            linestyle=self.kwargs.get("regression_linestyle", "--"),
            linewidth=self.kwargs.get("regression_linewidth", 1),
        )

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    def _apply_labels(self) -> None:
        """Apply title and axis labels using the shared kwargs schema."""

        title = self.kwargs.get(
            "title",
            "Minutes Played vs Fouls Drawn — EuroLeague 2025/26",
        )
        x_label = self.kwargs.get("x_label", self._label_from_column("x", "Minutes Played per Game"))
        y_label = self.kwargs.get("y_label", self._label_from_column("y", "Fouls Drawn per Game"))

        self.ax.set_title(
            title,
            pad=self.kwargs.get("title_pad", 60),
            fontsize=self.kwargs.get("title_fontsize", 25),
            color=self.kwargs.get("title_color", "#000000"),
        )
        self.ax.set_xlabel(
            x_label,
            fontsize=self.kwargs.get("axis_label_fontsize", 12),
            color=self.kwargs.get("axis_label_color", "#000000"),
        )
        self.ax.set_ylabel(
            y_label,
            fontsize=self.kwargs.get("axis_label_fontsize", 12),
            color=self.kwargs.get("axis_label_color", "#000000"),
        )

    def _apply_limits(self) -> None:
        """Expand plot limits based on configured padding."""

        x_col = self._get_column("x", "minutesPlayed")
        y_col = self._get_column("y", "foulsDrawn")

        numeric_df = self.df[[x_col, y_col]].dropna()
        if numeric_df.empty:
            return

        x_padding = self.kwargs.get("x_padding", 0.05)
        y_padding = self.kwargs.get("y_padding", 0.1)

        x_min, x_max = numeric_df[x_col].min(), numeric_df[x_col].max()
        y_min, y_max = numeric_df[y_col].min(), numeric_df[y_col].max()

        x_range = x_max - x_min
        y_range = y_max - y_min

        if x_range == 0:
            x_range = max(abs(x_max), 1) * 0.1
        if y_range == 0:
            y_range = max(abs(y_max), 1) * 0.1

        self.ax.set_xlim(
            x_min - x_range * x_padding,
            x_max + x_range * x_padding,
        )
        self.ax.set_ylim(
            y_min - y_range * y_padding,
            y_max + y_range * y_padding,
        )

    def _apply_grid(self) -> None:
        """Toggle the background grid according to configuration."""

        if not self.kwargs.get("show_grid", True):
            self.ax.grid(False)
            return

        self.ax.grid(
            alpha=self.kwargs.get("grid_alpha", 0.25),
            color=self.kwargs.get("grid_color", "#cccccc"),
            linestyle=self.kwargs.get("grid_linestyle", "-"),
        )

    # ------------------------------------------------------------------
    # Annotation helpers
    # ------------------------------------------------------------------
    def _resolve_image_position(self, image: Image.Image) -> Tuple[float, float]:
        """Determine zoom and vertical offset based on image aspect ratio."""

        base_zoom = self.kwargs.get("image_zoom", 0.08)
        base_offset = self.kwargs.get("image_y_offset", 0.35)

        aspect_ratio = image.height / max(image.width, 1)

        tall_ratio_threshold = self.kwargs.get("tall_image_ratio_threshold", 1.3)
        if aspect_ratio > tall_ratio_threshold:
            adjustment_factor = min(
                aspect_ratio / tall_ratio_threshold,
                self.kwargs.get("max_tall_image_adjustment", 1.8),
            )
            base_zoom = base_zoom / adjustment_factor
            base_offset = base_offset - 0.05 * (adjustment_factor - 1)

        return base_zoom, base_offset

    def _format_player_name(self, player_name: str) -> str:
        """Format player names using an optional formatter callable."""

        formatter: Optional[Callable[[str], str]] = self.kwargs.get("name_formatter")
        if formatter is not None:
            return formatter(player_name)

        if "," in player_name:
            return player_name.split(",")[0].title()
        return player_name.title()

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _get_column(self, key: str, default: str) -> str:
        return self.columns.get(key, default)

    def _label_from_column(self, key: str, fallback: str) -> str:
        column_name = self._get_column(key, "")
        if not column_name:
            return fallback
        return self.kwargs.get(f"{key}_label_fallback", column_name.replace("_", " ").title())

    def _validate_dataframe_columns(
        self,
        dataframe: pd.DataFrame,
        columns: Tuple[str, ...],
        optional: bool = False,
    ) -> None:
        missing = [col for col in columns if col and col not in dataframe.columns]
        if missing and not optional:
            raise KeyError(f"Required columns not found in dataframe: {', '.join(missing)}")
