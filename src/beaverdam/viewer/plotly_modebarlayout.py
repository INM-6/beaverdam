def modebar_layout(plot_type):
    """Define modebar layout for different plot types

    Use these as config options when creating a dcc.Graph object containing a plot.

    I didn't find any way to put these into a layout.

    A list of Plotly modebar buttons is here:
    https://plotly.com/python/configuration-options/#removing-modebar-buttons
    Make sure that you give the list of modebar buttons as [[ buttonNames ]]

    Args:
        plot_type (str): type of plot:  "pie", "bar", "box", "scatter"

    Returns:
        modebar_layout (dict): orientation, buttons, and options for the modebar
    """

    # Define general modebar properties
    modebar_base = {
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtons": [["toImage"]],
    }

    # Define modebar properties specific to each plot type
    #
    # Note that if you redefine a key in a plot-specific dict of config options, it will
    # override the values in the corresponding key of the base options, so if you want to
    # add on to base options you have to include the base value in the plot-specific value
    # alongside the additional options.
    if plot_type == "pie":
        modebar_layout = modebar_base
    elif plot_type == "bar":
        modebar_layout = modebar_base
    elif plot_type == "box":
        modebar_layout = {
            **modebar_base,
            "modeBarButtons": [
                modebar_base["modeBarButtons"][0]
                + [
                    "select2d",
                    "lasso2d",
                ]
            ],
        }
    elif plot_type == "scatter":
        modebar_layout = {
            **modebar_base,
            "modeBarButtons": [
                modebar_base["modeBarButtons"][0]
                + [
                    "zoom2d",
                    "pan2d",
                    "select2d",
                    "lasso2d",
                ]
            ],
        }
    else:
        modebar_layout = modebar_base

    return modebar_layout
