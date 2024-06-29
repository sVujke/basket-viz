team_configs = {
    "RED": {
        "color_map": {
            "made": "white",
            "miss": "black",
        },  # Red shades for made and missed shots
        "marker_size": 9,
        "marker_style": {"made": "o", "miss": "x"},
        "figsize": (12, 10),
        "court_line_color": "white",
        "line_width": 2,
        "outer_lines": True,
        "court_background_color": "red",
        "plot_shots": "all",  # Options: 'all', 'made', 'miss'
        "coord_x": "COORD_X",
        "coord_y": "COORD_Y",
        "sort_col": "UTC",
        "animation_interval": 100,
        "animation_repeat_delay": 1000,
        "animation_blit": True,
    }
}
