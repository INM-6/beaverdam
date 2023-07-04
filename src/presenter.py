"""Prepare data for visualization
"""

# import datatablepresenter as datatable
# import datafigurepresenter as datafigure
# import filterchecklistpresenter as checklist

import uielement as uielement


class Presenter:
    """Collects and prepares data so it's ready to be presented"""

    def __init__(self, cfg):
        """Store confituration information

        Args:
            cfg (namedtuple):  contains dicts for each heading of config file.  Example:

                cfg.headingName
                    {'key1': val1, 'key2': val2}
                cfg.headingName["key1"]
                    val1
                cfg.headingName["key2"]
                    val2

            Should contain headings:  plots, projections, queries
        """
        self.cfg = cfg

    def set_core(self, core_to_use):
        """Set backend logic

        Args:
            core_to_use (Core): backend logic, e.g. database access information, filter
            criteria, central data table, filtering functions
        """
        self.core = core_to_use
        # Load current info from core
        self.build()

    def build(self):
        """Assemble all information for user interface, e.g. plots, filters, data tables"""

        # TODO:  improvement: make this a dict, with keys as the element IDs
        self.ui_elements = []

        # Make data table
        self.ui_elements.append(uielement.DataTable(self.core.data_table))

        # Make checklists
        # self.checklists = []
        for ichecklist in self.cfg["filters"]["headings"]:
            self.ui_elements.append(
                uielement.FilterChecklist(
                    metadata_source=self.core.db,
                    field=ichecklist,
                    checklist_title=ichecklist,
                    selected_options=[],
                )
            )

        # Make graphs
        # self.graphs = []
        for iplot in self.cfg["plots"].values():
            if iplot["plot_type"] == "pie":
                self.ui_elements.append(
                    uielement.PieChart(
                        data_table=self.core.data_table,
                        field=iplot["data_field"],
                        title=iplot["data_field"],
                    )
                )
            elif iplot["plot_type"] == "bar":
                self.ui_elements.append(
                    uielement.BarGraph(
                        data_table=self.core.data_table,
                        field=iplot["data_field"],
                        title=iplot["data_field"],
                    )
                )
            elif iplot["plot_type"] == "scatter":
                self.ui_elements.append(
                    uielement.ScatterPlot(
                        data_table=self.core.data_table,
                        field=iplot["data_field"],
                        title=iplot["data_field"],
                    )
                )
            else:
                pass

        # Make data table
        # self.data_tables = [datatable.DataTablePresenter(self.core.data_table)]

        # # Make graphs
        # self.graphs = []
        # for plot_info in self.cfg["plots"].values():
        #     if plot_info["plot_type"] == "pie":
        #         self.graphs.append(
        #             datafigure.PieChartPresenter(
        #                 data_table=self.core.data_table,
        #                 field=plot_info["data_field"],
        #                 title=plot_info["data_field"],
        #             )
        #         )
        #     elif plot_info["plot_type"] == "bar":
        #         self.graphs.append(
        #             datafigure.BarGraphPresenter(
        #                 data_table=self.core.data_table,
        #                 field=plot_info["data_field"],
        #                 title=plot_info["data_field"],
        #             )
        #         )
        #     elif plot_info["plot_type"] == "scatter":
        #         self.graphs.append(
        #             datafigure.ScatterPlotPresenter(
        #                 data_table=self.core.data_table,
        #                 field=plot_info["data_field"],
        #                 title=plot_info["data_field"],
        #             )
        #         )
        #     else:
        #         pass

        # # Make checklists
        # self.checklists = []
        # for ichecklist in self.cfg["filters"]["headings"]:
        #     self.checklists.append(
        #         checklist.FilterChecklistPresenter(
        #             metadata_source=self.core.db, field=ichecklist
        #         )
        #     )

    def update(self):
        """Apply the current filter to all UI elements"""
        for ielement in self.ui_elements:
            ielement_type = ielement.properties["type"]
            if any(ielement_type == x for x in ["DataTable", "DataFigure"]):
                ielement.update(new_data_table=self.core.data_table)
            elif ielement_type == "FilterChecklist":
                try:
                    new_selected_options = self.core.data_table.filter_criteria[
                        ielement.properties["field"][0]
                    ]
                except:
                    # No current selections for the field this checklist represents
                    new_selected_options = []
                ielement.update(new_selected_options=new_selected_options)
            else:
                # Element type not defined
                pass
        # for itable in self.data_tables:
        #     itable.update(self.core.data_table)
        # for igraph in self.graphs:
        #     igraph.update(self.core.data_table)
        # for ichecklist in self.checklists:
        #     ichecklist.update(self.core.data_table.filter_criteria)

    def get_elements(self):
        """Get information about all elements in the Presenter

        Returns:
            ui_elements (dict):  information about each UI element (e.g. element ID and
            type) and contents of the element
        """
        ui_elements = {}

        for ielement in self.ui_elements:
            iproperties = ielement.get_properties()
            icontents = ielement.get_contents()
            # Note that storing the whole properties dict here is a bit stupid, because
            # we only need the keys that aren't "id".  However it is not so easy to
            # delete keys from a dict and store it as a new dict, plus it is a bit
            # stupid from a memory and speed perspective because you create an entirely
            # new dict.  This way, only a pointer to the original dict is stored, so we
            # are really only referencing it.
            ui_elements[iproperties["id"]] = {
                "properties": iproperties,
                "contents": icontents,
            }

        return ui_elements

    def get_element_properties(self, element_id):
        """Get the properties of an element, given the element's id

        Args:
            element_id (str):  the unique id of the element

        Returns:
            element_properties (dict):  properties of the element
        """
        all_elements = self.get_elements()
        element_properties = all_elements[element_id]["properties"]

        return element_properties
