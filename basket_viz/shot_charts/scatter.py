from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import pandas as pd
import matplotlib.animation as animation

class ShotChart:
    def __init__(self, color_map=None, marker_size=10, figsize=(10, 7)):
        self.color_map = color_map if color_map else {'made': '#66B2FF', 'miss': '#FF6F61'}
        self.marker_size = marker_size
        self.figsize = figsize

    def draw_court(self, ax=None, color='black', lw=1, outer_lines=True):
        if ax is None:
            ax = plt.gca()

        # Create the basketball hoop
        hoop = Circle((0, 0), radius=45.72 / 2, linewidth=lw, color=color, fill=False)
        # Create backboard
        backboard = Rectangle((-90, -157.5 + 120), 180, -1, linewidth=lw, color=color)
        # The paint
        outer_box = Rectangle((-490 / 2, -157.5), 490, 580, linewidth=lw, color=color, fill=False)
        inner_box = Rectangle((-360 / 2, -157.5), 360, 580, linewidth=lw, color=color, fill=False)
        # Create free throw top arc
        top_free_throw = Arc((0, 580 - 157.5), 360, 360, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)
        # Create free throw bottom arc
        bottom_free_throw = Arc((0, 580 - 157.5), 360, 360, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='dashed')
        # Restricted Zone
        restricted = Arc((0, 0), 2 * 125, 2 * 125, theta1=0, theta2=180, linewidth=lw, color=color)
        # Three point line
        corner_three_a = Rectangle((-750 + 90, -157.5), 0, 305, linewidth=lw, color=color)
        corner_three_b = Rectangle((750 - 90, -157.5), 0, 305, linewidth=lw, color=color)
        three_arc = Arc((0, 0), 2 * 675, 2 * 675, theta1=12, theta2=167.5, linewidth=lw, color=color)
        # Center Court
        center_outer_arc = Arc((0, 1400 - 157.5), 2 * 180, 2 * 180, theta1=180, theta2=0, linewidth=lw, color=color)

        court_elements = [hoop, backboard, outer_box, inner_box, restricted, top_free_throw, bottom_free_throw,
                          corner_three_a, corner_three_b, three_arc, center_outer_arc]
        if outer_lines:
            outer_lines = Rectangle((-750, -157.5), 1500, 1400, linewidth=lw, color=color, fill=False)
            court_elements.append(outer_lines)

        for element in court_elements:
            ax.add_patch(element)

        return ax

    def plot_field_goal_scatter(self, made, miss, title=None):
        plt.figure(figsize=self.figsize)
        self.draw_court()
        plt.plot(made['COORD_X'], made['COORD_Y'], 'o', label='Made', color=self.color_map['made'], markersize=self.marker_size)
        plt.plot(miss['COORD_X'], miss['COORD_Y'], 'x', color=self.color_map['miss'], markersize=self.marker_size, label='Missed')
        plt.legend(loc='upper right', bbox_to_anchor=(0.95, 0.95), prop={'size': 14})
        plt.xlim([-800, 800])
        plt.ylim([-200, 1300])
        plt.title(title)
        plt.show()

    def plot_field_goal_scatter_temporal(self, made, miss, title=None, gif_path='shots.gif'):
        made['Result'] = 'Made'
        miss['Result'] = 'Missed'
        shots = pd.concat([made, miss])
        shots.sort_values(by='UTC', inplace=True)

        fig, ax = plt.subplots(figsize=self.figsize)
        self.draw_court(ax)
        plt.xlim([-800, 800])
        plt.ylim([-200, 1300])
        plt.title(title)

        made_shots_x, made_shots_y = [], []
        missed_shots_x, missed_shots_y = [], []
        ims = []

        for _, shot in shots.iterrows():
            if shot['Result'] == 'Made':
                made_shots_x.append(shot['COORD_X'])
                made_shots_y.append(shot['COORD_Y'])
            else:
                missed_shots_x.append(shot['COORD_X'])
                missed_shots_y.append(shot['COORD_Y'])

            im = ax.plot(made_shots_x, made_shots_y, 'o', color=self.color_map['made'], markersize=self.marker_size, label='Made')
            im += ax.plot(missed_shots_x, missed_shots_y, 'x', color=self.color_map['miss'], markerfacecolor='none', markersize=self.marker_size, label='Missed')
            ims.append(im)

        ani = animation.ArtistAnimation(fig, ims, interval=100, blit=True, repeat_delay=1000)
        ani.save(gif_path, writer='pillow')
        plt.show()

# Example usage
if __name__ == "__main__":
    # Assuming `made_shots` and `missed_shots` are pandas DataFrames with shot data
    made_shots = pd.DataFrame({
        'COORD_X': [100, 200, 300],
        'COORD_Y': [200, 300, 400],
        'UTC': [1, 2, 3]
    })
    missed_shots = pd.DataFrame({
        'COORD_X': [150, 250, 350],
        'COORD_Y': [250, 350, 450],
        'UTC': [1, 2, 3]
    })

    shot_chart = ShotChart()
    shot_chart.plot_field_goal_scatter(made_shots, missed_shots, title='Field Goals Scatter Plot')
    shot_chart.plot_field_goal_scatter_temporal(made_shots, missed_shots, title='Field Goals Scatter Plot Temporal')
