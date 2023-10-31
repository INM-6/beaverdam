"""Prepare data for visualization
"""

from uielement import DataTable, FilterChecklist, DataFigure, SelectedCriteria


class Presenter:
    """Collects and prepares data so it's ready to be presented"""

    def __init__(self, cfg):
        """Store configuration information

        Args:
            cfg (ConfigParser):  contains a dict with information from config file.
            Required sections:  filters, plots
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
        self.ui_elements.append(DataTable(self.core.data_table))

        # Make checklists
        for ichecklist in self.cfg.get_section("filters")["headings"]:
            self.ui_elements.append(
                FilterChecklist(
                    source=self.core.data_table.df,
                    field=ichecklist,
                    checklist_title=ichecklist,
                    selected_options=[],
                )
            )

        # Make graphs
        for iplot in self.cfg.get_section("plots").values():
            self.ui_elements.append(
                DataFigure(
                    data_table=self.core.data_table,
                    field=iplot["data_field"],
                    title=iplot["data_field"],
                    style=iplot["plot_type"],
                )
            )

        # Make list of applied filters
        if (len(self.cfg.get_section("filters")["headings"]) > 0) | (
            len(self.cfg.get_section("plots").values()) > 0
        ):
            self.ui_elements.append(SelectedCriteria(title="Applied filters", items=[]))

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
