# Shot Charts Overview

The primary purpose of the `ShotChart` object is to facilitate the creation of uniform and visually appealing field goal attempt plots for various players or teams. It includes a default configuration that can be easily modified, accessed, and exported to meet specific visualization needs.

In addition, the `ShotChart` class offers a comprehensive API for generating both static and animated plots. It also provides specialized wrappers for specific leagues, such as the Euroleague, and includes a collection of configurations that customize the plots according to team colors and branding.

## How it works

todo add diagram here 


## Configuration and Parameters

The `ShotChart` class has a default config, enabling a quick start

```python
from basket_viz.court.shot_charts import ShotChart  

shot_chart = ShotChart()
```

### Get and set config params

You can check the config parameters at any time, since it is mutable

```python
shot_chart.get_config()
```

and if for customization purposes update them with 

```python
shot_chart.set_config_param(figsize=(14,12))
```
The `ShotChart` class can be initialized with a configuration dictionary. Here is an example:

```python
custom_config = {
    "color_map": {"made": "blue", "miss": "red"},
    "marker_size": 15,
    "figsize": (12, 10),
    "court_line_color": "grey",
    "line_width": 2,
    "outer_lines": False,
    "court_background_color": "lightgrey"
}

shot_chart = ShotChart(config=custom_config)
```


## Exporting Plots 

The class provides functionality to save plots in different formats depending on the plot type (static or animated). 


```python

shot_chart = ShotChart()

shot_chart.plot_field_goal_scatter(made, missed)

shot_chart.save_plot(output_dir, file_name, 'png')
```

For animated plots the supported formats are gif and mp4: 

```python

shot_chart = ShotChart()

shot_chart.plot_field_goal_scatter_temporal(made, missed)

shot_chart.save_plot(output_dir, file_name, 'gif')
```
## Features

## Static Scatter
## Animated Scatter 
## Heatmap