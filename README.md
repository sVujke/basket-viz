🏀 basket-viz
==============================

A Python library for creating interactive and customizable visualizations of basketball statistics.

![PyPI Version](https://img.shields.io/pypi/v/basket-viz)
![Python Version](https://img.shields.io/pypi/pyversions/basket-viz)
![License](https://img.shields.io/github/license/sVujke/basket-viz)
![Issues](https://img.shields.io/github/issues/sVujke/basket-viz)
![Last Commit](https://img.shields.io/github/last-commit/sVujke/basket-viz)
![Downloads](https://img.shields.io/pypi/dm/basket-viz)

## ♻️  Install from PyPI

To install basket-viz, simply run:

```bash
pip install basket-viz
```

# ⛹️‍♂️Getting Started 

## 🔍 Docs

For a comprehensive overview of features check out the [documentation](https://svujke.github.io/basket-viz).

## 🎯 Shot Charts 

```python
from basket_viz.court.shot_charts import ShotChart

shot_chart = ShotChart()
shot_chart.plot_shot_chart(df, player_name="NEDOVIC, NEMANJA")
```

![Alt Text](/media/shots.gif)


## ⬡ ⬢ Aggergated Shot Charts

```python
df_all = shot_chart.get_all_entity_hexbin_data(df)

shot_chart.plot_entity_hexbin_sized(
    df_all,
    offsets_col='offsets',
    color_col='values_ratio',
    size_col='values_all',
    entity_name=player_name,
)
```

![Alt Text](/media/sized_hexbin_shotchart.png)

## 🔊 Radar Charts

The radar charts are the first kind that has layers. First layer being the chart, second being the image layer. 

### Standard Radar

```python

radar_chart = RadarChart(
    dataframe=df_player_stats,
    columns=stats
)

radar_chart.plot_radar(player_name, title_sufix="\n Euroleague 2023/2024")   
radar_chart.add_player_image(img_path)
radar_chart.display_chart()
```

NOTE: The circular image is not mandatory.

![Alt Text](/media/simple-radar.png)

### Comparison Radar 

```python
radar_chart = RadarChart(
    dataframe=df_player_stats,
    columns=stats
)

player_names = ["Howard, Markus", "James, Mike"]
colors = [basconia_blue, monaco_gold]

# Plot the radar comparison
radar_chart.compare_radars(
    player_names=player_names,
    line_colors=colors,
    title="Euroleague 2023/2024 \n SCORRER COMPARISON"
)

# Add player images after plotting the radars
radar_chart.add_comparison_images(start_x=0.2, spacing=0.25, y_offset=-0.2)

# Display the chart
radar_chart.display_chart()
```

NOTE: The circular images are not mandatory.

![Alt Text](/media/comparison-radar.png)

## 🎢 Overlay 
This module supports plotting static and animated overlay comparing the performance of individuals against the rest of the league. 

```python
from basket_viz.overlay.trajectory import PlotTrajectory

pt = PlotTrajectory()

players = ["Hezonja, Mario","James, Mike","Lessort, Mathias"]
colors = [real_madrid_gold, monaco_red, panathenaicos_green]
v_lines = {1.0: 'Short-Range', 4.0: 'Mid-Range', 6.75: 'Three-Point Line'}

pt.plot_trajectory_animated(normalized_df, players, colors, v_lines=v_lines, title=f"Scoring Profiles \n EUROLEAGUE 23/24")
```

![Alt Text](/media/scoring_profile.gif)

## 🔴🟡🟢 Stat Grid 
This module supports plotting stat heatmaps for all players per game.

It also comes with marking capability, to "zoom in" on particular players by highlighting them.

The shape of the values can be square or circle. 

```python
from basket_viz.stat_grid.season_stats import PlayerStatsHeatmap

ps = PlayerStatsHeatmap()


ps.set_params( highlight_params={
                "backgroundcolor": basconia_red,
                "fontweight": "bold",
                "edgecolor": basconia_blue,
                "lw": 3,
            })
ps.plot_stat_heatmap(df_stats, team='BAS', player_bames=['moneke, chima'.upper()], num_games=15, stat=stat)
```

![Alt Text](/media/statgrid-plus-minus.png)

## 📈 Relationships 

This module supports plotting relationships between different stats of players int the team. 

To apply collor template that matches the brand of `Euroleague` teams use `use_team_config=True`. 

```python
from basket_viz.relationships.plotter import PlotRelationship

plotter = PlotRelationship(use_team_config=True,output_format='mp4')
plotter.plot_animated_relationship(
    df,
    team_filter="BAR",
    display_only_last_names=True,
)
```

![Alt Text](/media/BAR_.gif)

# 🙌 Contibuting 

We are continuously working on improving this project and we welcome your contributions!

## 🐞 Open Issues 

If you have any feature requests or bug reports, please don't hesitate to open an issue. This project is a work in progress, and your feedback is invaluable to us.

## 👨‍💻 Pick up Issues

You can also pick up an issue at any time and start working on it. Please make sure to follow our [contribution guidelines](CONTRIBUTING.md) to ensure a smooth collaboration process. Thank you for your support and happy coding!

