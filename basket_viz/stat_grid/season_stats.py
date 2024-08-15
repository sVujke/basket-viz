import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize


class PlayerStatsHeatmap:
    def __init__(self, config=None):
        default_params = {
            "figsize": (12, 8),
            "cmap": "Greens",
            "cbar": True,
            "annot": True,
            "shape": "square",
            "linewidths": 0.5,
            "linecolor": "white",
            "highlight_params": {
                "backgroundcolor": "gray",
                "fontweight": "bold",
                "edgecolor": "black",
                "lw": 5,
            },
            "title_params": {
                "label": "Stat Heatmap by Players in Different Games vs Teams",
                "fontsize": 16,
            },
            "xlabel_params": {
                "rotation": 45,
                "ha": "right",
                "fontsize": 10,
            },
            "xlabel_title_params": {  # New section for the main x-axis label
                "xlabel": "Player vs Team vs Game",
                "fontsize": 14,
                "rotation": 0,
                "ha": "center",
            },
            "ylabel_params": {"fontsize": 14, "rotation": 0, "color": "black"},
            "ylabel_title_params": {"ylabel": "Players", "fontsize": 14},
            "columns": {  # Added config for column names
                "team": "Team",
                "player": "Player",
                "game_code": "GAME_CODE",
                "vs_team": "VS_TEAM",
            },
        }

        self.params = default_params
        if config:
            self.params.update(config)

    def get_params(self):
        """
        Get the current config parameters.
        Returns
        -------
        params : dict
            The current parameters.
        """
        return self.params

    def set_params(self, **kwargs):
        """
        Update the config parameters.
        Parameters
        ----------
        **kwargs : dict
            The parameters to update.
        Returns
        -------
        None
        """
        self.params.update(kwargs)

    def plot_stat_heatmap(self, df, team, player_names, num_games=None, stat="Points"):
        """
        Plot the heatmap of the specified stat for the players.
        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame containing the stats.
        team : str
            The team code to filter the data.
        player_names : list
            The list of player names to highlight.
        num_games : int, default None
            The number of games to consider.
        stat : str, default "Points"
            The stat to plot.
        Returns
        -------
        heatmap_data : pd.DataFrame
            The DataFrame containing the heatmap data.
        """

        heatmap_data = self._prepare_data(df, team, num_games, stat)

        plt.figure(figsize=self.params["figsize"])
        ax = plt.gca()

        if self.params["shape"] == "circle":

            ax.set_yticks(np.arange(len(heatmap_data.index) + 1) - 0.5, minor=True)
            ax.set_xticks(np.arange(len(heatmap_data.columns) + 1) - 0.5, minor=True)

            # Manually set the major ticks without overwriting the grid
            ax.set_yticks(np.arange(len(heatmap_data.index)), minor=False)
            ax.set_xticks(np.arange(len(heatmap_data.columns)), minor=False)
            ax.set_yticklabels(
                heatmap_data.index,
                va="center",
                **self.params["ylabel_params"],
            )
            ax.set_xticklabels(
                heatmap_data.columns,
                **self.params["xlabel_params"],
            )

        else:
            ax.set_yticks(np.arange(len(heatmap_data.index)) + 0.5, minor=False)
            ax.set_yticklabels(
                heatmap_data.index, va="center", **self.params["ylabel_params"]
            )
            ax.set_xticks(np.arange(len(heatmap_data.columns)) + 0.5, minor=False)
            ax.set_xticklabels(heatmap_data.columns, ha="center")

        if self.params["shape"] == "square":
            # Square mode using seaborn heatmap
            sns.heatmap(
                heatmap_data,
                annot=self.params["annot"],
                cmap=self.params["cmap"],
                cbar=self.params["cbar"],
                linewidths=self.params["linewidths"],
                linecolor=self.params["linecolor"],
                ax=ax,
            )

        elif self.params["shape"] == "circle":
            # Circle mode using PatchCollection and circles
            self._plot_circles(ax, heatmap_data)

        # Highlight the specified players' rows
        self._highlight_players(ax, heatmap_data, player_names)

        plt.title(**self.params["title_params"])

        plt.xlabel(
            **self.params["xlabel_title_params"],
        )
        plt.ylabel(
            **self.params["ylabel_title_params"],
        )
        plt.show()

        return heatmap_data

    def _prepare_data(self, df, team, num_games, stat):
        """
        Prepare the data for the heatmap.
        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame containing the game stats.
        team : str
            The team code to filter the data.
        num_games : int
            The number of games to consider.
        stat : str
            The stat to plot.
        Returns
        -------
        heatmap_data : pd.DataFrame
            The DataFrame containing the heatmap data.
        """

        columns = self.params["columns"]

        if team:
            df = df[df[columns["team"]] == team]

        df = df[~df[columns["player"]].isin([columns["team"], "Total"])]

        # Assign unique game numbers based on GAME_CODE
        df["game_num"] = pd.factorize(df[columns["game_code"]])[0] + 1

        # Create a unique identifier for each player vs team vs game combination (because games change)
        df["unique_game"] = df.apply(
            lambda row: f"{row[columns['vs_team']]}_{row['game_num']}", axis=1
        )

        # Check for duplicates in the unique_game column
        duplicate_counts = df.duplicated(subset=["unique_game"]).sum()
        print(f"Number of duplicate unique_game entries: {duplicate_counts}")

        # Filter by number of games if specified
        if num_games:
            df = df[df["game_num"] <= num_games]

        df = df.sort_values(by="game_num")

        # Pivot the DataFrame to get players vs unique game heatmap
        heatmap_data = df.pivot(
            index=columns["player"], columns="unique_game", values=stat
        )

        # Sort columns by game number
        sorted_columns = sorted(
            heatmap_data.columns, key=lambda x: int(x.split("_")[-1])
        )
        heatmap_data = heatmap_data[sorted_columns]

        return heatmap_data

    def _normalize_data(self, heatmap_data):
        """
        Normalize the stat data for the circle mode.
        Parameters
        ----------
        heatmap_data : pd.DataFrame
            The DataFrame containing the heatmap data.
        Returns
        -------
        R : np.ndarray
            Normalized radius values.
        c : np.ndarray
            Flattened array of the heatmap data.
        """

        s = heatmap_data.to_numpy()
        # nanmax to ignore NaN values
        max_val = np.nanmax(np.abs(s))
        # normalize the radius of the circles
        R = s / max_val / 2
        # from multidimensional to 1D array
        c = s.flatten()

        return R, c

    def _plot_circles(self, ax, heatmap_data):
        """
        Plot the heatmap using circles.
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes to plot the circles.
        heatmap_data : pd.DataFrame
            The DataFrame containing the heatmap data.
        Returns
        -----
        None
        """

        x, y = np.meshgrid(
            np.arange(len(heatmap_data.columns)), np.arange(len(heatmap_data.index))
        )

        # Normalize the values
        R, c = self._normalize_data(heatmap_data)

        # Create circles
        circles = [
            plt.Circle((j, i), radius=r) for r, j, i in zip(R.flat, x.flat, y.flat)
        ]

        norm = Normalize(vmin=np.nanmin(c), vmax=np.nanmax(c))

        col = PatchCollection(
            circles,
            array=c,
            cmap=self.params["cmap"],
            edgecolor=self.params["linecolor"],
            norm=norm,
        )
        ax.add_collection(col)

        # keep circles symmetrical
        ax.set_aspect("equal", "box")

        # Add grid
        # adding 1 ensures ticks start from the the start of the first column/row
        # subtracting 0.5 centers the ticks between the grid lines

        ax.grid(which="minor")

        if self.params["cbar"]:
            plt.colorbar(col, ax=ax)

        if self.params["annot"]:
            for i in range(len(heatmap_data.index)):
                for j in range(len(heatmap_data.columns)):
                    if not np.isnan(heatmap_data.iloc[i, j]):
                        ax.text(
                            j,
                            i,
                            f"{heatmap_data.iloc[i, j]:.1f}",
                            ha="center",
                            va="center",
                            color="black",
                        )

    def _highlight_players(self, ax, heatmap_data, player_names):
        """
        Highlight the specified players' rows in the heatmap.
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes to plot the heatmap.
        heatmap_data : pd.DataFrame
            The DataFrame containing the heatmap data.
        player_names : list
            The list of player names to highlight.
        Returns
        -------
        None
        """

        for player_name in player_names:
            if player_name in heatmap_data.index:
                player_index = heatmap_data.index.get_loc(player_name)

                # Highlight the player name in the y-axis
                for tick in ax.get_yticklabels():
                    if tick.get_text() == player_name:
                        tick.set_backgroundcolor(
                            self.params["highlight_params"]["backgroundcolor"]
                        )
                        tick.set_weight(self.params["highlight_params"]["fontweight"])
                    # Center the y-tick labels vertically within the row
                    tick.set_verticalalignment("center")

                # Determine the x and y position adjustments based on shape
                x_position = -0.5 if self.params["shape"] == "circle" else 0
                y_position = (
                    player_index - 0.5
                    if self.params["shape"] == "circle"
                    else player_index
                )

                # Draw a rectangle around the selected player's row
                ax.add_patch(
                    plt.Rectangle(
                        (
                            x_position,
                            y_position,
                        ),  # x, y (adjust x and y if shape is 'circle')
                        len(heatmap_data.columns),  # width
                        1,  # height
                        fill=False,
                        edgecolor=self.params["highlight_params"]["edgecolor"],
                        lw=self.params["highlight_params"]["lw"],
                    )
                )
