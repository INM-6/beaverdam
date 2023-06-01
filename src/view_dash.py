"""Builds a user interface using Dash"""

import view as view
import datafigure_dash as fig
import filterchecklist_dash as checklist
import datatable_dash as dtable
import resetbutton_dash as resetbutton
from dash import Dash, html, Input, Output, ctx, State, MATCH, ALL
import dash_bootstrap_components as dbc


class DashView(view.View):
    """Use a Dash dashboard for the user interface

    Args:
        view.View (View): this class is based on the generic View class
    """

    def __init__(self):
        """Define Dash as a frontend"""
        super().__init__()

        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    def build(self):
        """Create and assemble all elements for user interface; load callback functions"""
        # Make sure we are starting with clean variables
        self.checklists = []
        self.plots = []
        self.tables = []

        # Create UI elements
        self.resetbutton = resetbutton.DashResetButton()
        for ichecklist in self.presenter.checklists:
            self.checklists.append(checklist.DashFilterChecklist(ichecklist))
        for iplot in self.presenter.graphs:
            if iplot.graph_type == "pie":
                self.plots.append(fig.DashPieChart(iplot))
            elif iplot.graph_type == "bar":
                self.plots.append(fig.DashBarGraph(iplot))
            elif iplot.graph_type == "scatter":
                self.plots.append(fig.DashScatterPlot(iplot))
            else:
                pass
        for itable in self.presenter.data_tables:
            self.tables.append(dtable.DashDataTable(itable))

        # Get display name for each interactive element and associate it with the
        # element id
        self.component_display_names = {}
        for ichecklist in self.checklists:
            self.component_display_names[
                ichecklist.id["index"]
            ] = ichecklist.display_name
        for iplot in self.plots:
            self.component_display_names[iplot.id["index"]] = iplot.display_name

        # Assemble UI elements into user interface
        topbar_elements = []
        sidebar_elements = []
        mainpanel_elements = []
        topbar_elements.append(html.Div(html.H1("Beaverdam")))
        sidebar_elements.append(self.resetbutton.build())
        for ichecklist in self.checklists:
            sidebar_elements.append(ichecklist.build())
        for iplot in self.plots:
            mainpanel_elements.append(iplot.build())
        for itable in self.tables:
            mainpanel_elements.append(itable.build())
        self.app.layout = dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            topbar_elements,
                        ),
                        # style={"background-color": "#ff0000",},
                    ),
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                sidebar_elements,
                            ),
                            md=1,
                            style={#"background-color": "#ffff00",
                                   "overflow-wrap": "break-word"},
                        ),
                        dbc.Col(
                            html.Div(
                                mainpanel_elements,
                            ),
                            md=11,
                            # style={"background-color": "#0ff000",},
                        ),
                    ],
                ),
            ],
            fluid=True,
        )

        # Assign callbacks to UI
        self.register_callbacks()

    def register_callbacks(self):
        """Define actions that occur on user interaction; update frontend appropriately

        Returns:
            Updated versions of checklists, plots, and tables
        """
        app = self.app

        @app.callback(
            Output({"type": "DataTable", "index": ALL}, "data"),
            Output({"type": "FilterChecklist", "index": ALL}, "value"),
            Output({"type": "PieChart", "index": ALL}, "figure"),
            Output({"type": "BarGraph", "index": ALL}, "figure"),
            Output({"type": "ScatterPlot", "index": ALL}, "figure"),
            Input({"type": "ResetButton", "index": ALL}, "n_clicks"),
            Input({"type": "FilterChecklist", "index": ALL}, "value"),
            Input({"type": "PieChart", "index": ALL}, "clickData"),
            Input({"type": "BarGraph", "index": ALL}, "clickData"),
            Input({"type": "ScatterPlot", "index": ALL}, "selectedData"),
        )
        def filter_data(
            values, resetButtonClicks, pieClickData, barClickData, selectionData
        ):
            # Get id and type of element that was clicked
            triggered_element = ctx.triggered_id
            # On load, ctx.triggered_id is None, and we don't have to filter anyway
            if triggered_element is not None:

                # Get specific information about the element that was triggered
                triggered_element_id = triggered_element["index"]
                triggered_element_type = ctx.triggered_id["type"]

                # Get display name, if it exists.
                try:
                    display_name = self.component_display_names[triggered_element_id]
                    # To be consistent, make sure display_name is a list, even if it's only
                    # one element
                    if isinstance(display_name, str):
                        display_name = [display_name]
                except:
                    pass

                # Get new filter criteria.  How this happens depends on the type of
                # element that was triggered.

                # If the element triggered was the reset button, reset filter criteria
                if triggered_element_type == "ResetButton":
                    self.controller.trigger_clear_filter_criteria()

                if triggered_element_type == "FilterChecklist":
                    # Note that filter criteria will be listed whether the box was
                    # already selected or not -- need to include a check somewhere
                    # (core?) to add or delete from list of selected values
                    new_filter_criteria = ctx.triggered[0]["value"]
                    self.controller.trigger_update_filter_criteria(
                        {display_name[0]: new_filter_criteria}
                    )
                elif triggered_element_type == "PieChart":
                    # If the object clicked was a graph, the new filter criteria will be a
                    # dict of information. Extract the specific criteria.
                    new_filter_criteria = [
                        ctx.triggered[0]["value"]["points"][0]["label"]
                    ]
                    self.controller.trigger_update_filter_criteria(
                        {display_name[0]: new_filter_criteria}
                    )
                elif triggered_element_type == "BarGraph":
                    # If the object clicked was a graph, the new filter criteria will be a
                    # dict of information. Extract the specific criteria.
                    new_filter_criteria = [ctx.triggered[0]["value"]["points"][0]["x"]]
                    self.controller.trigger_update_filter_criteria(
                        {display_name[0]: new_filter_criteria}
                    )
                elif triggered_element_type == "ScatterPlot":
                    # When I wrote this code, "pointNumber" and "pointIndex" were equal.
                    selected_rows = [
                        point["pointIndex"]
                        for point in ctx.triggered[0]["value"]["points"]
                    ]
                    self.controller.trigger_clear_filter_criteria()
                    self.controller.trigger_select_dataframe_rows(selected_rows)

                # Update presenter
                self.presenter.update()

            # Make sure that all the elements of ctx.outputs_list are lists of dicts.
            # Default behaviour is for an element to be a dict if there is only one
            # dict, or a list of dicts if there is more than one dict -- this screws up
            # the loops later.
            outputs_list = [
                [item] if isinstance(item, dict) else item for item in ctx.outputs_list
            ]

            # Update tables
            new_table_data = []
            presenter_table_ids = {
                itable.id: idx for idx, itable in enumerate(self.presenter.data_tables)
            }
            for itable in outputs_list[0]:
                # Get ID of UI table
                ui_id = itable["id"]["index"]
                # Find table in the presenter with the same ID as the UI table
                presenter_id = presenter_table_ids[ui_id]
                # Add the updated data for the table to the list of data_table data
                new_table_data.append(
                    dtable.df_to_dict(self.presenter.data_tables[presenter_id].df)
                )

            # Update FilterChecklists
            new_checklist_data = []
            presenter_checklist_ids = {
                ichecklist.id: idx
                for idx, ichecklist in enumerate(self.presenter.checklists)
            }
            for ichecklist in outputs_list[1]:
                # Get ID of UI checklist
                ui_id = ichecklist["id"]["index"]
                # Find checklist in the presenter with the same ID as the UI checklist
                presenter_id = presenter_checklist_ids[ui_id]
                # Add the updated data for the checklist to the list of checklist data
                new_checklist_data.append(
                    self.presenter.checklists[presenter_id].selected_options
                )

            # Update plots
            presenter_plot_ids = {
                iplot.id: idx for idx, iplot in enumerate(self.presenter.graphs)
            }
            new_piechart_data = []
            for iplot in outputs_list[2]:
                # Get ID of UI plot
                ui_id = iplot["id"]["index"]
                # Find plot in the presenter with the same ID as the UI plot
                presenter_id = presenter_plot_ids[ui_id]
                # Add the updated data for the plot to the list of piechart data
                new_piechart_data.append(
                    fig.DashPieChart(self.presenter.graphs[presenter_id]).build().figure
                )
            new_bargraph_data = []
            for iplot in outputs_list[3]:
                # Get ID of UI plot
                ui_id = iplot["id"]["index"]
                # Find plot in the presenter with the same ID as the UI plot
                presenter_id = presenter_plot_ids[ui_id]
                # Add the updated data for the plot to the list of piechart data
                new_bargraph_data.append(
                    fig.DashBarGraph(self.presenter.graphs[presenter_id]).build().figure
                )
            new_scatterplot_data = []
            for iplot in outputs_list[4]:
                # Get ID of UI plot
                ui_id = iplot["id"]["index"]
                # Find plot in the presenter with the same ID as the UI plot
                presenter_id = presenter_plot_ids[ui_id]
                # Add the updated data for the plot to the list of scatterplot data
                new_scatterplot_data.append(
                    fig.DashScatterPlot(self.presenter.graphs[presenter_id])
                    .build()
                    .figure
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
                new_bargraph_data,
                new_scatterplot_data,
            ]

    def launch_ui(self):
        """Build and run frontend"""
        if __name__ == "view_dash":

            self.build()
            self.app.run_server(debug=False)
