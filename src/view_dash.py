from dash import Dash, html, dcc, dash_table, Input, Output, ctx, State, MATCH, ALL
import plotly.express as px


class View:
    def __init__(self):
        pass

    def set_presenter(self, presenter):
        self.presenter = presenter

    def set_controller(self, controller):
        self.controller = controller


class DashView(View):
    def __init__(self):
        super().__init__()

        self.app = Dash(__name__)

    def set_presenter(self, presenter):
        self.presenter = presenter

    def build(self):
        # Create UI elements
        self.testchecklist = FilterChecklist(self.presenter.checklists)
        self.testplot = PieChart(self.presenter.graphs)
        self.testtable = DataTable(self.presenter.data_tables)
        # Get display name for each UI element, and associate it with the element id
        self.component_ids = {
            self.testchecklist.id["index"]: self.testchecklist.display_name,
            self.testplot.id["index"]: self.testplot.display_name,
        }

        # Arrange UI elements into final layout
        self.app.layout = html.Div(
            [
                self.testchecklist.build(),
                self.testplot.build(),
                self.testtable.build(),
            ]
        )

        # Assign callbacks to UI
        self.register_callbacks()

    def register_callbacks(self):
        app = self.app

        @app.callback(
            Output({"type": "DataTable", "index": ALL}, "data"),
            Output({"type": "FilterChecklist", "index": ALL}, "value"),
            Output({"type": "PieChart", "index": ALL}, "figure"),
            Input({"type": "FilterChecklist", "index": ALL}, "value"),
            Input({"type": "PieChart", "index": ALL}, "clickData"),
        )
        def filter_data(values, clickData):
            new_filter_criteria = ""
            if ctx.triggered_id is None:
                # The first time the callback runs is when the page is loaded; no
                # filtering is needed here
                table_data = df_to_dict(self.presenter.data_tables.df)
                testfigure = PieChart(self.presenter.graphs).build()

                return [
                    # DataTables
                    [table_data],
                    # FilterChecklists
                    [[]],
                    # PieCharts
                    [testfigure.figure],
                ]
            else:
                # Get id of element that was clicked
                triggered_id = ctx.triggered_id["index"]
                # Get display name
                display_name = self.component_ids[
                    triggered_id
                ]  # getattr(self, triggered_id).display_name
                # Get new filter criteria
                # Note that this will be the case whether the box was already selected
                # or not -- need to include a check somewhere (core?) to add or delete
                # from list of selected values
                new_filter_criteria = ctx.triggered[0]["value"]
                # If the object clicked was a graph, the new filter criteria will be a
                # dict of information. Extract the specific criteria.
                if isinstance(new_filter_criteria, dict):
                    new_filter_criteria = [new_filter_criteria["points"][0]["label"]]

                # Update filter criteria
                self.controller.trigger_update_filter_criteria(
                    {display_name: new_filter_criteria}
                )

                # Update presenter
                self.presenter.update()
                # Update data for UI components
                new_table_data = df_to_dict(self.presenter.data_tables.df)
                testchecklist_values = self.presenter.checklists.selected_options
                testplot = PieChart(self.presenter.graphs).build()

                # Return new UI stuff:
                # - If ONE Output() is pattern-matching, Dash expects the returned value
                # to be a list containing one list for each of the detected output.
                # - If MORE THAN ONE Output() is pattern-matching, Dash expects the
                # returned value to be a list containing one list for each of the
                # Output() elements, in turn containing one list for each of the
                # detected outputs.
                return [
                    # DataTables
                    [new_table_data],
                    # FilterChecklists
                    [testchecklist_values],
                    # PieCharts
                    [testplot.figure],
                ]

    def launch_app(self):
        if __name__ == "view_dash":

            self.build()
            self.app.run_server(debug=False)


class UiElement:
    """General class for all UI elements"""

    def __init__(self, UIelement):
        # Set ID of element
        self.id = {"index": UIelement.id, "type": "undefined"}
        # pass

    def build(self):
        # Use on first creation of element
        pass

    def update(self):
        # Use to update element with current info from presenter class.  Only return
        # attributes of the element that need updating.
        pass


class FilterChecklist(UiElement):
    """Checklist containing filter criteria"""

    def __init__(self, filter_checklist_object):
        super().__init__(filter_checklist_object)
        # Set type of UI element
        self.id["type"] = "FilterChecklist"
        # Override default ID for debugging purposes
        self.id["index"] = "test-checklist"

        # Duplicate fields from filter_checklist_object [there's got to be a nicer way
        # to do this]
        self.checklist_options = filter_checklist_object.checklist_options
        self.display_name = filter_checklist_object.display_name
        self.title = filter_checklist_object.title

    def build(self):
        """Build checklist for Dash dashboard

        Returns:
            html.Div containing checklist title and options
        """

        # Build the checklist elements
        return html.Div(
            children=[
                html.Div(children=self.title),
                html.Div(
                    children=dcc.Checklist(
                        options=self.checklist_options,
                        value=[],
                        id=self.id,
                        labelStyle={"display": "block"},
                    )
                ),
            ]
        )

    def update(self, new_values):
        """Update checklist"""
        self.values = new_values


class DataFigure(UiElement):
    """General class for figures"""

    def __init__(self, UIelement):
        super().__init__(UIelement)
        # Set type of UI element
        self.id["type"] = "DataFigure"


class PieChart(DataFigure):
    """Pie chart figure"""

    def __init__(self, graph_object):
        super().__init__(graph_object)
        # Set type of UI element
        self.id["type"] = "PieChart"
        # Override default ID for debugging purposes
        self.id["index"] = "test-plot"
        # Duplicate fields from graph_object [there's got to be a nicer way to do this]
        self.col_to_plot = graph_object.col_to_plot
        self.display_name = self.col_to_plot
        self.df = graph_object.df
        self.graph_type = graph_object.graph_type
        self.title = graph_object.title

    def build(self):
        """Build plot for Dash dashboard

        Returns:
            html.Div containing plot
        """

        return dcc.Graph(
            id=self.id,
            figure=px.pie(
                self.df,
                names=list(self.df.columns.values)[0],
                title=self.title,
            ),
        )


class DataTable(UiElement):
    """Class for data tables"""

    def __init__(self, prettydatatable_object):
        super().__init__(prettydatatable_object)
        # Set type of UI element
        self.id["type"] = "DataTable"
        # Override default ID for debugging purposes
        self.id["index"] = "test-table"
        # Duplicate fields from prettydatatable_object
        self.df = prettydatatable_object.df

    def build(self):

        return dash_table.DataTable(
            id=self.id,
            data=df_to_dict(self.df),
        )


def df_to_dict(df):
    """Convert dataframe to the data format that Dash wants for a DataTable

    Args:
        df (dataframe): data to be shown in DataTable
    """
    return df.to_dict("records")
