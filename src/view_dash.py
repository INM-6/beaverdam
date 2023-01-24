from dash import Dash, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import plotly.express as px
import uuid


class View:
    def __init__(self):
        pass

    def set_presenter(self, presenter):
        self.presenter = presenter

    def set_controller(self, controller):
        self.controller = controller


class DashView(View):
    def __init__(self):  # TODO: make inputs more generic
        super().__init__()

        self.app = Dash(__name__)

    def set_presenter(self, presenter):
        self.presenter = presenter
        self.app.layout = html.Div(
            [
                build_checklist(self.presenter.checklists),
                build_data_figure(self.presenter.graphs),
                html.Div(
                    id="test_output"
                ),  # {"id": "test_output", "type": "TestType"}),
                build_data_table(self.presenter.data_tables),
            ]
        )

        self.register_callbacks()

    def register_callbacks(self):
        app = self.app

        @app.callback(
            Output("test_output", "children"),
            Input({"type": "Checklist", "idx": ALL}, "value"),
        )
        def filter_data(values):
            return html.Div(str(values))
            # bdc.trigger_update_filter_criteria(values)

    def launch_app(self):
        if __name__ == "view_dash":
            self.app.run_server(debug=False)


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
                    id={"idx": "Checklist_" + str(uuid.uuid4()), "type": "Checklist"},
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
        id={"idx": "DataTable_" + str(uuid.uuid4()), "type": "DataTable"},
        data=data_table.df.to_dict("records"),
    )


def build_data_figure(data_figure):
    """Build figure for Dash dashboard

    Args:
        data_figure (DataFigure): data to plot and information about how to plot it
    """
    if data_figure.graph_type == "pie":
        return dcc.Graph(
            id={"idx": "Graph_pie_" + str(uuid.uuid4()), "type": "Graph_pie"},
            figure=px.pie(
                data_figure.df,
                names=list(data_figure.df.columns.values)[0],
                title=data_figure.title,
            ),
        )
    else:
        raise Exception("Graph type " + data_figure.graph_type + " not defined.")
