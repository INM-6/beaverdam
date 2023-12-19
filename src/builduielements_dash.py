"""Functions to build elements of a Dash user interface"""

from dash import dcc, dash_table, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_trich_components as dtc  # alternative for carousel: dash_slick
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import theme_plots
import uuid


def set_ui_object_id(element_type, id=[]):
    """Set the id field of a Dash UI object so that it works with pattern-matching callbacks

    Args:
        element_type (str):  the type of object
        id (str):  unique identifier for the object (optional; will be auto-generated if omitted)

    Returns:
        ui_id (dict):  keys "index" and "type".  Compatible with Dash pattern-matching
        callbacks which select UI elements based on type.
    """

    # Set defaults
    ui_id = {"index": str(uuid.uuid4()), "type": "undefined"}

    # Set ID of object
    if len(id) > 0:
        ui_id["index"] = id
    # Set object type
    ui_id["type"] = element_type

    return ui_id


def df_to_dict(df):
    """Convert dataframe to the data format that Dash wants for a DataTable

    Args:
        df (dict): data to be shown in DataTable
    """
    return df.to_dict("records")


def unlist_element(x):
    """Check whether an element is a list, and if so convert it to not a list

    Args:
        x (undefined): element to unlist if it's a list

    Returns:
        new_value (undefined):  element that isn't a list
    """
    if isinstance(x, list):
        if len(x) < 1:
            # Empty lists become nothing
            new_value = None
        else:
            # Take the first element from a list
            new_value = x[0]
    else:
        # If the element isn't a list, leave it as is
        new_value = x
    return new_value


def display_as_card(card_body, card_margin="0vmin"):
    """Wrap a UI element in a card

    Args:
        card_body (Dash or html element | list of Dash or html elements): the contents
        of the card
        card_margin (str):  value of the html margin property to use fo the card
        (default: "0vmin")

    Returns:
        dbc.Card (dbc.Card):  Dash Bootstrap Components card
    """
    card_body = [card_body] if not isinstance(card_body, list) else card_body
    return dbc.Card([dbc.CardBody(children=card_body)], style={"margin": card_margin})


def build_data_table(data, id=[], element_type=""):
    """Build Dash data table

    Args:
        data (dataframe): data for the table, with column names the same as the headers
        for the table
        id (str):  unique ID for the Dash element (optional; will be auto-generated if
        omitted)
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)

    Returns:
        dash_table.DataTable: Dash DataTable
    """
    return dash_table.DataTable(
        id=set_ui_object_id(id=id, element_type=element_type),
        data=df_to_dict(data),
        style_table={"overflowX": "scroll"},
        style_cell={"textAlign": "left"},
    )


def get_data_table_contents(datatable_object):
    """Get only the contents of the data table, in the format Dash likes

    Args:
        datatable_object (DataTablePresenter from Presenter module): formatted data for
        the table

    Returns:
        (dict):  data to be shown in DataTable
    """
    return df_to_dict(datatable_object.contents["df"])


def build_data_table_label(
    current_num_records, initial_num_records, id=[], element_type=""
):
    """Generate text specifying number of selected and total records

    Args:
        current_num_records (int): number of records currently selected
        initial_num_records (int): number of total records possible to select
        id (str):  unique ID for the Dash element (optional; will be auto-generated if
        omitted)
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)

    Returns:
        dbc.Stack: text in a Dash Bootstrap Components stack, with the current number of
        selected records having the provided ID
    """
    return dbc.Stack(
        [
            html.Div(
                style={"white-space": "pre-wrap"},
                children=str(current_num_records),
                id=set_ui_object_id(id=id, element_type=element_type),
            ),
            html.Div(
                style={"white-space": "pre-wrap"},
                children=[
                    " of " + str(initial_num_records),
                ],
            ),
            html.Div(
                style={"white-space": "pre-wrap"},
                children=[" sessions meet your criteria"],
            ),
        ],
        direction="horizontal",
    )


def build_filter_checklist(items, title=[], id=[], element_type=""):
    """Build Dash checklist

    Args:
        items (list):  options for the checklist
        title (str):  title for the checklist
        id (str):  unique identifier
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)

    Returns:
        filter_checklist (dbc.Card): Dash Bootstrap Components card containing the checklist title and options
    """
    filter_checklist = display_as_card(
        [
            html.Div(children=title),
            html.Div(
                children=dcc.Checklist(
                    options=items,
                    value=[],
                    id=set_ui_object_id(id=id, element_type=element_type),
                    labelStyle={"display": "block", "margin-bottom": "0px"},
                )
            ),
        ],
        card_margin="1vmin",
    )
    return filter_checklist


def get_checklist_selection(filterchecklist_object):
    """Get only the selected options of a filter checklist

    Args:
        filterchecklist_object (FilterChecklist from Presenter module): title and
        options for the checklist

    Returns:
        the options from the checklist which are selected
    """
    return filterchecklist_object.contents["selected_options"]


