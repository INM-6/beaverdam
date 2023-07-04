"""Functions to build elements of a Dash user interface"""

from dash import dcc, dash_table, html
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


def build_filter_checklist(items, title=[], id=[], element_type=""):
    """Build Dash checklist

    Args:
        items (list):  options for the checklist
        title (str):  title for the checklist
        id (str):  unique identifier
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)

    Returns:
        html.Div: contains checklist title and options
    """
    return html.Div(
        children=[
            html.Div(children=title),
            html.Div(
                children=dcc.Checklist(
                    options=items,
                    value=[],
                    id=set_ui_object_id(id=id, element_type=element_type),
                    labelStyle={"display": "block"},
                )
            ),
        ]
    )


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


def build_data_figure(graph_object, id=[], element_type=""):
    """Build a Dash data figure containing a graph and with appropriate Dash identifiers

    Args:
        graph_object (Plotly Express object containing a graph):  the plot
        id (str):  unique identifier for the figure (optional; will be auto-generated if
        not provided)
        element_type (str):  type of object, for use with pattern-matching callbacks
        (opt)

    Returns:
        dash_graph (dcc.Graph): Dash object containing the graph
    """
    dash_graph = dcc.Graph(
        id=set_ui_object_id(id=id, element_type=element_type),
        figure=graph_object,
    )

    # If you build a scatter plot, update selection mode to avoid the error:
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
    # try:
    #     plot_type = graph_object.data[0]["type"]
    #     if plot_type=="scatter":
    #         dash_graph.figure.update_layout(
    #             newselection_mode="gradual",
    #         )
    # except:
    #     pass

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
    )

    return scatter_plot


# def build_graph(style, data, title=[], id=[], element_type=""):
#     """Build a Dash graph

#     Args:
#         style (str): type of graph -- this will end up being the type that elements are
#         selected on in pattern matching callbacks.
#         data (df or list, depending on graph style):  data to be plotted
#         title (str):  title of the graph (optional; default is no title)
#         id (str):  unique identifier for the graph (optional; will be auto-generated if
#         not provided)
#         element_type (str):  type of object, for use with pattern-matching callbacks
#         (opt)

#     Returns:
#         dash_graph (dcc.Graph): Dash object containing the graph
#     """

#     dash_graph = dcc.Graph(
#             id=set_ui_object_id(id=id, element_type=element_type),
#             figure=build_figure(graph_object),
#         )

#     if style == "ScatterPlot":
#         # Update selection mode to avoid the error:
#         #   unrecognized GUI edit: selections[0].xref
#         # Otherwise, after selecting points in a dataframe, there is an error
#         # (use the inspector in the browser to see the error) on plotly.js
#         # versions 2.13.2 and 2.13.3.
#         # https://github.com/plotly/react-plotly.js/issues/290
#         # Here is a list of plotly versions and which version of plotly.js
#         # they use:
#         # https://github.com/plotly/plotly.py/releases
#         # I got the error in plotly v5.11.0, 5.13.1, 5.9.0, and 5.8.2.
#         # The error only occurs if the scatterplot data is updated as an output
#         # after selecting points from the scatterplot, not if the points are updated
#         # after selecting via checkboxes or pie graphs.
#         dash_graph.figure.update_layout(
#             newselection_mode="gradual",
#         )

#     return dash_graph

# def build_figure(graph_object):
#     """Build only the figure part of a Dash graph

#     Args:
#         graph_object (DataFigure): title, type, and options for the graph. Must specify
#         the type of graph in the field DataFigure.graph_type -- currently supported
#         values are "pie", "bar", "scatter".

#     Returns:
#         dash_figure (dcc.Graph.figure): Dash object containing the figure part of
#         a Graph object
#     """

#     graph_type = graph_object.graph_type
#     graph_data = graph_object.df
#     graph_title = graph_object.title

#     dash_figure = []

#     # NOTE:  in Python 3.10 and up, use match / case instead.  Unfortunately as 3.10
#     # isn't supported on Ubuntu 20.04 I am stuck with 3.9 for now.
#     # match graph_object.graph_type:
#     #     case "pie":
#     #     case "bar":
#     #     case "scatter":
#     #     case _:
#             # Graph type not defined
#     if graph_type == "pie":
#        dash_figure = px.pie(
#                 data_frame=graph_data,
#                 names=list(graph_object.df.columns.values)[0],
#                 title=graph_title,
#             )
#     elif graph_type == "bar":
#         dash_figure = px.histogram(
#                 data_frame=graph_data,
#                 x=graph_object.field,
#                 title=graph_title,
#             )
#     elif graph_type == "scatter":
#         dash_figure = px.scatter(
#                 data_frame=graph_data,
#                 x=graph_object.field[1],
#                 y=graph_object.field[0],
#                 title=graph_title,
#             )
#     else:
#         # Graph type not defined
#         pass

