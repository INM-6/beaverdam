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
        # Make sure we are starting with clean variables
        self.checklists = []
        self.plots = []
        self.tables = []

        # Create UI elements
        for ichecklist in self.presenter.checklists:
            self.checklists.append(FilterChecklist(ichecklist))
        for iplot in self.presenter.graphs:
            if iplot.graph_type == "pie":
                self.plots.append(PieChart(iplot))
            elif iplot.graph_type == "scatter":
                self.plots.append(ScatterPlot(iplot))
            else:
                pass
        for itable in self.presenter.data_tables:
            self.tables.append(DataTable(itable))

        # Get display name for each interactive element and associate it with the element id
        self.component_display_names = {}
        for ichecklist in self.checklists:
            self.component_display_names[
                ichecklist.id["index"]
            ] = ichecklist.display_name
        for iplot in self.plots:
            self.component_display_names[iplot.id["index"]] = iplot.display_name

        # Assemble UI elements into user interface
        UIelements = []
        for ichecklist in self.checklists:
            UIelements.append(ichecklist.build())
        for iplot in self.plots:
            UIelements.append(iplot.build())
        for itable in self.tables:
            UIelements.append(itable.build())
        self.app.layout = html.Div(UIelements)

        # Assign callbacks to UI
        self.register_callbacks()

    def register_callbacks(self):
        app = self.app

        @app.callback(
            Output({"type": "DataTable", "index": ALL}, "data"),
            Output({"type": "FilterChecklist", "index": ALL}, "value"),
            Output({"type": "PieChart", "index": ALL}, "figure"),
            Output({"type": "ScatterPlot", "index": ALL}, "figure"),
            Input({"type": "FilterChecklist", "index": ALL}, "value"),
            Input({"type": "PieChart", "index": ALL}, "clickData"),
        )
        def filter_data(values, clickData):
            # Get id of element that was clicked
            triggered_id = ctx.triggered_id
            # On load, ctx.triggered_id is None, and we don't have to filter anyway
            if triggered_id is not None:

                # Get display name
                display_name = self.component_display_names[triggered_id["index"]]

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

            # Update tables
            new_table_data = []
            presenter_table_ids = {
                itable.id: idx for idx, itable in enumerate(self.presenter.data_tables)
            }
            for itable in ctx.outputs_list[0]:
                # Get ID of UI table
                ui_id = itable["id"]["index"]
                # Find table in the presenter with the same ID as the UI table
                presenter_id = presenter_table_ids[ui_id]
                # Add the updated data for the table to the list of data_table data
                new_table_data.append(
                    df_to_dict(self.presenter.data_tables[presenter_id].df)
                )

            # Update FilterChecklists
            new_checklist_data = []
            presenter_checklist_ids = {
                ichecklist.id: idx
                for idx, ichecklist in enumerate(self.presenter.checklists)
            }
            for ichecklist in ctx.outputs_list[1]:
                # Get ID of UI checklist
                ui_id = ichecklist["id"]["index"]
                # Find table in the presenter with the same ID as the UI table
                presenter_id = presenter_checklist_ids[ui_id]
                # Add the updated data for the table to the list of data_table data
                new_checklist_data.append(
                    self.presenter.checklists[presenter_id].selected_options
                )

            # Update plots
            presenter_plot_ids = {
                iplot.id: idx for idx, iplot in enumerate(self.presenter.graphs)
            }
            new_piechart_data = []
            for iplot in ctx.outputs_list[2]:
                # Get ID of UI table
                ui_id = iplot["id"]["index"]
                # Find table in the presenter with the same ID as the UI table
                presenter_id = presenter_plot_ids[ui_id]
                # Add the updated data for the table to the list of data_table data
                new_piechart_data.append(
                    PieChart(self.presenter.graphs[presenter_id]).build().figure
                )
            new_scatterplot_data = []
            for iplot in ctx.outputs_list[3]:
                # Get ID of UI table
                ui_id = iplot["id"]["index"]
                # Find table in the presenter with the same ID as the UI table
                presenter_id = presenter_plot_ids[ui_id]
                # Add the updated data for the table to the list of data_table data
                new_scatterplot_data.append(
                    ScatterPlot(self.presenter.graphs[presenter_id]).build().figure
                )

            # Return new UI stuff:
            # - If ONE Output() is pattern-matching, Dash expects the returned value
            # to be a list containing one list for each of the detected output.
            # - If MORE THAN ONE Output() is pattern-matching, Dash expects the
            # returned value to be a list containing one list for each of the
            # Output() elements, in turn containing one list for each of the
            # detected outputs.
            return [
                new_table_data,
                new_checklist_data,
                new_piechart_data,
                new_scatterplot_data,
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
                data_frame=self.df,
                names=list(self.df.columns.values)[0],
                title=self.title,
            ),
        )


class ScatterPlot(DataFigure):
    """Scatterplot figure"""

    def __init__(self, graph_object):
        super().__init__(graph_object)

        # Set type of UI element
        self.id["type"] = "ScatterPlot"

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
            figure=px.scatter(
                data_frame=self.df,
                x=self.col_to_plot[1],
                y=self.col_to_plot[0],
                # names = list(self.df.columns.values)[0],
                title=self.title,
            ),
        )


class DataTable(UiElement):
    """Class for data tables"""

    def __init__(self, prettydatatable_object):
        super().__init__(prettydatatable_object)

        # Set type of UI element
        self.id["type"] = "DataTable"

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
