"""Prepare data for visualization
"""

import datatablepresenter as datatable
import datafigurepresenter as datafigure
import filterchecklistpresenter as checklist


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

        # Make data table
        self.data_tables = [datatable.DataTablePresenter(self.core.data_table)]

        # Make graphs
        self.graphs = []
        for plot_info in self.cfg["plots"].values():
            if plot_info["plot_type"] == "pie":
                self.graphs.append(
                    datafigure
                .PieChartPresenter(
                        data_table=self.core.data_table,
                        col_to_plot=plot_info["data_field"],
                        title=plot_info["data_field"],
                    )
                )
            elif plot_info["plot_type"] == "bar":
                self.graphs.append(
                    datafigure
                .BarGraphPresenter(
                        data_table=self.core.data_table,
                        col_to_plot=plot_info["data_field"],
                        title=plot_info["data_field"],
                    )
                )
            elif plot_info["plot_type"] == "scatter":
                self.graphs.append(
                    datafigure
                .ScatterPlotPresenter(
                        data_table=self.core.data_table,
                        col_to_plot=plot_info["data_field"],
                        title=plot_info["data_field"],
                    )
                )
            else:
                pass

        # Make checklists
        self.checklists = []
        for ichecklist in self.cfg["filters"]["headings"]:
            self.checklists.append(
                checklist.FilterChecklistPresenter(
                    metadata_source=self.core.db, display_name=ichecklist
                )
            )

    def update(self):
        """Apply the current filter to all UI elements"""
        for itable in self.data_tables:
            itable.update(self.core.data_table)
        for igraph in self.graphs:
            igraph.update(self.core.data_table)
        for ichecklist in self.checklists:
            ichecklist.update(self.core.data_table.filter_criteria)
