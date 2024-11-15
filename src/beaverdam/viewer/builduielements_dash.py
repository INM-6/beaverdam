"""Functions to build elements of a Dash user interface."""

import uuid

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_trich_components as dtc  # alternative for carousel: dash_slick
import plotly.express as px
from dash import dash_table, dcc, html

from beaverdam.viewer.plotly_modebarlayout import modebar_layout

# Custom plot themes (themes are loaded immediately when imported)
from . import (
    plotly_theme,  # noqa: F401
)


def set_ui_object_id(element_type, id=[]):
    """Set the id field of a Dash UI object so that it works with pattern-matching callbacks.

    Args:
        element_type (str):  the type of object
        id (str):  unique identifier for the object (optional; will be auto-generated if
        omitted)

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
    """Convert dataframe to the data format that Dash wants for a DataTable.

    Args:
        df (dict): data to be shown in DataTable

    """
    return df.to_dict("records")


def unlist_element(x):
    """Check whether an element is a list, and if so convert it to not a list.

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


def value_to_label(x):
    """Make sure that a value is formatted appropriately to display in UI components.

    Most UI components can display strings and numbers, but not e.g. booleans.  So
    things like booleans need to be converted to strings.

    If a value is None, it's a design choice whether to show it or not.  Currently, if a
    value doesn't exist in the database, it is stored internally in the dataframe as
    None.  It might be confusing to show a None, for example in a filter checklist,
    because it implies that None was a value assigned to a piece of metadata.
    Conversely, it might be useful to show None, because then users can see how many
    undefined values there are (as long as they know that None means undefined).  Here,
    I've chosen not to show None values (by leaving them as None), because they
    currently aren't shown in plots.

    Args:
        x (a single item of undetermined type): value to format as labels

    Returns:
        formatted_x (string or numeric or None, depending on the input):  formatted
        label

    """
    # Labels must be strings or numbers.  In Python, numbers can be int, float,
    # or complex.  But we have to check for bool first, because for historic
    # reasons bool is a subclass of int so if you check for int first it'll
    # return true even if item is bool.
    if isinstance(x, bool):
        if x:
            formatted_x = "True"
        else:
            formatted_x = "False"
    elif isinstance(x, (str, int, float)):
        formatted_x = x
    elif x is None:
        # To show None values, just get rid of this elif statement and they'll get
        # converted to strings in the else part.
        formatted_x = x
    else:
        formatted_x = str(x)
    return formatted_x


def display_as_card(card_body, card_margin="0vmin"):
    """Wrap a UI element in a card.

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
    """Build Dash data table.

    Args:
        data (dataframe): data for the table, with column names the same as the headers
        for the table
        id (str):  unique ID for the Dash element (optional; will be auto-generated if
        omitted)
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)

    Returns:
        (html.Div): containing Dash Bootstrap table.  The table needs to be inside a div
        in order to update the contents.

    """
    return html.Div(
        id=set_ui_object_id(element_type=element_type, id=id),
        children=build_data_table_contents(data),
        className="dbc",
    )


def build_data_table_contents(data):
    """Build the contents of a new data table.

    Args:
        data (dataframe): data for the table, with column names the same as the headers
        for the table

    Returns:
        (DataTable):  Dash DataTable containing data

    """
    return dash_table.DataTable(
        data=data.to_dict("records"),
        page_size=500,
        cell_selectable=False,
        style_table={"overflowX": "scroll"},
    )


def build_data_table_label(
    current_num_records, initial_num_records, id=[], element_type=""
):
    """Generate text specifying number of selected and total records.

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
                children=[" records meet your criteria"],
            ),
        ],
        direction="horizontal",
    )


def build_filter_checklist(items, title=[], id=[], element_type=""):
    """Build Dash checklist.

    Args:
        items (list):  options for the checklist
        title (str):  title for the checklist
        id (str):  unique identifier
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)

    Returns:
        filter_checklist (dbc.Card): Dash Bootstrap Components card containing the checklist title and options

    """
    # Find checklist options
    values = [unlist_element(x) for x in items]
    options = []
    for idx, item in enumerate(values):
        if item is None:
            # TODO:  decide if it makes sense to show None (i.e. missing) values in
            # checklists, or not.  Currently they aren't shown in plots, so it seems
            # weird to show them in checklists.
            pass
        else:
            options.append({"label": value_to_label(item), "value": values[idx]})
    filter_checklist = display_as_card(
        [
            html.Div(children=title),
            html.Div(
                children=dbc.Checklist(
                    options=options,
                    value=[],
                    id=set_ui_object_id(id=id, element_type=element_type),
                    labelStyle={"display": "block", "margin-bottom": "0px"},
                )
            ),
        ],
        card_margin="1vmin",
    )
    return filter_checklist


def build_button(button_text, button_type="button"):
    """Build Dash button with specified text.

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


def build_data_figure(graph_object, id=[], element_type=""):
    """Build Dash data figure containing a graph and with appropriate Dash identifiers.

    Args:
        graph_object (Plotly Express object containing a graph):  the plot
        id (str):  unique identifier for the figure (optional; will be auto-generated if
        not provided)
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)

    Returns:
        dash_graph (dbc.Card): Dash Bootstrap Components card containing the graph

    """
    # Create plot
    dash_graph = display_as_card(
        dcc.Graph(
            id=set_ui_object_id(id=id, element_type=element_type),
            figure=graph_object,
            config=modebar_layout(graph_object.data[0].type),
        ),
        card_margin="6px",
    )
    return dash_graph


def build_plot(data, title=[], style=""):
    """Build a plot to include in a Dash figure.

    Args:
        data (df):  data to be plotted.  Number of columns depends on the plot type.
        title (str):  title of the graph (optional; default is no title)
        style (str):  type of plot:  "pie", "bar", "box", "scatter"

    Returns:
        final_plot (px plot object): Plotly Express object containing the plot.  The
        exact type of object depends on the plot type.

    """
    if style == "pie":
        final_plot = build_pie_chart(data, title)
    elif style == "bar":
        final_plot = build_bar_graph(data, title)
    elif style == "box":
        final_plot = build_box_plot(data, title)
    elif style == "scatter":
        final_plot = build_scatter_plot(data, title)
    else:
        pass
    return final_plot


def build_pie_chart(data, title=[]):
    """Build a pie chart to include in a Dash figure.

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
    return pie_chart


