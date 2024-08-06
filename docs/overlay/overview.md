# Trajectory Plotter Overview

The `TrajectoryPlotter` class is designed to facilitate the visualization of trajectory data for various subjects, such as players or items. It offers comprehensive customization options through a default configuration that can be easily modified, accessed, and exported. This class supports both static and animated trajectory plots, making it a versatile tool for data visualization.

## How it works


## Configuration and Parameters 

The class comes with a default configuration, which can be updated and accessed at any time.

### Get Configuration 

The get_params method returns the current configuration of the TrajectoryPlotter.

```python
from trajectory_plotter import TrajectoryPlotter

trajectory_plotter = TrajectoryPlotter()

params = trajectory_plotter.get_params()

print(params)
```

### Update Configuration

```python
from trajectory_plotter import TrajectoryPlotter

trajectory_plotter = TrajectoryPlotter()

trajectory_plotter.set_params(marker_size=15, court_line_color="blue")
```
## Custom Config

```python
from trajectory_plotter import TrajectoryPlotter

config = {
    "subject_col": "PLAYER",
    "vlines": {"color": "red", "linestyle": "-"},
    "xlabel_params": {"fontsize": 20, "labelpad": 30},
}

trajectory_plotter = TrajectoryPlotter(config=config)
```

## Exporting Plots 

The class provides functionality to save plots in different formats depending on the plot type (static or animated). 

```python
trajectory_plotter.save_plot(directory="media", file_name="trajectory", file_format="png")
```

For animated plots the supported formats are `gif` and `mp4`: 

```python
trajectory_plotter.save_plot(directory="media", file_name="trajectory", file_format="mp4")
```

## Features


### Scoring Trajectory - Static

![Field Goals Scatter Plot](../media/scoring_profile.png)

### Scoring Trajectory - Animated 

![Field Goals Scatter Plot](../media/scoring_profile.gif)
