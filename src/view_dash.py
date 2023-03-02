from dash import Dash, html, dcc, dash_table, Input, Output, ctx, State, MATCH, ALL
import plotly.express as px
# import uuid


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

    def build(self):
        self.testchecklist = FilterChecklist(self.presenter.checklists)
        self.testfigure = PieChart(self.presenter.graphs)
        self.testtable = DataTable(self.presenter.data_tables)
        # Store IDs of UI elements
        self.component_ids.extend([self.testchecklist.id, self.testfigure.id, self.testtable.id])

        self.app.layout = html.Div(
            [
                # self.build_checklist(self.presenter.checklists),
                self.testchecklist.build(),
                self.testfigure.build(),
                # self.build_data_figure(self.presenter.graphs),
                html.Div(
                    id="test_output"
                ),  # {"id": "test_output", "type": "TestType"}),
                # self.build_data_table(self.presenter.data_tables),
                self.testtable.build(),
            ]
        )

        self.register_callbacks()


    def register_callbacks(self):
        app = self.app

        @app.callback(
            Output("test_output", "children"),
            Output("testtable", "data"),#self.component_ids[2], "data"),##Output(''.join([i for i in self.component_ids if "DataTable" in i]), "data"), # Output("testtable", "data"),  # Output({"type": "DataTable", "idx": ALL}, "data"),
            Output("testplot", "figure"), # veronica:  try using the "figure" property and returning an entire new plot?
            Input({"type": "Checklist", "idx": ALL}, "value"),#Input("testchecklist", "value"),#self.component_ids[0], "value"),#
            Input({"type": "Graph", "idx": ALL}, "clickData"),#Input("testplot", "clickData"),#self.component_ids[1], "clickData"),#
        )
        def filter_data(values, clickData):
            new_filter_criteria = ""
            if ctx.triggered_id is None:
                # The first time the callback runs is when the page is loaded; no
                # filtering is needed here
                # pass
                test_output = html.Div(
                    ""
                )
                table_data = df_to_dict(self.presenter.data_tables.df)#self.testtable.get_updated_df(self.presenter.data_tables.df)
                plot_data = df_to_dict(self.presenter.graphs.df)
                testfigure = PieChart(self.presenter.graphs).build()

                return test_output, table_data, testfigure.figure#plot_data
            else:
                # Get display name
                # display_name = ctx.triggered_id["idx"].split("_")[1]
                display_name = getattr(self, ctx.triggered_id["idx"]).display_name
                # Get new filter values -- the method is different for the different
                # types of input
                input_type = ctx.triggered_id["type"]
                if input_type == "Checklist":
                    new_filter_criteria = values[0]
                elif input_type == "Graph-pie":
                    new_filter_criteria = [clickData[0]["points"][0]["label"]]
                else:
                    raise Exception("Undefined UI input")
                # Update filter criteria
                self.controller.trigger_update_filter_criteria(
                    {display_name: new_filter_criteria}
                )

                # Update presenter
                self.presenter.update()
                # Update data for UI components
                new_test_output = html.Div(
                    str(new_filter_criteria)
                    + str(self.presenter.core.data_table.filter_criteria)
                )
                new_table_data = df_to_dict(self.presenter.data_tables.df)#self.testtable.get_updated_df(self.presenter.data_tables.df)
                new_plot_data = df_to_dict(self.presenter.graphs.df)
                testfigure = PieChart(self.presenter.graphs).build()

                # Return new UI stuff

                    # self.build() # veronica - figure out why UI elements aren't updating -- do I need to set them as outputs to the callback?
                # self.presenter.update()
                return new_test_output, new_table_data, testfigure.figure#new_plot_data#self.presenter.data_tables.df.to_dict("records")#, self.presenter.graphs.df


    def launch_app(self):
        if __name__ == "view_dash":

            self.build()
            self.app.run_server(debug=False)

    # Initialize structure to keep track of ids of dashboard components.
    # dict with keys=id, vals=type of component, named as per the Dash component name
    # ui_ids = {}

    # def build_data_table(self, data_table):
    #     """Build table for Dash dashboard

    #     Args:
    #         data_table (DataTable):  data to display in the table
    #     """
    #     # TODO:  iterate over list of tables

    #     # Store ID of each table
    #     self.component_ids.append("DataTable_" + str(uuid.uuid4()))

    #     return dash_table.DataTable(
    #         id="testtable",  # {"idx": self.component_ids[-1], "type": "DataTable"},
    #         data=data_table.df.to_dict("records"),
    #     )

    # def build_data_figure(self, data_figure):
    #     """Build figure for Dash dashboard

    #     Args:
    #         data_figure (DataFigure): data to plot and information about how to plot it
    #     """
    #     # TODO:  iterate over list of figures

    #     # Store ID of each checklist
    #     self.component_ids.append(
    #         "Graph-pie_" + data_figure.col_to_plot + "_" + str(uuid.uuid4())
    #     )

    #     if data_figure.graph_type == "pie":
    #         return dcc.Graph(
    #             id="testplot",#{"idx": self.component_ids[-1], "type": "Graph-pie"},
    #             figure=px.pie(
    #                 data_figure.df,
    #                 names=list(data_figure.df.columns.values)[0],
    #                 title=data_figure.title,
    #             ),
    #         )
    #     else:
    #         raise Exception("Graph type " + data_figure.graph_type + " not defined.")

