"""Builds a user interface using Dash"""

import view
import builduielements_dash
from dash import Dash, html, Input, Output, ctx, State, MATCH, ALL
import dash_bootstrap_components as dbc


def get_image(app, image_file_name, image_height):
    """Get an image from the assets folder

    Args:
        app (Dash app):  the instance of the Dash app, with an appropriately-set
        assets_folder
        image_file_name (str): name of the image file.  The file should be located
        in the assets folder.
        image_height (str):  height of the displayed image (pixels)

    Returns:
        the image as an html component
    """
    return html.Img(src=Dash.get_asset_url(app, image_file_name), height=image_height)


class DashView(view.View):
    """Use a Dash dashboard for the user interface

    Args:
        view.View (View): this class is based on the generic View class
    """

    def __init__(self):
        """Define Dash as a frontend"""
        super().__init__()

        self.app = Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            assets_folder="../assets",
        )

    def build(self):
        # Define some parameters for UI
        is_page_fluid = True
        header_height = "56px"
        logo_file_name = "beaverdam-logo_long.png"

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
                    builduielements_dash.build_data_table(
                        id=element_id,
                        element_type=element_type,
                        data=element_contents["df"],
                    )
                )
            elif element_type == "FilterChecklist":
                checklist_elements.append(
                    builduielements_dash.build_filter_checklist(
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
                    igraph = builduielements_dash.build_pie_chart(
                        data=element_contents["df"],
                        title=element_contents["title"],
                    )
                elif element_style == "bar":
                    igraph = builduielements_dash.build_bar_graph(
                        data=element_contents["df"],
                        title=element_contents["title"],
                    )
                elif element_style == "scatter":
                    igraph = builduielements_dash.build_scatter_plot(
                        data=element_contents["df"],
                        title=element_contents["title"],
                    )
                # Create the plot
                ielement = builduielements_dash.build_data_figure(
                    graph_object=igraph, id=element_id, element_type=element_type
                )
                figure_elements.append(ielement)

        # Assemble elements into the different UI panels
        # list1.extend(list2) and list1 += list2 are equivalent:
        #   https://stackoverflow.com/a/56407963
        topbar_elements = []
        sidebar_elements = []
        mainpanel_elements = []
        topbar_elements.append(get_image(self.app, logo_file_name, header_height))
        sidebar_elements.append(
            builduielements_dash.build_button("Reset", "ResetButton")
        )
        sidebar_elements.extend(checklist_elements)
        mainpanel_elements.extend(figure_elements)
        mainpanel_elements.extend(datatable_elements)

        # Build user interface
        self.app.layout = dbc.Container(
            [
                dbc.Navbar(
                    topbar_elements,
                    style={
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
                            style={
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
                            style={},
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
            Input({"type": "ResetButton", "index": ALL}, "n_clicks"),
            Input({"type": "FilterChecklist", "index": ALL}, "value"),
            Input({"type": "DataFigure", "index": ALL}, "clickData"),
            Input({"type": "DataFigure", "index": ALL}, "selectedData"),
        )
        def filter_data(
            resetButtonClicks, checklistValue, figureClickData, figureSelectedData
        ):
            # Get id and type of element that was clicked
            triggered_element = ctx.triggered_id

            # Get information about each element
            ui_element_info = self.presenter.get_elements()
            # Get information to relate each element ID to its corresponding location in
            # the list of UI elements in Presenter
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

                # Get new filter criteria.  How this happens depends on the type of
                # element that was triggered.
                if triggered_element_type == "ResetButton":
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
                        new_filter_criteria = [
                            ctx.triggered[0]["value"]["points"][0]["label"]
                        ]
                        self.controller.trigger_update_filter_criteria(
                            {database_field: new_filter_criteria}
                        )
                    elif triggered_element_style == "bar":
                        new_filter_criteria = [
                            ctx.triggered[0]["value"]["points"][0]["x"]
                        ]
                        self.controller.trigger_update_filter_criteria(
                            {database_field: new_filter_criteria}
                        )
                    elif triggered_element_style == "scatter":
                        # When I wrote this code, "pointNumber" and "pointIndex" were
                        # equal.  Note that if px.scatter() uses a color parameter,
                        # pointNumber and pointIndex are no longer unique over all
                        # points in the plot -- in this case, you need to uniquely
                        # identify each point by combining curveNumber and one of
                        # pointNumber or pointIndex.  See info here:
                        # https://stackoverflow.com/a/70110314
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
                    # Get updated data for the element and add it to the appropriate
                    # list
                    presenter_ui_element = self.presenter.ui_elements[
                        ui_element_ids.index(output_element_id)
                    ]
                    if output_element_type == "DataTable":
                        new_table_data.append(
                            builduielements_dash.get_data_table_contents(
                                presenter_ui_element
                            )
                        )
                    elif output_element_type == "FilterChecklist":
                        new_checklist_data.append(
                            builduielements_dash.get_checklist_selection(
                                presenter_ui_element
                            )
                        )
                    elif output_element_type == "DataFigure":
                        output_element_style = output_element_properties["style"]
                        data = presenter_ui_element.contents["df"]
                        title = presenter_ui_element.contents["title"]
                        if output_element_style == "pie":
                            new_figure_data.append(
                                builduielements_dash.build_pie_chart(data, title)
                            )
                        elif output_element_style == "bar":
                            new_figure_data.append(
                                builduielements_dash.build_bar_graph(data, title)
                            )
                        elif output_element_style == "scatter":
                            new_figure_data.append(
                                builduielements_dash.build_scatter_plot(data, title)
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
                new_figure_data,
            ]

    def launch_ui(self):
        """Build and run frontend"""
        if __name__ == "view_dash":

            self.build()
            self.app.run_server(debug=False)
