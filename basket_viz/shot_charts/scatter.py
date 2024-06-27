from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import pandas as pd
import matplotlib.animation as animation

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import pandas as pd


class ShotChart:
    def __init__(self, config=None):
        default_config = {
            "color_map": {"made": "#66B2FF", "miss": "#FF6F61"},
            "marker_size": 10,
            "figsize": (10, 7),
            "court_line_color": "black",
            "line_width": 1,
            "outer_lines": True,
            "court_background_color": "white",
            "plot_shots": "all",  # options: 'all', 'made', 'miss'
            "coord_x": "COORD_X",
            "coord_y": "COORD_Y",
        }
        self.config = {**default_config, **(config or {})}

    def set_config_param(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
            else:
                raise KeyError(
                    f"Config parameter '{key}' is not a valid config option."
                )

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
            ax.set_title(title)
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
    # refactor field_goal_scatter_temporal to use the config
    # add euroleague wraper to plot player or team shots
    # add output settings

    def plot_field_goal_scatter_temporal(
        self, made, miss, title=None, gif_path="shots.gif"
    ):
        made["Result"] = "Made"
        miss["Result"] = "Missed"
        shots = pd.concat([made, miss])
        shots.sort_values(by="UTC", inplace=True)

        fig, ax = plt.subplots(figsize=self.figsize)
        self.draw_court(ax)
        plt.xlim([-800, 800])
        plt.ylim([-200, 1300])
        plt.title(title)

        made_shots_x, made_shots_y = [], []
        missed_shots_x, missed_shots_y = [], []
        ims = []

        for _, shot in shots.iterrows():
            if shot["Result"] == "Made":
                made_shots_x.append(shot["COORD_X"])
                made_shots_y.append(shot["COORD_Y"])
            else:
                missed_shots_x.append(shot["COORD_X"])
                missed_shots_y.append(shot["COORD_Y"])

            im = ax.plot(
                made_shots_x,
                made_shots_y,
                "o",
                color=self.color_map["made"],
                markersize=self.marker_size,
                label="Made",
            )
            im += ax.plot(
                missed_shots_x,
                missed_shots_y,
                "x",
                color=self.color_map["miss"],
                markerfacecolor="none",
                markersize=self.marker_size,
                label="Missed",
            )
            ims.append(im)

        ani = animation.ArtistAnimation(
            fig, ims, interval=100, blit=True, repeat_delay=1000
        )
        ani.save(gif_path, writer="pillow")
        plt.show()


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
