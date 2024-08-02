

## Animated Field Goal Scatter

The `plot_field_goal_scatter_temporal` function creates a scatter plot of made and missed shots.

### Parameters
- `made` (DataFrame): DataFrame containing made shots.
- `miss` (DataFrame): DataFrame containing missed shots.
- `title` (str, optional): Title of the plot.

## Examples

### Basic Scatter Shot Chart

```python
from basket_viz.court.shot_charts import ShotChart  

made_shots = pd.DataFrame({
    "COORD_X": [100, -150, 300, 450, -500, 600],
    "COORD_Y": [50, 75, 200, 250, 350, 500],
    "UTC": list(range(1, 7))
})

# Missed shots
missed_shots = pd.DataFrame({
    "COORD_X": [200, -250, -400, 550, 600, -700],
    "COORD_Y": [100, 450, 300, 350, 450, 500],
    "UTC": list(range(1, 7))
})

shot_chart = ShotChart()
shot_chart.plot_field_goal_scatter_temporal(made_shots, missed_shots, title="Field Goals Scatter Plot")
```

![Field Goals Scatter Plot](../media/basic_shot_chart_animated.gif)

### Customized Scatter Shot Chart

```python
from basket_viz.court.shot_charts import ShotChart  

shot_chart = ShotChart()

# set figure size 
shot_chart.set_config_param(figsize=(14,12))

# change marker colors
shot_chart.set_config_param(color_map={"made": "purple", "miss": "black"})

# change court colors 
shot_chart.set_config_param(court_background_color="gray", court_line_color="white")

#change title 
shot_chart.set_config_param(title={"fontsize": 30, "fontweight": "bold", "color": "white"})

shot_chart.plot_field_goal_scatter(made_shots, missed_shots, title="Field Goals Scatter Plot")
```

![Field Goals Scatter Plot](../media/basic_shot_chart_animated_customized.gif)

