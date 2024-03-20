"""Builds a user interface using Dash"""

from dash import (
    Dash,
    html,
    Input,
    Output,
    dcc,
    ctx,
    State,
    MATCH,
    ALL,
    clientside_callback,
)
import dash_bootstrap_components as dbc  # also see dash-mantine-components
import plotly.io as pio

from view import View
import builduielements_dash
import colours as bd_colours


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
                dbc.themes.SANDSTONE,
                dbc.icons.FONT_AWESOME,
            ],
            assets_folder="../assets",
        )

        self.app.title = "Beaverdam"

    def _get_image(self, image_file_name, image_height):
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

    def _build_color_mode_switch(self):
        switch_id = builduielements_dash.set_ui_object_id("switch")
        return html.Span(
            [
                dbc.Label(className="fa fa-moon", html_for=switch_id),
                dbc.Switch(
                    id=switch_id,
                    value=False,
                    className="d-inline-block ms-1",
                    persistence=True,
                ),
                dbc.Label(className="fa fa-sun", html_for=switch_id),
            ]
        )

    def build_layout(self):
        """Assemble elements of the user interface"""

        # Define some parameters for UI
        is_page_fluid = True
        header_height = "56px"
        logo_file_name = "beaverdam-logo_long.png"
        loading_indicator_type = "default"
        loading_indicator_color = bd_colours.beaverdam_red
        # Options for the carousel displaying figures
        n_figures_to_show = 3
        n_figures_to_scroll = 1
        carousel_margin_bottom = "5%"
        carousel_margin_side = "2.5%"

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
                    dcc.Loading(
                        id=builduielements_dash.set_ui_object_id("loading"),
                        type=loading_indicator_type,
                        color=loading_indicator_color,
                        children=builduielements_dash.build_chip_group(
                            id=element_id,
                            element_type=element_type,
                            items=element_contents["items"],
                            title=element_contents["title"],
                        ),
                    )
                )
            elif element_type == "DataFigure":
                ielement = builduielements_dash.build_data_figure(
                    graph_object=builduielements_dash.build_plot(
                        data=element_contents["df"],
                        title=element_contents["title"],
                        style=element_style,
                    ),
                    id=element_id,
                    element_type=element_type,
                )
                figure_elements.append(ielement)

        # Assemble elements into the different UI panels
        # list1.extend(list2) and list1 += list2 are equivalent:
        #   https://stackoverflow.com/a/56407963
        topbar_elements = []
        sidebar_elements = []
        mainpanel_elements = []
        topbar_elements.append(self._get_image(logo_file_name, header_height))
        topbar_elements.append(self._build_color_mode_switch())
        sidebar_elements.append(
            builduielements_dash.build_button("Reset", "ResetButton")
        )
        sidebar_elements.extend(applied_filter_elements)
        sidebar_elements.extend(checklist_elements)
        mainpanel_elements.append(
            builduielements_dash.build_carousel(
                figure_elements,
                n_figs=n_figures_to_show,
                n_scroll=n_figures_to_scroll,
                margin_bottom=carousel_margin_bottom,
                margin_side=carousel_margin_side,
            )
        )
        mainpanel_elements.extend(datatable_elements)

        # Build user interface
        self.app.layout = dbc.Container(
            [
                dbc.Navbar(
                    topbar_elements,
                    id="navbar",
                    style={
                        "height": header_height,
                        "padding": "var(--bs-navbar-padding-y) 1vmin",
                        "justify-content": "space-between",
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
            Output({"type": "DataTable", "index": ALL}, "children"),
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
            Input({"type": "switch", "index": ALL}, "value"),
        )
        def filter_data(
            resetButtonClicks,
            checklistValue,
            figureClickData,
            figureSelectedData,
            chipData,
            isSwitchOn,
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

                # Find the database field(s) represented by the clicked element.  Keep
                # this as '' if the UI element doesn't have a field (e.g. chips) or
                # isn't in the Presenter's list of UI elements (e.g. reset button).
                database_field = ui_element_info.get(triggered_element_id, "")
                if database_field != "":
                    database_field = database_field["properties"].get("field", "")
                if isinstance(database_field, list) and len(database_field) == 1:
                    # If the clicked element only represents one field, we can take it
                    # immediately.  If there is more than one field represented, we need
                    # to choose which to update later, because this can be different for
                    # different types of e.g. plots.
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
                    elif triggered_element_style == "box":
                        # Figure out if the user has selected points or the box part.
                        if (
                            "hoverOnBox"
                            in ctx.triggered[0]["value"]["points"][0].keys()
                        ):
                            # The user has clicked a box.  Assume that they want to
                            # filter by the x category (rather than only including
                            # points inside the box, i.e. non-outliers) (this is the
                            # same as the bar graph case).
                            new_filter_criteria = [
                                ctx.triggered[0]["value"]["points"][0]["x"]
                            ]
                            self.controller.trigger_update_filter_criteria(
                                {database_field[1]: new_filter_criteria}
                            )
                        else:
                            # The user has clicked on or selected multiple outliers.
                            # Filter by the dataframe row (this is the same as the
                            # scatterplot case)
                            #
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
                    # Get the criterion name and value of the clicked chip
                    criterion_name, criterion_value = (
                        builduielements_dash.decode_criterion_info(
                            filter_criteria_to_remove
                        )
                    )
                    # Clicking a chip removes that criterion from the filter criteria.
                    # Be careful to not modify existing_filter_criteria, because this
                    # will also modify the actual filter criteria in the datatable.
                    new_filter_criteria = {}
                    for criterion, val in existing_filter_criteria.items():
                        # Go through each existing filter criterion and see which (if
                        # any) elements from it to keep
                        if criterion == "row_index":
                            # If the chip representing manual selection was selected,
                            # remove all these criteria
                            new_filter_criteria[criterion] = []
                        elif criterion == criterion_name:
                            # Keep only the other elements in that criterion.  Using
                            # .remove() was the best solution I found that was also
                            # robust to bool.  Make sure to do .remove() separately from
                            # assigning the result, because since .remove() doesn't
                            # return anything you get e.g. a=None if you try a =
                            # val.remove(b)
                            val.remove(criterion_value)
                            new_filter_criteria[criterion] = val
                            # Removing the last criterion using .remove() results in
                            # None, but we want an empty list.  Don't just remove the
                            # entire entry from the criteria dict, or the filter update
                            # won't work because it won't know which criterion to
                            # update.
                            if new_filter_criteria[criterion] is None:
                                new_filter_criteria[criterion] = []
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
                        # We already make labels update automatically with their
                        # associated element
                        if "_label" not in output_element_id:
                            output_element_properties = (
                                self.presenter.get_element_properties(output_element_id)
                            )
                            output_element_type = output_element_properties["type"]
                            # Get updated data for the element and add it to the
                            # appropriate list
                            presenter_ui_element = self.presenter.ui_elements[
                                ui_element_ids.index(output_element_id)
                            ]
                            if output_element_type == "DataTable":
                                new_table_data.append(
                                    builduielements_dash.build_data_table_contents(
                                        presenter_ui_element.contents["df"]
                                    )
                                )
                                new_text_output.append(
                                    str(
                                        output_element_properties["current_num_records"]
                                    )
                                )
                            elif output_element_type == "FilterChecklist":
                                new_checklist_data.append(
                                    presenter_ui_element.contents["selected_options"]
                                )
                            elif output_element_type == "DataFigure":
                                if ielement["property"] == "figure":
                                    new_figure_data.append(
                                        builduielements_dash.build_plot(
                                            data=presenter_ui_element.contents["df"],
                                            title=presenter_ui_element.contents[
                                                "title"
                                            ],
                                            style=output_element_properties["style"],
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
                                    else:
                                        del chip_criteria["row_index"]
                                # Get values of each criterion to display in chips.
                                # Also get and store the criterion associated with the
                                # value, and the type of the value (e.g. int, str, bool)
                                # in the chip's value property.  This way, the
                                # criterion's value can be unambiguously associated with
                                # its criterion if the chip is clicked on.  We have to
                                # store all this as a string in the chip's value
                                # property, because unlike for e.g. a checklist item,
                                # Dash Mantine Component chips only take strings as
                                # values.
                                chip_criteria_values = []
                                chip_info = []
                                for key, val in chip_criteria.items():
                                    if isinstance(val, list):
                                        for ival in val:
                                            chip_criteria_values.append(ival)
                                            chip_info.append(
                                                builduielements_dash.encode_criterion_info(
                                                    key, ival
                                                )
                                            )
                                    else:
                                        chip_criteria_values.append(val)
                                        chip_info.append(
                                            builduielements_dash.encode_criterion_info(
                                                key, val
                                            )
                                        )
                                new_chips.append(
                                    builduielements_dash.build_chips(
                                        chip_criteria_values,
                                        item_info=chip_info,
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

        @app.callback(
            Output("navbar", "color"),
            Input({"type": "switch", "index": ALL}, "value"),
        )
        def change_theme(
            isSwitchOn,
        ):
            if isSwitchOn[0]:
                theme_type = "light"
                pio.templates.default = "main_light"
            else:
                theme_type = "dark"
                pio.templates.default = "main_dark"
            return theme_type

        clientside_callback(
            """ 
            (switchOn) => {
            switchOn[0]
                ? document.documentElement.setAttribute('data-bs-theme', 'light')
                : document.documentElement.setAttribute('data-bs-theme', 'dark')
            return [window.dash_clientside.no_update]
            }
            """,
            Output({"type": "switch", "index": ALL}, "id"),
            Input({"type": "switch", "index": ALL}, "value"),
        )

    def launch_ui(self):
        """Build and run frontend"""
        if __name__ == "view_dash":
            self.build_layout()
            self.register_callbacks()
            self.app.run(debug=False)