class UiElement():
    """General class for all UI elements
    """
    def __init__(self, UIelement):
        # Set ID of element
        self.id = UIelement.id
        pass

    def build(self):
        # Use on first creation of element
        pass

    def update(self):
        # Use to update element with current info from presenter class.  Only return
        # attributes of the element that need updating.
        pass

class FilterChecklist(UiElement):
    """Checklist containing filter criteria
    """

    def __init__(self, filter_checklist_object):
        super().__init__(filter_checklist_object)
        # Store information for filter_checklist_object by assigning all fields to self
        # [there's got to be a nicer way to do this]
        # self.checklist_object = filter_checklist_object # veronica
        # Set ID of UI element
        # self.id = "Checklist_" + filter_checklist_object.display_name + "_" + str(uuid.uuid4())
        # Duplicate fields from filter_checklist_object
        self.checklist_options = filter_checklist_object.checklist_options
        self.display_name = filter_checklist_object.display_name
        self.title = filter_checklist_object.title

    def build(self):
        """Build checklist for Dash dashboard

        Returns:
            html.Div containing checklist title and options
        """

        # TODO:  iterate over list of checklists

        # Store ID of each checklist
        # self.component_ids.append(
        #     "Checklist_" + filter_checklist.display_name + "_" + str(uuid.uuid4())
        # )

        # Build the checklist elements
        return html.Div(
            children=[
                html.Div(children=self.title),
                html.Div(
                    children=dcc.Checklist(
                        options=self.checklist_options,
                        id={"idx": self.id, "type": "Checklist"},
                        # id={"idx": self.component_ids[-1], "type": "Checklist"},
                        labelStyle={"display": "block"},
                    )
                ),
            ]
        )

    def update(self, new_values):
        """Update checklist
        """
        self.values = new_values

class DataFigure(UiElement):
    """General class for figures
    """
    def __init__(self, UIelement):
        super().__init__(UIelement)

class PieChart(DataFigure):
    """Pie chart figure
    """

    def __init__(self, graph_object):
        super().__init__(graph_object)
        # Store information for graph_object by assigning all fields to self
        # [there's got to be a nicer way to do this]
        # self.checklist_object = filter_checklist_object # veronica
        # Set ID of UI element
        # self.id = "Graph-pie_" + str(uuid.uuid4())
        # Duplicate fields from graph_object
        self.col_to_plot = graph_object.col_to_plot
        self.df = graph_object.df
        self.graph_type = graph_object.graph_type
        self.title = graph_object.title

    def build(self):
        """Build plot for Dash dashboard

        Returns:
            html.Div containing plot
        """
        # Store ID of each checklist
        # self.component_ids.append(self.id)

        return dcc.Graph(
            id=self.id,#"testplot",#{"idx": self.component_ids[-1], "type": "Graph-pie"},
            figure=px.pie(
                self.df,
                names=list(self.df.columns.values)[0],
                title=self.title,
            ),
        )

    # def update_figure(self):
    #     return {figure: px.pie(
    #             self.df,
    #             names=list(self.df.columns.values)[0],
    #             title=self.title,
    #         )


class DataTable(UiElement):
    """Class for data tables
    """
    def __init__(self, prettydatatable_object):
        super().__init__(prettydatatable_object)
        # Set ID of UI element
        # self.id = "DataTable_" + str(uuid.uuid4())
        # Duplicate fields from prettydatatable_object
        self.df = prettydatatable_object.df

    def build(self):
        # Store ID of each table
        # self.component_ids.append(self.id)

        return dash_table.DataTable(
            id=self.id,  # {"idx": self.component_ids[-1], "type": "DataTable"},
            data=df_to_dict(self.df),
        )

def df_to_dict(df):
    """Convert dataframe to the data format that Dash wants for a DataTable

    Args:
        df (dataframe): data to be shown in DataTable
    """
    return df.to_dict("records")