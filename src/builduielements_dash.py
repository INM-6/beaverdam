"""Functions to build elements of a Dash user interface"""

from dash import dcc, dash_table, html
import dash_bootstrap_components as dbc
import plotly.express as px
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
                    labelStyle={"display": "block"},
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
            html.Button(
                button_text, id=set_ui_object_id(element_type=button_type), n_clicks=0
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
        data_frame=data,
        names=data.iloc[:, 0].tolist(),
        title=title,
    )
    pie_chart.update_layout(
        margin=dict(l=0, r=0, t=56, b=0),
        modebar=dict(orientation="v"),
    )
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
        data_frame=data,
        x=data.columns,
        title=title,
    )
    bar_graph.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=56, b=0),
        modebar=dict(orientation="v"),
    )
    return bar_graph


def build_scatter_plot(data, title=[]):
    """Build a scatter plot to include in a Dash figure
    Args:
        data (df with two columns):  data to be plotted
        title (str):  title of the graph (optional; default is no title)

    Returns:
        scatter_plot (px.scatter): Plotly Express object containing the graph
    """
    scatter_plot = px.scatter(
        data_frame=data,
        x=data.columns[0],
        y=data.columns[1],
        hover_name=data.index,
        title=title,
    )

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
    scatter_plot.update_layout(
        newselection_mode="gradual",
        dragmode="select",
        margin=dict(l=0, r=0, t=56, b=0),
        modebar=dict(orientation="v"),
    )

    return scatter_plot
