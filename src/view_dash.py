from dash import Dash, html, dcc, dash_table
import plotly.express as px

import presenters

# from . import beaverdam_controllers_dash as bd_control
# from beaverdam_controllers_dash import register_callbacks


def build_data_table(data_table):
    """Build table for Dash dashboard

    Args: 
        data_table (DataTable):  data to display in the table
    """    
    return dash_table.DataTable(
            id=data_table.id,
            data=data_table.df.to_dict("records"),
            columns=data_table.columns,
        )


def build_dash_app(datatable, single_figure, single_checkbox_list):
    """Define the layout and build a Dash app

    Args:
        datatable (DashDataTable): data to show and column names, formatted so Dash
        likes it
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            single_checkbox_list.build(),
            single_figure.build(),
            build_data_table(datatable),
        ]
    )

    # bd_control.register_callbacks(app)

    if __name__ == "view_dash":
        app.run_server(debug=True)
