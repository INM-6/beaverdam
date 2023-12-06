import plotly.graph_objects as go
import plotly.io as pio


def generate_colours():
    """Set colour sequence for plotting data.

    Returns:
        figure_colours (list):  list of colours as hex strings, in the order to use
        them
    """
    figure_colours = [
        "#73adaa",  # blue
        "#dbc172",  # yellow        
        "#a6bc68",  # green
        "#dd8b52",  # orange
        "#cc4f4c",  # red
        "#7f5b47",  # brown
    ]

    return figure_colours


# Define Plotly templates
#
# Plotly templates incorporate layout and data properties:
#   https://plotly.com/python/templates
#   - Layout properties define general aspects of all plots.  You can use them to define
#     things that will be common to all plot types (assuming the property is supported).
#   - Data properties define characteristics of traces added to a figure.  You can use
#     them to define things that will be specific to different plot types (assuming the
#     property is supported).
# Because we want some layout properties to be different between plot types (e.g.
# modebar buttons), we unfortunately need to define one general theme and additional
# specific themes for each plot type with their layout properties.

# General figure properties
pio.templates["main"] = go.layout.Template(
    layout=dict(
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=42, r=42, t=56, b=42),
        colorway=generate_colours(),
        modebar=dict(orientation="v"),
    )
)

# Pie charts
pio.templates["pie"] = go.layout.Template(
    layout=dict(
        margin=dict(l=0, r=0, t=56, b=0),
    )
)

# Bar graphs
pio.templates["bar"] = go.layout.Template(
    layout=dict(
        showlegend=False,
        xaxis=dict(
            linecolor="rgb(1,1,1)",
            linewidth=1,
        ),
        yaxis=dict(
            linecolor="rgb(1,1,1)",
            linewidth=1,
            gridcolor="rgba(1,1,1,0.1)",
            gridwidth=1,
        ),
    )
)

# Box plots
pio.templates["box"] = go.layout.Template(
    layout=dict(
        newselection_mode="gradual",
        dragmode="select",
    )
)

# Scatter plots
#
# Update selection mode to avoid the error:
#   unrecognized GUI edit: selections[0].xref
# Otherwise, after selecting points in a dataframe, there is an error
# (use the inspector in the browser to see the error) on plotly.js
# versions 2.13.2 and 2.13.3.
# https://github.com/plotly/react-plotly.js/issues/290
# Here is a list of plotly versions and which version of plotly.js
# they use:
# https://github.com/plotly/plotly.py/releases
# I got the error in plotly v5.11.0, 5.13.1, 5.9.0, and 5.8.2.
# The error only occurs if the scatterplot data is updated as an output
# after selecting points from the scatterplot, not if the points are updated
# after selecting via checkboxes or pie graphs.
pio.templates["scatter"] = go.layout.Template(
    layout=dict(
        newselection_mode="gradual",
        dragmode="select",
        xaxis=dict(
            rangemode="tozero",
            linecolor="rgb(1,1,1)",
            linewidth=1,
            gridcolor="rgba(1,1,1,0.1)",
            gridwidth=1,
        ),
        yaxis=dict(
            rangemode="tozero",
            linecolor="rgb(1,1,1)",
            linewidth=1,
            gridcolor="rgba(1,1,1,0.1)",
            gridwidth=1,
        ),
    )
)
