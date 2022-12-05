from dash import Dash, html
#from . import beaverdam_controllers_dash as bd_control
#from beaverdam_controllers_dash import register_callbacks


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
            datatable.build(),
        ]
    )

    #bd_control.register_callbacks(app)

    if __name__ == "view_dash":
        app.run_server(debug=True)