#     return dash_figure


# def build_pie_chart(element_type, data, title=[], id=[]):
#     """Build Dash pie chart

#     Args:
#         element_type (str): type of graph -- this will end up being the type that elements are
#         selected on in pattern matching callbacks.
#         data (df):  data to be plotted
#         title (str):  title of the graph (optional; default is no title)
#         id (str):  unique identifier for the graph (optional; will be auto-generated if
#         not provided)

#     Returns:
#         dcc.Graph: Dash pie graph
#     """
#     return dcc.Graph(
#         id=set_ui_object_id(id=id, element_type=element_type),
#         figure=px.pie(
#             data_frame=data,
#             names=list(data.columns.values)[0],
#             title=title,
#         ),
#     )

# def build_bar_graph(element_type, data, title=[], id=[]):
#     """Build Dash bar graph

#     Args:
#         element_type (str): type of graph -- this will end up being the type that elements are
#         selected on in pattern matching callbacks.
#         data (df):  data to be plotted
#         title (str):  title of the graph (optional; default is no title)
#         id (str):  unique identifier for the graph (optional; will be auto-generated if
#         not provided)

#     Returns:
#         dcc.Graph: Dash histogram
#     """
#     return dcc.Graph(
#         id=set_ui_object_id(id=id, element_type=element_type),
#         figure=px.histogram(
#             data_frame=data,
#             x=col_to_plot,
#             title=title,
#         ),
#     )
# def build_scatter_plot(element_type, data, title=[], id=[]):
#     """Build Dash scatter plot

#     Args:
#         element_type (str): type of graph -- this will end up being the type that elements are
#         selected on in pattern matching callbacks.
#         data (df):  data to be plotted
#         title (str):  title of the graph (optional; default is no title)
#         id (str):  unique identifier for the graph (optional; will be auto-generated if
#         not provided)

#     Returns:
#         dcc.Graph: Dash scatter plot
#     """
#     scatter_plot = dcc.Graph(
#         id=set_ui_object_id(id=id, element_type=element_type),
#         figure=px.scatter(
#             data_frame=data,
#             x=graph_object.col_to_plot[1],
#             y=graph_object.col_to_plot[0],
#             # names = list(self.df.columns.values)[0],
#             title=title,
#         ),
#     )
# def get_pie_chart_figure(graph_object):
#     """Get only the figure part of a Dash pie chart

#     Args:
#         graph_object (PieChart from Presenter module): title and options for the graph

#     Returns:
#         dcc.Graph: Dash pie graph
#     """
#     graph = build_pie_chart(graph_object)
#     return graph.figure


# def get_bar_graph_figure(graph_object):
#     """Get only the figure part of a Dash bar graph

#     Args:
#         graph_object (BarGraph from Presenter module): title and options for the graph

#     Returns:
#         dcc.Graph: Dash bar graph
#     """
#     graph = build_bar_graph(graph_object)
#     return graph.figure


#     # Update selection mode to avoid the error:
#     #   unrecognized GUI edit: selections[0].xref
#     # Otherwise, after selecting points in a dataframe, there is an error
#     # (use the inspector in the browser to see the error) on plotly.js
#     # versions 2.13.2 and 2.13.3.
#     # https://github.com/plotly/react-plotly.js/issues/290
#     # Here is a list of plotly versions and which version of plotly.js
#     # they use:
#     # https://github.com/plotly/plotly.py/releases
#     # I got the error in plotly v5.11.0, 5.13.1, 5.9.0, and 5.8.2.
#     # The error only occurs if the scatterplot data is updated as an output
#     # after selecting points from the scatterplot, not if the points are updated
#     # after selecting via checkboxes or pie graphs.
#     scatter_plot.figure.update_layout(
#         newselection_mode="gradual",
#     )

#     return scatter_plot

# def get_scatter_plot_figure(graph_object):
#     """Get only the figure part of a Dash scatter plot

#     Args:
#         graph_object (ScatterPlot from Presenter module): title and options for the graph

#     Returns:
#         dcc.Graph: Dash scatter plot
#     """
#     graph = build_scatter_plot(graph_object)
#     return graph.figure
