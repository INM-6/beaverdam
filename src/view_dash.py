from dash import Dash, html, dcc, dash_table
import plotly.express as px
import uuid

# import presenters

# from . import beaverdam_controllers_dash as bd_control
# from beaverdam_controllers_dash import register_callbacks

# Initialize structure to keep track of ids of dashboard components.
# dict with keys=id, vals=type of component, named as per the Dash component name
ui_ids = {}


def build_checklist(filter_checklist):
    """Build checklist for Dash dashboard

    Args:
        filter_checklist (FilterChecklist): checklist options, ID, and title
    """
    return html.Div(
        children=[
            html.Div(children=filter_checklist.title),
            html.Div(
                children=dcc.Checklist(
                    options=filter_checklist.checklist_options,
                    id={"id": "Checklist_" + str(uuid.uuid4()), "type": "Checklist"},
                    labelStyle={"display": "block"},
                )
            ),
        ]
    )


def build_data_table(data_table):
    """Build table for Dash dashboard

    Args:
        data_table (DataTable):  data to display in the table
    """
    return dash_table.DataTable(
        id={"id": "DataTable_" + str(uuid.uuid4()), "type": "DataTable"},
        data=data_table.df.to_dict("records"),
        # columns=list(data_table.df.columns),
    )


def build_data_figure(data_figure):
    """Build figure for Dash dashboard

    Args:
        data_figure (DataFigure): data to plot and information about how to plot it
    """
    if data_figure.graph_type == "pie":
        return dcc.Graph(
            id={"id": "Graph_pie_" + str(uuid.uuid4()), "type": "Graph_pie"},
            figure=px.pie(
                data_figure.df,
                names=list(data_figure.df.columns.values)[0],
                title=data_figure.title,
            ),
        )
    else:
        raise Exception("Graph type " + data_figure.graph_type + " not defined.")


def build_dash_app(datatable, single_figure, single_checkbox_list):
    """Define the layout and build a Dash app

    Args:
        datatable (DashDataTable): data to show and column names, formatted so Dash
        likes it
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            build_checklist(single_checkbox_list),
            build_data_figure(single_figure),
            build_data_table(datatable),
        ]
    )

    # bd_control.register_callbacks(app)

    # @app.callback(
    #     Output(

    if __name__ == "view_dash":
        app.run_server(debug=True)
