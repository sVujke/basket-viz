🏀 basket-viz
==============================

A Python library for creating interactive and customizable visualizations of basketball statistics.

![PyPI Version](https://img.shields.io/pypi/v/basket-viz)
![Python Version](https://img.shields.io/pypi/pyversions/basket-viz)
![License](https://img.shields.io/github/license/sVujke/basket-viz)
![Issues](https://img.shields.io/github/issues/sVujke/basket-viz)
![Last Commit](https://img.shields.io/github/last-commit/sVujke/basket-viz)
![Downloads](https://img.shields.io/pypi/dm/basket-viz)

## ♻️  Installation

To install basket-viz, simply run:

```bash
pip install basket-viz
```

# ⛹️‍♂️Getting Started 

## 🎯 Shot Charts 

```python
from basket_viz.court.shot_charts import ShotChart

shot_chart = ShotChart()
shot_chart.plot_shot_chart(df, player_name="NEDOVIC, NEMANJA")
```

![Alt Text](/media/shots.gif)

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
