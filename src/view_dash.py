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

        # Initialize element to store IDs of each UI component
        self.component_ids = []

    def set_presenter(self, presenter):
        self.presenter = presenter

    def build(self):
        self.testchecklist = FilterChecklist(self.presenter.checklists)
        self.testplot = PieChart(self.presenter.graphs)
        self.testtable = DataTable(self.presenter.data_tables)
        # Store IDs of UI elements
        self.component_ids.extend(
            [self.testchecklist.id, self.testplot.id, self.testtable.id]
        )

        self.app.layout = html.Div(
            [
                self.testchecklist.build(),
                self.testplot.build(),
                self.testtable.build(),
            ]
        )

        self.register_callbacks()

    def register_callbacks(self):
        app = self.app

        @app.callback(
            Output("testtable", "data"),
            Output("testchecklist", "value"),
            Output("testplot", "figure"),
            Input("testchecklist", "value"),
            Input("testplot", "clickData"),
        )
        def filter_data(values, clickData):
            new_filter_criteria = ""
            if ctx.triggered_id is None:
                # The first time the callback runs is when the page is loaded; no
                # filtering is needed here
                table_data = df_to_dict(self.presenter.data_tables.df)
                plot_data = df_to_dict(self.presenter.graphs.df)
                testfigure = PieChart(self.presenter.graphs).build()

                return table_data, [], testfigure.figure  # plot_data
            else:
                # Get id of element that was clicked
                triggered_id = ctx.triggered_id
                # Get display name
                display_name = getattr(self, triggered_id).display_name
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

                # Return new UI stuff
                return (
                    new_table_data,
                    testchecklist_values,
                    testplot.figure,
                )

    def launch_app(self):
        if __name__ == "view_dash":

            self.build()
            self.app.run_server(debug=False)


class UiElement:
    """General class for all UI elements"""

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
    """Checklist containing filter criteria"""

    def __init__(self, filter_checklist_object):
        super().__init__(filter_checklist_object)
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


class PieChart(DataFigure):
    """Pie chart figure"""

    def __init__(self, graph_object):
        super().__init__(graph_object)
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
