import plotly.graph_objects as go
import plotly.io as pio

# Generate and save themes (templates) for Plotly plots.
#
# You can check properties of built-in templates using:
#   pio.templates --> displays a list of the currently available templates
#   from dash_bootstrap_templates import load_figure_template --> gives access to bootstrap templates
#   load_figure_template("template_name") --> loads bootstrap template "template_name"
#   pio.templates["template_name"] --> displays all the properties of "template_name"
#
# Access specific properties using dict notation, e.g.:
#   pio.templates["sandstone"].layout.font


def _generate_colours():
    """Set colour sequence for plotting data.

    Returns:
        figure_colours (list):  list of colours as hex strings, in the order to use
        them
    """
    figure_colours = [
        "#5e82bb",  # blue
        "#d27164",  # red
        "#97b14e",  # green
        "#dfaf20",  # yellow
        "#856451",  # brown
        "#9e79c8",  # purple
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
# If you want layout properties to be different between plot types (e.g.  modebar
# buttons), you need to define additional specific themes for each plot type with their
# layout properties, or set them using myplot.update_layout() after generating myplot.

# General figure properties
pio.templates["main"] = go.layout.Template(
    layout=dict(
        margin=dict(l=42, r=42, t=56, b=42),
        colorway=_generate_colours(),
        piecolorway=_generate_colours(),
        modebar=dict(orientation="v"),  # , bgcolor="rgba(0,0,0,0)"),
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
