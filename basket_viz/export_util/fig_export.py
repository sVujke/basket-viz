import os


class LocalExport:
    @staticmethod
    def save_plot(
        fig=None, ani=None, directory="output", file_name="shot_chart", file_format=None
    ):
        if not os.path.exists(directory):
            os.makedirs(directory)

        if ani is not None:
            if file_format is None:
                file_format = "mp4"
            full_path = os.path.join(directory, f"{file_name}.{file_format}")
            if file_format == "gif":
                ani.save(full_path, writer="pillow")
            elif file_format == "mp4":
                ani.save(full_path, writer="ffmpeg")
            else:
                raise ValueError(
                    f"Unsupported file format for animation: {file_format}"
                )
            print(f"Saved animation to {full_path}")

        elif fig is not None and ani is None:
            if file_format is None:
                file_format = "png"
            full_path = os.path.join(directory, f"{file_name}.{file_format}")
            fig.savefig(full_path)
            print(f"Saved figure to {full_path}")

        else:
            raise ValueError("No plot or animation available to save.")