def build_bar_graph(data, title=[]):
    """Build a bar graph to include in a Dash figure.

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
    bar_graph.update_layout(
        showlegend=False,
    )
    return bar_graph


def build_box_plot(data, title=[]):
    """Build a box plot to include in a Dash figure.

    Args:
        data (df with two columns):  data to be plotted
        title (str):  title of the graph (optional; default is no title).

    Returns:
        scatter_plot (px.scatter): Plotly Express object containing the graph

    """
    box_plot = px.box(
        data_frame=data.map(unlist_element),
        x=data.columns[1],
        y=data.columns[0],
        hover_name=data.index,
        title=title,
    )
    box_plot.update_layout(
        newselection_mode="gradual",
        dragmode="select",
    )
    return box_plot


def build_scatter_plot(data, title=[]):
    """Build a scatter plot to include in a Dash figure.

    Args:
        data (df with two columns):  data to be plotted
        title (str):  title of the graph (optional; default is no title)

    Returns:
        scatter_plot (px.scatter): Plotly Express object containing the graph

    """
    scatter_plot = px.scatter(
        data_frame=data.map(unlist_element),
        x=data.columns[1],
        y=data.columns[0],
        hover_name=data.index,
        title=title,
    )
    scatter_plot.update_layout(
        newselection_mode="gradual",
        dragmode="select",
        xaxis=dict(
            rangemode="tozero",
        ),
        yaxis=dict(
            rangemode="tozero",
        ),
    )
    return scatter_plot


def build_carousel(
    figures, n_figs=1, n_scroll=1, margin_bottom="5%", margin_side="2.5%"
):
    """Arrange figures in a carousel.

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


def encode_criterion_info(criterion_name, criterion_value):
    """Encode information about a criterion value into a string.

    The resulting string can be decoded to uniquely recover the value and its associated
    criterion.

    Args:
    criterion_name (str):  name of criterion
    criterion_value (anything):  value of criterion

    Returns:
    criterion_info (string):  encodes the value, its type, and its associated criterion

    """
    criterion_info = (
        "CRITERION="
        + criterion_name
        + "__VALUE="
        + str(value_to_label(criterion_value))
        + "__TYPE="
        + type(criterion_value).__name__
    )
    return criterion_info


def decode_criterion_info(criterion_info):
    """Extract information about a criterion value from an encoded string.

    Args:
    criterion_info (string):  encodes the value, its type, and its associated criterion

    Returns:
    criterion_name (str):  name of criterion
    criterion_value (anything):  value of criterion

    """
    string_components = criterion_info.split("__")

    def get_value(key_name):
        """Get the value associated with a key from encoded criterion info.

        Args:
            key_name (str): name of the key

        Returns:
            str: value associated with the key

        """
        inds = [ind for ind, s in enumerate(string_components) if key_name in s]
        return string_components[inds[0]].split(key_name + "=")[1]

    criterion_name = get_value("CRITERION")
    criterion_str_value = get_value("VALUE")
    criterion_type = get_value("TYPE")
    # Convert the criterion's value to its actual value, e.g. str, int, bool
    if criterion_type == "str":
        criterion_value = criterion_str_value
    elif criterion_type == "int":
        criterion_value = int(criterion_str_value)
    elif criterion_type == "float":
        criterion_value = float(criterion_str_value)
    elif criterion_type == "bool":
        # Bool values are more complicated to convert
        if criterion_str_value.lower() == "true":
            criterion_value = True
        elif criterion_str_value.lower() == "false":
            criterion_value = False
        else:
            raise ValueError("Undefined bool value")
    else:
        raise ValueError(
            "Beaverdam doesn't know how to decode {0} yet.".format(criterion_type)
        )
    return criterion_name, criterion_value


def build_chips(chip_items, item_info=[]):
    """Build chips from a list of items.

    Args:
        chip_items (list): each item in the list will be the text shown on one chip
        item_info (list): each item in the list will be used as the value of the
        corresponding chip.  Must have the same length as chip_items, and consist only
        of strings.  Optional; defaults to None.

    Returns:
        chips (list):  all chips, in a list

    """
    # Check that hidden_info is the same size as chip_items, and if not set it to an
    # empty list of the correct size
    if len(item_info) != len(chip_items):
        item_info = [None for _ in chip_items]
    chips = [
        dmc.Chip(
            [html.I(className="fa fa-solid fa-circle-xmark"), " ", value_to_label(x)],
            size="s",
            radius="lg",
            checked=True,
            value=item_info[ind],
        )
        for ind, x in enumerate(chip_items)
    ]
    return chips


def build_chip_group(items, item_info=[], title="", id="", element_type=""):
    """Build chipgroup from chips and display in card.

    Args:
        items (list): each item in the list will be one chip
        item_info (list): each item in the list will be the value of the corresponding
        chip.  Must have the same length as chip_items and contain only strings.
        Optional; defaults to None.
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
                    build_chips(items, item_info),
                    id={"index": id, "type": element_type},
                    position="left",
                    spacing=8,
                )
            ),
        ],
        card_margin="1vmin",
    )
    return chip_group
