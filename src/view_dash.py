"""Builds a user interface using Dash"""

from dash import Dash, html, Input, Output, ctx, State, MATCH, ALL
import dash_bootstrap_components as dbc  # also see dash-mantine-components
import dash_trich_components as dtc  # alternative for carousel: dash_slick
import dash_mantine_components as dmc

from view import View
import builduielements_dash


class DashView(View):
    """Use a Dash dashboard for the user interface

    Args:
        View (View): this class is based on the generic View class
    """

    def __init__(self):
        """Define Dash as a frontend"""
        super().__init__()

        self.app = Dash(
            __name__,
            external_stylesheets=[
                dbc.themes.BOOTSTRAP,
                dbc.icons.FONT_AWESOME,
            ],
            assets_folder="../assets",
        )

        self.app.title = "Beaverdam"

    def __get_image(self, image_file_name, image_height):
        """Get an image from the assets folder

        Args:
            image_file_name (str): name of the image file.  The file should be located
            in the assets folder.
            image_height (str):  height of the displayed image (pixels)

        Returns:
            the image as an html component
        """
        return html.Img(
            src=Dash.get_asset_url(self.app, image_file_name), height=image_height
        )

    def build_layout(self):
        """Assemble elements of the user interface"""

        # Define some parameters for UI
        is_page_fluid = True
        header_height = "56px"
        logo_file_name = "beaverdam-logo_long.png"
        # Options for the carousel displaying figures
        n_figures_to_show = 2
        n_figures_to_scroll = 1
        carousel_margin_bottom = "5%"
        carousel_margin_side = "2.5%"
        # Here are options for the graph layout -- use graph_object.update_layout() to
        # set them after creating a Plotly graph object "graph_object"
        # https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html
        #
        # A list of Plotly modebar buttons is here:
        # https://plotly.com/python/configuration-options/#removing-modebar-buttons
        # Make sure that you give the list of modebar buttons as [[ buttonNames ]]
        plotly_config_options_base = {
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtons": [["toImage"]],
        }
        # Note that if you redefine a key in a plot-specific dict of config options, it
        # will override the values in the corresponding key of the base options, so if
        # you want to add on to base options you have to include the base value in the
        # plot-specific value alongside the additional options.
        plotly_config_options_pie = {}
        plotly_config_options_bar = {}
        plotly_config_options_scatter = {
            "modeBarButtons": [
                plotly_config_options_base["modeBarButtons"][0]
                + [
                    "zoom2d",
                    "pan2d",
                    "select2d",
                    "lasso2d",
                ]
            ]
        }

        ui_elements = self.ui_elements

        # Populate UI elements for each UI component, from Presenter information
        checklist_elements = []
        applied_filter_elements = []
        datatable_elements = []
        figure_elements = []
        for key, val in ui_elements.items():
            element_properties = val["properties"]
            element_id = element_properties["id"]
            element_type = element_properties["type"]
            if "style" in element_properties:
                element_style = element_properties["style"]
            element_contents = val["contents"]
            if element_type == "DataTable":
                datatable_elements.append(
                    dbc.Container(
                        [
                            builduielements_dash.build_data_table_label(
                                element_properties["current_num_records"],
                                element_properties["initial_num_records"],
                                id=element_id + "_label",
                                element_type="TextOutput",
                            ),
                            builduielements_dash.build_data_table(
                                id=element_id,
                                element_type=element_type,
                                data=element_contents["df"],
                            ),
                        ],
                        style={"max-width": "max-content"},
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
            elif element_type == "SelectedCriteria":
                applied_filter_elements.append(
                    builduielements_dash.build_chip_group(
                        id=element_id,
                        element_type=element_type,
                        items=element_contents["items"],
                        title=element_contents["title"],
                    )
                )
            elif element_type == "DataFigure":
                ielement = []
                igraph = []
                fig_config_options = {}
                if element_style == "pie":
                    igraph = builduielements_dash.build_pie_chart(
                        data=element_contents["df"],
                        title=element_contents["title"],
                    )
                    fig_config_options = {
                        **plotly_config_options_base,
                        **plotly_config_options_pie,
                    }
                elif element_style == "bar":
                    igraph = builduielements_dash.build_bar_graph(
                        data=element_contents["df"],
                        title=element_contents["title"],
                    )
                    fig_config_options = {
                        **plotly_config_options_base,
                        **plotly_config_options_bar,
                    }
                elif element_style == "scatter":
                    igraph = builduielements_dash.build_scatter_plot(
                        data=element_contents["df"],
                        title=element_contents["title"],
                    )
                    fig_config_options = {
                        **plotly_config_options_base,
                        **plotly_config_options_scatter,
                    }
                # Create the plot
                ielement = builduielements_dash.build_data_figure(
                    graph_object=igraph,
                    id=element_id,
                    element_type=element_type,
                    config=fig_config_options,
                )
                figure_elements.append(ielement)

        # Assemble elements into the different UI panels
        # list1.extend(list2) and list1 += list2 are equivalent:
        #   https://stackoverflow.com/a/56407963
        topbar_elements = []
        sidebar_elements = []
        mainpanel_elements = []
        topbar_elements.append(self.__get_image(logo_file_name, header_height))
        sidebar_elements.append(
            builduielements_dash.build_button("Reset", "ResetButton")
        )
        sidebar_elements.extend(applied_filter_elements)
        sidebar_elements.extend(checklist_elements)
        mainpanel_elements.append(
            dtc.Carousel(
                figure_elements,
                id="FigureGallery",
                dots=True,
                arrows=True,
                infinite=True,
                speed=500,
                slides_to_show=n_figures_to_show,
                slides_to_scroll=n_figures_to_scroll,
                style={
                    "margin-bottom": carousel_margin_bottom,
                    "margin-left": carousel_margin_side,
                    "margin-right": carousel_margin_side,
                },
            )
        )
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

    def register_callbacks(self):
        """Define actions that occur on user interaction; update frontend appropriately

        Returns:
            Updated versions of checklists, plots, and tables
            Resets clickData to None for all plots
        """
        app = self.app

        @app.callback(
            Output({"type": "DataTable", "index": ALL}, "data"),
            Output({"type": "FilterChecklist", "index": ALL}, "value"),
            Output({"type": "DataFigure", "index": ALL}, "figure"),
            Output({"type": "DataFigure", "index": ALL}, "clickData"),
            Output({"type": "TextOutput", "index": ALL}, "children"),
            Output({"type": "SelectedCriteria", "index": ALL}, "children"),
            Input({"type": "ResetButton", "index": ALL}, "n_clicks"),
            Input({"type": "FilterChecklist", "index": ALL}, "value"),
            Input({"type": "DataFigure", "index": ALL}, "clickData"),
            Input({"type": "DataFigure", "index": ALL}, "selectedData"),
            Input({"type": "SelectedCriteria", "index": ALL}, "value"),
        )
        def filter_data(
            resetButtonClicks,
            checklistValue,
            figureClickData,
            figureSelectedData,
            chipData,
        ):
            """Detect clicks on user interface then filter and display appropriately

            Args:
                resetButtonClicks (_type_): trigger when reset button clicked
                checklistValue (_type_): trigger when checklist selection changes
                figureClickData (_type_): trigger when figures clicked
                figureSelectedData (_type_): trigger when data in a figure (e.g.
                scatterplot) is selected

            Returns:
                list: contains one list for each detected output
            """
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

                # Find the database field(s) represented by the clicked element.  Set
                # this to "" if the UI element doesn't have a field (e.g. chips) or
                # isn't in the Presenter's list of UI elements (e.g. reset button).
                database_field = ui_element_info.get(triggered_element_id, "")
                if database_field != "":
                    database_field = database_field["properties"].get("field", "")
                if isinstance(database_field, list):
                    database_field = database_field[0]

                # Get new filter criteria.  How this happens depends on the type of
                # element that was triggered.
                if triggered_element_type == "ResetButton":
                    self.controller.trigger_clear_filter_criteria()

                elif triggered_element_type == "FilterChecklist":
                    # Checking a checkbox should remove any direct selection of rows,
                    # e.g. from a scatter plot
                    self.controller.trigger_undo_row_selection()
                    # Apply the new criteria
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

                        # Get indices of selected points in the plotted dataframe
                        selected_rows = [
                            point["pointIndex"]
                            for point in ctx.triggered[0]["value"]["points"]
                        ]
                        # Convert to the index in the main dataframe, which is the
                        # subject ID
                        selected_rows = list(
                            ui_element_info[triggered_element_id]["contents"]["df"]
                            .iloc[selected_rows]
                            .index
                        )
                        # Select the appropriate rows
                        self.controller.trigger_select_dataframe_rows(selected_rows)

                elif triggered_element_type == "SelectedCriteria":
                    existing_filter_criteria = (
                        self.presenter.core.data_table.get_filter_criteria()
                    )
                    filter_criteria_to_remove = ctx.triggered[0]["value"]
                    # Clicking a chip removes that criterion from the filter criteria.
                    # Be careful to not modify existing_filter_criteria, because this
                    # will also modify the actual filter criteria in the datatable.
                    #
                    # TODO:  be robust to criterion which have the same value but come
                    # from different filters, e.g. keep track of which element changed
                    # each filter criterion, and store alongside the criterion (e.g. in
                    # the "value" property of a chip), or add the filter title to the
                    # property in the text on the chip.
                    if filter_criteria_to_remove == "manual selection":
                        # We grouped scatterplot selection, with the "row_index" key,
                        # into a "manual selection" chip.  Use the original key to
                        # select criteria to remove.
                        filter_criteria_to_remove = "row_index"
                    new_filter_criteria = {}
                    for criterion, val in existing_filter_criteria.items():
                        # Go through each existing filter criterion and see which (if
                        # any) elements from it to keep
                        if filter_criteria_to_remove == criterion:
                            # If the chip represents a criterion (e.g. row_index),
                            # delete all values in the criterion
                            new_filter_criteria[criterion] = []
                        elif filter_criteria_to_remove in val:
                            # If the chip represents a single element, keep only the
                            # other elements in that criterion
                            new_filter_criteria[criterion] = [
                                x for x in val if x not in filter_criteria_to_remove
                            ]
                        else:
                            # If a criterion isn't affected by the selected chip, keep
                            # it the same
                            new_filter_criteria[criterion] = val
                    self.controller.trigger_update_filter_criteria(new_filter_criteria)

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
            new_figure_clickdata = []
            new_text_output = []
            new_chips = []
            # Go through each UI element that's an output of the callback
            for output_type in outputs_list:
                for ielement in output_type:
                    # Get the element ID
                    try:
                        output_element_id = ielement["id"]["index"]
                        # We already make labels update automatically with their associated
                        # element
                        if "_label" not in output_element_id:
                            output_element_properties = (
                                self.presenter.get_element_properties(output_element_id)
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
                                new_text_output.append(
                                    str(
                                        output_element_properties["current_num_records"]
                                    )
                                )
                            elif output_element_type == "FilterChecklist":
                                new_checklist_data.append(
                                    builduielements_dash.get_checklist_selection(
                                        presenter_ui_element
                                    )
                                )
                            elif output_element_type == "DataFigure":
                                if ielement["property"] == "figure":
                                    output_element_style = output_element_properties[
                                        "style"
                                    ]
                                    data = presenter_ui_element.contents["df"]
                                    title = presenter_ui_element.contents["title"]
                                    if output_element_style == "pie":
                                        new_figure_data.append(
                                            builduielements_dash.build_pie_chart(
                                                data, title
                                            )
                                        )
                                    elif output_element_style == "bar":
                                        new_figure_data.append(
                                            builduielements_dash.build_bar_graph(
                                                data, title
                                            )
                                        )
                                    elif output_element_style == "scatter":
                                        new_figure_data.append(
                                            builduielements_dash.build_scatter_plot(
                                                data, title
                                            )
                                        )
                                elif ielement["property"] == "clickData":
                                    # This fixes a bug in Dash where clicking the same
                                    # figure section (e.g. bar in a bar graph) multiple
                                    # times in a row doesn't fire the callback.  See bug
                                    # report here:
                                    # https://github.com/plotly/dash/issues/1300
                                    new_figure_clickdata.append(None)
                            elif output_element_type == "SelectedCriteria":
                                # Update chips.  Make sure to modify a COPY of the
                                # applied criteria, or else you will modify the actual
                                # filter criteria from the datatable.
                                chip_criteria = dict(
                                    self.presenter.core.data_table.get_filter_criteria()
                                )
                                if "row_index" in chip_criteria.keys():
                                    # Put any filter criteria originating from selecting
                                    # scatterplot points into single "custom criteria"
                                    # chip.
                                    if len(chip_criteria["row_index"]) > 0:
                                        chip_criteria["row_index"] = "manual selection"
                                chip_criteria_values = []
                                for val in chip_criteria.values():
                                    if isinstance(val, str):
                                        chip_criteria_values.append(val)
                                    else:
                                        chip_criteria_values.extend(val)
                                new_chips.append(
                                    builduielements_dash.build_chips(
                                        chip_criteria_values
                                    )
                                )
                    except:
                        pass

            return [
                new_table_data,
                new_checklist_data,
                new_figure_data,
                new_figure_clickdata,
                new_text_output,
                new_chips,
            ]

    def launch_ui(self):
        """Build and run frontend"""
        if __name__ == "view_dash":

            self.build_layout()
            self.register_callbacks()
            self.app.run_server(debug=False)
