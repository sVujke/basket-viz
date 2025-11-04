import requests
import numpy as np
from PIL import Image
from io import BytesIO
from matplotlib import pyplot as plt
from matplotlib.offsetbox import OffsetImage


class ImageProcessor:
    def __init__(self):
        self.image = None

    def download(self, url):
        """
        Download an image from the provided URL.
        :param url: str: URL of the image
        :return: None
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            self.image = Image.open(BytesIO(response.content))
            print("Image downloaded successfully.")
        except Exception as e:
            print(f"Failed to download the image: {e}")

    def crop(self, left, top, right, bottom):
        """
        Crop the image with the provided coordinates.
        :param left: int: Left pixel coordinate
        :param top: int: Top pixel coordinate
        :param right: int: Right pixel coordinate
        :param bottom: int: Bottom pixel coordinate
        :return: None
        """
        if self.image:
            self.image = self.image.crop((left, top, right, bottom))
            print(f"Image cropped to box: {(left, top, right, bottom)}.")
        else:
            print("No image loaded. Please download an image first.")

    def display(self):
        """
        Display the current image using matplotlib.
        :return: None
        """
        if self.image:
            plt.imshow(self.image)
            plt.axis("off")  # Hide the axes
            plt.show()
        else:
            print("No image to display. Please download and crop the image first.")

    def save(self, output_path):
        """
        Save the image to the specified file path.
        :param output_path: str: Path where the image should be saved
        :return: None
        """
        if self.image:
            self.image.save(output_path)
            print(f"Image saved at: {output_path}")
        else:
            print("No image to save. Please download and crop the image first.")

    def get_image(self):
        """Return a copy of the currently loaded image."""
        if self.image:
            return self.image.copy()
        return None

    def to_offset_image(self, zoom=0.5):
        """Convert the current image into an OffsetImage for matplotlib plots."""
        if not self.image:
            raise ValueError("No image available. Please download or load an image first.")

        img_array = np.array(self.image)
        return OffsetImage(img_array, zoom=zoom)
