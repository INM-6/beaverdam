import plotly.graph_objects as go
import plotly.io as pio

import colours as bd_colours

"""Define themes for Plotly plots, and modebar styles for different plot types"""

# Generate and save themes (templates) for Plotly plots.
#
# Importing this module automatically makes the templates it contains available.
#
# Plotly templates incorporate layout and data properties:
#   https://plotly.com/python/templates
#   - Layout properties define general aspects of all plots.  You can use them to define
#     things that will be common to all plot types (assuming the property is supported).
#   - Data properties define characteristics of traces added to a figure.  You can use
#     them to define things that will be specific to different plot types (assuming the
#     property is supported).
# If you want layout properties to be different between plot types, you need to define
# additional specific themes for each plot type with their layout properties, or set
# them using myplot.update_layout() after generating myplot.
#
# You can check properties of built-in templates using:
#   pio.templates --> displays a list of the currently available templates
#   from dash_bootstrap_templates import load_figure_template --> gives access to bootstrap templates
#   load_figure_template("template_name") --> loads bootstrap template "template_name"
#   pio.templates["template_name"] --> displays all the properties of "template_name"
#
# After importing, you can access specific properties using dict notation, e.g.:
#   pio.templates["sandstone"].layout.font


# General figure properties
pio.templates["main"] = go.layout.Template(
    layout=dict(
        margin=dict(l=42, r=42, t=56, b=42),
        colorway=bd_colours.figure_colourway,
        piecolorway=bd_colours.figure_colourway,
        modebar=dict(orientation="v"),
        font=dict(
            family='Roboto,-apple-system,BlinkMacSystemFont,"Segoe UI","Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol"'
        ),
        xaxis=dict(zerolinewidth=2),
        yaxis=dict(zerolinewidth=2),
    )
)

# Dark mode
pio.templates["main_dark"] = pio.templates["main"]
pio.templates["main_dark"].layout.update(
    {
        "plot_bgcolor": "#212529",
        "paper_bgcolor": "#212529",
        "font_color": "#dfd7ca",
        "xaxis": {
            "gridcolor": "#303336",
            "zerolinecolor": "#3c4044",
        },
        "yaxis": {
            "gridcolor": "#303336",
            "zerolinecolor": "#3c4044",
        },
    }
)


# Light mode
pio.templates["main_light"] = pio.templates["main"]
pio.templates["main_light"].layout.update(
    {
        "plot_bgcolor": "#fff",
        "paper_bgcolor": "#fff",
        "font_color": "#3e3f3a",
        "xaxis": {
            "gridcolor": "#f0f0ef",
            "zerolinecolor": "#e6e6e5",
        },
        "yaxis": {
            "gridcolor": "#f0f0ef",
            "zerolinecolor": "#e6e6e5",
        },
    }
)


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