def build_button(button_text, button_type="button"):
    """Build Dash button with specified text

    Args:
        button_text (str):  text to display on the button
        button_type (str):  type of UI element (for pattern matching callbacks) (opt)

    Returns:
        html.Div containing button
    """
    return html.Div(
        children=[
            dbc.Button(
                button_text,
                id=set_ui_object_id(element_type=button_type),
                n_clicks=0,
                size="sm",
            ),
        ]
    )


def build_data_figure(graph_object, id=[], element_type="", config={}):
    """Build a Dash data figure containing a graph and with appropriate Dash identifiers

    Args:
        graph_object (Plotly Express object containing a graph):  the plot
        id (str):  unique identifier for the figure (optional; will be auto-generated if
        not provided)
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)
        config (dict):  configuration options for Plotly figures (optional)

    Returns:
        dash_graph (dbc.Card): Dash Bootstrap Components card containing the graph
    """
    # Plotly themes have been imported when importing theme_plots.py
    # Set default theme
    pio.templates.default = "main"
    # Create plot
    dash_graph = display_as_card(
        dcc.Graph(
            id=set_ui_object_id(id=id, element_type=element_type),
            figure=graph_object,
            config=config,
        ),
        card_margin="6px",
    )
    return dash_graph


def build_pie_chart(data, title=[]):
    """Build a pie chart to include in a Dash figure
    Args:
        data (df with one column):  data to be plotted
        title (str):  title of the graph (optional; default is no title)

    Returns:
        pie_chart (px.pie): Plotly Express object containing the graph
    """
    pie_chart = px.pie(
        data_frame=data.map(unlist_element),
        names=data.iloc[:, 0].tolist(),
        title=title,
    )
    pie_chart.update_layout(template="main+pie")
    return pie_chart


def build_bar_graph(data, title=[]):
    """Build a bar graph to include in a Dash figure
    Args:
        data (df with one column):  data to be plotted
        title (str):  title of the graph (optional; default is no title)

    Returns:
        bar_graph (px.histogram): Plotly Express object containing the graph
    """
    bar_graph = px.histogram(
        data_frame=data.map(unlist_element),
        x=data.columns,
        title=title,
    )
    bar_graph.update_layout(template="main+bar")
    return bar_graph


def build_box_plot(data, title=[]):
    box_plot = px.box(
        data_frame=data.map(unlist_element),
        x=data.columns[1],
        y=data.columns[0],
        hover_name=data.index,
        title=title,
    )
    box_plot.update_layout(template="main+box")
    return box_plot


def build_scatter_plot(data, title=[]):
    """Build a scatter plot to include in a Dash figure
    Args:
        data (df with two columns):  data to be plotted
        title (str):  title of the graph (optional; default is no title)

    Returns:
        scatter_plot (px.scatter): Plotly Express object containing the graph
    """
    scatter_plot = px.scatter(
        data_frame=data.map(unlist_element),
        x=data.columns[0],
        y=data.columns[1],
        hover_name=data.index,
        title=title,
    )
    scatter_plot.update_layout(template="main+scatter")
    return scatter_plot


def build_carousel(
    figures, n_figs=1, n_scroll=1, margin_bottom="5%", margin_side="2.5%"
):
    """Arrange figures in a carousel

    Args:
        figures (list): figures to show, as some sort of Dash UI element
        n_figs (int, optional): how many figures to show at once. Defaults to 1.
        n_scroll (int, optional): how many figures to scroll when the scroll button is clicked. Defaults to 1.
        margin_bottom (str, optional): bottom margin, with units. Defaults to 5%.
        margin_side (str, optional): side margin, with units. Defaults to 2.5%.

    Returns:
        carousel (dtc.Carousel):  carousel containing the figures
    """
    carousel = dtc.Carousel(
        figures,
        id="FigureGallery",
        dots=True,
        arrows=True,
        infinite=True,
        speed=500,
        slides_to_show=n_figs,
        slides_to_scroll=n_scroll,
        style={
            "margin-bottom": margin_bottom,
            "margin-left": margin_side,
            "margin-right": margin_side,
        },
    )
    return carousel


def build_chips(chip_items):
    """Build chips from a list of items

    Args:
        chip_items (list): each item in the list will be one chip

    Returns:
        chips (list):  all chips, in a list
    """
    chips = [
        dmc.Chip(
            [html.I(className="fa fa-solid fa-circle-xmark"), " ", x],
            value=x,
            size="s",
            radius="lg",
            checked=False,
        )
        for x in chip_items
    ]
    return chips


def build_chip_group(items, title=[], id=[], element_type=""):
    """Build chipgroup from chips and display in card

    Args:
        items (list): each item in the list will be one chip
        title (str):  title for the chipgroup
        id (str):  unique identifier
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)

    Returns:
        chip_group (dbc.Card): Dash Bootstrap Components card containing the chips and title
    """
    chip_group = display_as_card(
        [
            html.Div(children=title),
            html.Div(
                children=dmc.ChipGroup(
                    build_chips(items),
                    id={"index": id, "type": element_type},
                    position="left",
                    spacing=8,
                )
            ),
        ],
        card_margin="1vmin",
    )
    return chip_group
