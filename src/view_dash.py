"""Builds a user interface using Dash"""

import view as view
import datafigure_dash as fig
import filterchecklist_dash as checklist
import datatable_dash as dtable
import resetbutton_dash as resetbutton
import builduielements_dash as buildui
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
        # Define some parameters for UI
        is_page_fluid = True
        header_height = "56px"

        ui_elements = self.ui_elements

        # Populate UI elements for each UI component, from Presenter information
        checklist_elements = []
        datatable_elements = []
        figure_elements = []
        for key, val in ui_elements.items():
            element_id = val["properties"]["id"]
            element_type = val["properties"]["type"]
            if "style" in val["properties"]:
                element_style = val["properties"]["style"]
            element_contents = val["contents"]
            if element_type == "DataTable":
                datatable_elements.append(
                    buildui.build_data_table(
                        id=element_id,
                        element_type=element_type,
                        data=element_contents["df"],
                    )
                )
            elif element_type == "FilterChecklist":
                checklist_elements.append(
                    buildui.build_filter_checklist(
                        id=element_id,
                        element_type=element_type,
                        items=element_contents["checklist_options"],
                        title=element_contents["title"],
                    )
                )
            elif element_type == "DataFigure":
                ielement = []
                igraph = []
                if element_style == "pie":
                    igraph = buildui.build_pie_chart(
                        # id=element_id,
                        # element_type=element_type,
                        data=element_contents["df"],
                        title=element_contents["title"],
                    )
                elif element_style == "bar":
                    igraph = buildui.build_bar_graph(
                        # id=element_id,
                        # element_type=element_type,
                        data=element_contents["df"],
                        title=element_contents["title"],
                    )
                elif element_style == "scatter":
                    igraph = buildui.build_scatter_plot(
                        # id=element_id,
                        # element_type=element_type,
                        data=element_contents["df"],
                        title=" vs. ".join(element_contents["title"]),
                    )
                # Create the plot
                ielement = buildui.build_data_figure(
                    graph_object=igraph, id=element_id, element_type=element_type
                )
                figure_elements.append(
                    ielement
                    # buildui.build_graph(
                    #     id=element_id,
                    #     data=element_contents["df"],
                    #     style=graph_style,
                    #     title=element_contents["title"],
                    # )
                )

        # Assemble elements into the different UI panels
        # list1.extend(list2) and list1 += list2 are equivalent:
        #   https://stackoverflow.com/a/56407963
        topbar_elements = []
        sidebar_elements = []
        mainpanel_elements = []
        topbar_elements.append(html.Div(html.H1("Beaverdam")))
        sidebar_elements.append(buildui.build_button("Reset", "ResetButton"))
        sidebar_elements.extend(checklist_elements)
        mainpanel_elements.extend(figure_elements)
        mainpanel_elements.extend(datatable_elements)
        # for ichecklist in self.presenter.checklists:
        #     sidebar_elements.append(buildui.build_filter_checklist(ichecklist))
        # for iplot in self.presenter.graphs:
        #     mainpanel_elements.append(buildui.build_graph(iplot))
        # for itable in self.presenter.data_tables:
        #     mainpanel_elements.append(buildui.build_data_table(itable))
        self.app.layout = dbc.Container(
            [
                dbc.Navbar(
                    topbar_elements,
                    style={  # "background-color": "#ff0000"
                        "height": header_height,
                    },
                    sticky="top",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Nav(
                                sidebar_elements,
                                vertical="md",
                            ),
                            md=2,
                            style={  # "background-color": "#ffff00",
                                "position": "sticky",
                                "top": header_height,
                                "height": "calc(100vh - " + header_height + ")",
                                "overflow-y": "scroll",
                                "overflow-wrap": "break-all",
                            },
                        ),
                        dbc.Col(
                            html.Div(
                                mainpanel_elements,
                            ),
                            md=10,
                            style={},  # "background-color": "#0ff000",
                        ),
                    ],
                ),
            ],
            fluid=is_page_fluid,
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
            Output({"type": "DataFigure", "index": ALL}, "figure"),
            # Output({"type": "BarGraph", "index": ALL}, "figure"),
            # Output({"type": "ScatterPlot", "index": ALL}, "figure"),
            Input({"type": "ResetButton", "index": ALL}, "n_clicks"),
            Input({"type": "FilterChecklist", "index": ALL}, "value"),
            # Input({"type": "PieChart", "index": ALL}, "clickData"),
            # Input({"type": "BarGraph", "index": ALL}, "clickData"),
            # Input({"type": "ScatterPlot", "index": ALL}, "selectedData"),
            Input({"type": "DataFigure", "index": ALL}, "clickData"),
            Input({"type": "DataFigure", "index": ALL}, "selectedData"),
        )
        def filter_data(
            resetButtonClicks,
            checklistValue,
            figureClickData,
            figureSelectedData
            # values, resetButtonClicks, pieClickData, barClickData, selectionData
        ):
            # Get id and type of element that was clicked
            triggered_element = ctx.triggered_id

            # Get information about each element
            ui_element_info = self.presenter.get_elements()
            # Get information to relate each element ID to its corresponding location in
            # the list of UI elements in Presenter.  TODO:  change the list of UI
            # elements in Presenter to a dict, for easier reference.
            ui_element_ids = [key for key in ui_element_info.keys()]

            # On load, ctx.triggered_id is None, and we don't have to filter anyway
            if triggered_element is not None:

                # Get specific information about the element that was triggered
                triggered_element_id = triggered_element["index"]
                triggered_element_type = ctx.triggered_id["type"]

                # Find the database field(s) represented by the clicked element
                try:
                    database_field = ui_element_info[triggered_element_id][
                        "properties"
                    ]["field"][0]
                except:
                    # Some UI elements, e.g. the reset button, don't have a field
                    database_field = ""

                # Get display name, if it exists.
                # try:
                #     display_name = self.component_display_names[triggered_element_id]
                #     # To be consistent, make sure display_name is a list, even if it's only
                #     # one element
                #     if isinstance(display_name, str):
                #         display_name = [display_name]
                # except:
                #     pass

                # Get new filter criteria.  How this happens depends on the type of
                # element that was triggered.

                if triggered_element_type == "ResetButton":
                    # If the element triggered was the reset button, reset filter
                    # criteria
                    self.controller.trigger_clear_filter_criteria()

                if triggered_element_type == "FilterChecklist":
                    # Note that filter criteria will be listed whether the box was
                    # already selected or not -- need to include a check somewhere
                    # (core?) to add or delete from list of selected values
                    new_filter_criteria = ctx.triggered[0]["value"]
                    self.controller.trigger_update_filter_criteria(
                        {database_field: new_filter_criteria}
                    )
                elif triggered_element_type == "DataFigure":
                    triggered_element_style = ui_element_info[triggered_element_id][
                        "properties"
                    ]["style"]
                    if triggered_element_style == "pie":
                        # If the object clicked was a graph, the new filter criteria
                        # will be a dict of information. Extract the specific criteria.
                        new_filter_criteria = [
                            ctx.triggered[0]["value"]["points"][0]["label"]
                        ]
                        self.controller.trigger_update_filter_criteria(
                            {database_field: new_filter_criteria}
                        )
                    elif triggered_element_style == "bar":
                        # If the object clicked was a graph, the new filter criteria
                        # will be a dict of information. Extract the specific criteria.
                        new_filter_criteria = [
                            ctx.triggered[0]["value"]["points"][0]["x"]
                        ]
                        self.controller.trigger_update_filter_criteria(
                            {database_field: new_filter_criteria}
                        )
                    elif triggered_element_style == "scatter":
                        # When I wrote this code, "pointNumber" and "pointIndex" were
                        # equal.
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

            # Initialize lists to store outputs for the different UI element types
            new_table_data = []
            new_checklist_data = []
            new_figure_data = []
            # Go through each UI element that's an output of the callback
            for output_type in outputs_list:
                for ielement in output_type:
                    # Get information about the element
                    output_element_id = ielement["id"]["index"]
                    output_element_properties = self.presenter.get_element_properties(
                        output_element_id
                    )
                    output_element_type = output_element_properties["type"]
                    # Get updated data for the element and add it to the appropriate list
                    presenter_ui_element = self.presenter.ui_elements[
                        ui_element_ids.index(output_element_id)
                    ]
                    if output_element_type == "DataTable":
                        new_table_data.append(
                            buildui.get_data_table_contents(presenter_ui_element)
                        )
                    elif output_element_type == "FilterChecklist":
                        new_checklist_data.append(
                            buildui.get_checklist_selection(presenter_ui_element)
                        )
                    elif output_element_type == "DataFigure":
                        output_element_style = output_element_properties["style"]
                        data = presenter_ui_element.contents["df"]
                        title = presenter_ui_element.contents["title"]
                        if output_element_style == "pie":
                            new_figure_data.append(buildui.build_pie_chart(data, title))
                        elif output_element_style == "bar":
                            new_figure_data.append(buildui.build_bar_graph(data, title))
                        elif output_element_style == "scatter":
                            title = " vs. ".join(title)
                            new_figure_data.append(
                                buildui.build_scatter_plot(data, title)
                            )

            # Update tables
            # new_table_data = []
            # presenter_table_ids = {
            #     itable.id: idx for idx, itable in enumerate(self.presenter.data_tables)
            # }
            # for itable in outputs_list[0]:
            #     # Get ID of UI table
            #     ui_id = itable["id"]["index"]
            #     # Find table in the presenter with the same ID as the UI table
            #     presenter_id = presenter_table_ids[ui_id]
            #     # Add the updated data for the table to the list of data_table data
            #     new_table_data.append(
            #         buildui.get_data_table_contents(
            #             self.presenter.data_tables[presenter_id]
            #         )
            #         # dtable.df_to_dict(self.presenter.data_tables[presenter_id].df)
            #     )

            # # Update FilterChecklists
            # new_checklist_data = []
            # presenter_checklist_ids = {
            #     ichecklist.id: idx
            #     for idx, ichecklist in enumerate(self.presenter.checklists)
            # }
            # for ichecklist in outputs_list[1]:
            #     # Get ID of UI checklist
            #     ui_id = ichecklist["id"]["index"]
            #     # Find checklist in the presenter with the same ID as the UI checklist
            #     presenter_id = presenter_checklist_ids[ui_id]
            #     # Add the updated data for the checklist to the list of checklist data
            #     new_checklist_data.append(
            #         buildui.get_checklist_selection(
            #             self.presenter.checklists[presenter_id]
            #         )
            #         # self.presenter.checklists[presenter_id].selected_options
            #     )

            # # Update plots
            # presenter_plot_ids = {
            #     iplot.id: idx for idx, iplot in enumerate(self.presenter.graphs)
            # }
            # new_piechart_data = []
            # for iplot in outputs_list[2]:
            #     # Get ID of UI plot
            #     ui_id = iplot["id"]["index"]
            #     # Find plot in the presenter with the same ID as the UI plot
            #     presenter_id = presenter_plot_ids[ui_id]
            #     # Add the updated data for the plot to the list of piechart data
            #     new_piechart_data.append(
            #         buildui.build_figure(self.presenter.graphs[presenter_id])
            #         # fig.DashPieChart(self.presenter.graphs[presenter_id]).build().figure
            #     )
            # new_bargraph_data = []
            # for iplot in outputs_list[3]:
            #     # Get ID of UI plot
            #     ui_id = iplot["id"]["index"]
            #     # Find plot in the presenter with the same ID as the UI plot
            #     presenter_id = presenter_plot_ids[ui_id]
            #     # Add the updated data for the plot to the list of piechart data
            #     new_bargraph_data.append(
            #         buildui.build_figure(self.presenter.graphs[presenter_id])
            #         # fig.DashBarGraph(self.presenter.graphs[presenter_id]).build().figure
            #     )
            # new_scatterplot_data = []
            # for iplot in outputs_list[4]:
            #     # Get ID of UI plot
            #     ui_id = iplot["id"]["index"]
            #     # Find plot in the presenter with the same ID as the UI plot
            #     presenter_id = presenter_plot_ids[ui_id]
            #     # Add the updated data for the plot to the list of scatterplot data
            #     new_scatterplot_data.append(
            #         buildui.build_figure(self.presenter.graphs[presenter_id])
            #         # fig.DashScatterPlot(self.presenter.graphs[presenter_id])
            #         # .build()
            #         # .figure
            #     )

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
                new_figure_data,
                # new_piechart_data,
                # new_bargraph_data,
                # new_scatterplot_data,
            ]

    def launch_ui(self):
        """Build and run frontend"""
        if __name__ == "view_dash":

            self.build()
            self.app.run_server(debug=False)
