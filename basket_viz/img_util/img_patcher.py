from io import BytesIO

import numpy as np
import requests
from PIL import Image, ImageDraw
from matplotlib.offsetbox import AnnotationBbox, OffsetImage


class ImagePatcher:
    def __init__(
        self, img_path, img_size=(300, 300), ellipse_coords=None, text_params=None
    ):
        self.img_path = img_path
        self.img_size = img_size
        self.img = self._load_image()

        # Ellipse coordinates (default to a full circle if not provided)
        self.ellipse_coords = (
            ellipse_coords if ellipse_coords else (0, 0) + self.img.size
        )

        # Text parameters for positioning
        self.text_params = (
            text_params
            if text_params
            else {
                "ha": "center",
                "va": "top",
                "text_offset_y": 0.21,  # default vertical offset for text
            }
        )

    def _load_image(self):
        """Load the image and resize it."""
        img = Image.open(self.img_path).convert("RGBA")
        return img.resize(self.img_size, Image.LANCZOS)

    def create_circular_mask(self):
        """Create a circular mask for the image using the provided or default ellipse coordinates."""
        mask = Image.new("L", self.img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(self.ellipse_coords, fill=255)
        self.img.putalpha(mask)

    def add_circular_border(self, border_color=None, border_width=20):
        """Add a circular border around the image."""
        if border_color and border_width > 0:
            border_size = (
                self.img_size[0] + border_width * 2,
                self.img_size[1] + border_width * 2,
            )
            border_img = Image.new("RGBA", border_size)
            border_draw = ImageDraw.Draw(border_img)

            # Draw the border ellipse with dynamic size
            border_draw.ellipse(
                (
                    border_width // 2,
                    border_width // 2,
                    border_size[0] - border_width // 2,
                    border_size[1] - border_width // 2,
                ),
                outline=border_color,
                width=border_width,
            )

            # Paste the original image onto the center of the border image
            border_img.paste(self.img, (border_width, border_width), self.img)
            self.img = border_img

    def convert_to_offset_image(self, zoom=0.5):
        """Convert the image to a numpy array and create an OffsetImage."""
        img_array = np.array(self.img)
        return OffsetImage(img_array, zoom=zoom)

    def get_text_position(self, position):
        """Calculate the text position using the dynamic parameters."""
        return position[0], position[1] - self.text_params["text_offset_y"]

    def add_circular_image(
        self,
        ax,
        zoom=0.5,
        position=(0.5, 0.5),
        border_color=None,
        border_width=20,
        text=None,
        text_color="black",
        text_size=16,
    ):
        """
        Adds a circular image with an optional border to the given axis at the specified position.
        """
        # Create a circular mask
        self.create_circular_mask()

        # Add a circular border if specified
        self.add_circular_border(border_color, border_width)

        # Convert the image to OffsetImage
        offset_image = self.convert_to_offset_image(zoom=zoom)

        # Create an AnnotationBbox and position it at the specified position
        ab = AnnotationBbox(
            offset_image,
            position,
            frameon=False,
            xycoords="axes fraction",
            boxcoords="axes fraction",
            pad=0,
        )

        # Add the image to the plot
        ax.add_artist(ab)

        # Add text if specified
        if text:
            text_position = self.get_text_position(position)
            ax.text(
                text_position[0],
                text_position[1],
                text,
                ha=self.text_params["ha"],
                va=self.text_params["va"],
                fontsize=text_size,
                color=text_color,
                transform=ax.transAxes,
            )


def fetch_logo_image(url, timeout=10):
    """Download an image from a URL and return it as a ``PIL.Image``.

    Parameters
    ----------
    url : str
        Remote image URL.
    timeout : int, optional
        Request timeout in seconds.

    Returns
    -------
    PIL.Image.Image
        The downloaded image converted to RGBA.
    """

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGBA")


class InlineImagePatcher:
    """Convenience helper for patching in-memory images onto matplotlib axes."""

    def __init__(self, pil_img, img_size=(300, 300)):
        self.img = pil_img.convert("RGBA").resize(img_size, Image.LANCZOS)

    def create_circular_mask(self):
        """Apply a circular alpha mask to the current image."""

        mask = Image.new("L", self.img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + self.img.size, fill=255)
        self.img.putalpha(mask)

    def to_offset_image(self, zoom=0.5):
        """Convert the masked image to an ``OffsetImage``."""

        return OffsetImage(np.array(self.img), zoom=zoom)

    def add_circular_image(self, ax, position, zoom=0.5):
        """Draw the image onto ``ax`` at ``position`` using axis fractions."""

        self.create_circular_mask()
        offset_image = self.to_offset_image(zoom=zoom)
        ab = AnnotationBbox(
            offset_image,
            position,
            frameon=False,
            xycoords="axes fraction",
            boxcoords="axes fraction",
            pad=0,
        )
        ax.add_artist(ab)


def render_bottom_images(ax, image_urls, logo_zoom=0.12, y_offset=-0.08, img_size=(260, 260)):
    """Render a horizontal row of circular images beneath the x-axis.

    This helper is designed for stat grids but can be reused anywhere a row of
    logos needs to be positioned under a matplotlib axis without a background.
    Images are downloaded, cropped into circles, and drawn in axis-fraction
    coordinates, so they stay aligned even if limits or scales change.
    """

    if not image_urls:
        return

    n_images = len(image_urls)
    for idx, url in enumerate(image_urls):
        try:
            pil_img = fetch_logo_image(url)
            patcher = InlineImagePatcher(pil_img, img_size=img_size)
            x_position = (idx + 0.5) / n_images
            patcher.add_circular_image(
                ax=ax, position=(x_position, y_offset), zoom=logo_zoom
            )
        except Exception as exc:  # pragma: no cover - non-critical rendering aid
            print(f"⚠️ failed to render bottom image {url}: {exc}")
