"""Prepare data for visualization
"""

import uielement


class Presenter:
    """Collects and prepares data so it's ready to be presented"""

    def __init__(self, cfg):
        """Store configuration information

        Args:
            cfg (namedtuple):  contains dicts for each heading of config file.  Example:

                cfg.headingName
                    {'key1': val1, 'key2': val2}
                cfg.headingName["key1"]
                    val1
                cfg.headingName["key2"]
                    val2

            Required headings:  filters, table, plots
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
        for ichecklist in self.cfg["filters"]["headings"]:
            self.ui_elements.append(
                uielement.FilterChecklist(
                    source=self.core.data_table.df,
                    field=ichecklist,
                    checklist_title=ichecklist,
                    selected_options=[],
                )
            )

        # Make graphs
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

    def update(self):
        """Apply the current filter to all UI elements"""
        for ielement in self.ui_elements:
            ielement.update(new_data_table=self.core.data_table)

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
