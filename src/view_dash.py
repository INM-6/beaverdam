from dash import Dash, html, dcc, dash_table, Input, Output, ctx, State, MATCH, ALL
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

        # Initialize element to store IDs of each UI component
        self.component_ids = []

    def set_presenter(self, presenter):
        self.presenter = presenter

        self.app.layout = html.Div(
            [
                self.build_checklist(self.presenter.checklists),
                self.build_data_figure(self.presenter.graphs),
                html.Div(
                    id="test_output"
                ),  # {"id": "test_output", "type": "TestType"}),
                self.build_data_table(self.presenter.data_tables),
            ]
        )

        self.register_callbacks()

    def register_callbacks(self):
        app = self.app

        @app.callback(
            Output("test_output", "children"),
            Output("testtable", "data"),  # {"type": "DataTable", "idx": ALL}, "data"),
            Input({"type": "Checklist", "idx": ALL}, "value"),
        )
        def filter_data(values):
            if ctx.triggered_id is None:
                # The first time the callback runs is when the page is loaded; no
                # filtering is needed here
                # pass
                display_name = "empty"
            else:
                display_name = ctx.triggered_id["idx"].split("_")[1]
                self.controller.trigger_update_filter_criteria(
                    {display_name: values[0]}
                )
            self.presenter.update()
            return html.Div(
                str(values[0]) + str(self.presenter.core.data_table.filter_criteria)
            ), self.presenter.data_tables.df.to_dict("records")

    def launch_app(self):
        if __name__ == "view_dash":
            self.app.run_server(debug=False)

    # Initialize structure to keep track of ids of dashboard components.
    # dict with keys=id, vals=type of component, named as per the Dash component name
    # ui_ids = {}

    def build_checklist(self, filter_checklist):
        """Build checklist for Dash dashboard

        Args:
            filter_checklist (FilterChecklist): checklist options, ID, and title
        """

        # TODO:  iterate over list of checklists

        # Store ID of each checklist
        self.component_ids.append(
            "Checklist_"
            + filter_checklist.title.replace(" ", "-")
            + "_"
            + str(uuid.uuid4())
        )

        # Build the checklist elements
        return html.Div(
            children=[
                html.Div(children=filter_checklist.title),
                html.Div(
                    children=dcc.Checklist(
                        options=filter_checklist.checklist_options,
                        id={"idx": self.component_ids[-1], "type": "Checklist"},
                        labelStyle={"display": "block"},
                    )
                ),
            ]
        )

    def build_data_table(self, data_table):
        """Build table for Dash dashboard

        Args:
            data_table (DataTable):  data to display in the table
        """
        # TODO:  iterate over list of tables

        # Store ID of each table
        self.component_ids.append("DataTable_" + str(uuid.uuid4()))

        return dash_table.DataTable(
            id="testtable",  # {"idx": self.component_ids[-1], "type": "DataTable"},
            data=data_table.df.to_dict("records"),
        )

    def build_data_figure(self, data_figure):
        """Build figure for Dash dashboard

        Args:
            data_figure (DataFigure): data to plot and information about how to plot it
        """
        # TODO:  iterate over list of figures

        # Store ID of each checklist
        self.component_ids.append("Graph-pie_" + str(uuid.uuid4()))

        if data_figure.graph_type == "pie":
            return dcc.Graph(
                id={"idx": self.component_ids[-1], "type": "Graph_pie"},
                figure=px.pie(
                    data_figure.df,
                    names=list(data_figure.df.columns.values)[0],
                    title=data_figure.title,
                ),
            )
        else:
            raise Exception("Graph type " + data_figure.graph_type + " not defined.")
