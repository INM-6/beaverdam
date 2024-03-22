class Controller:
    """Define functions that can be called by View elements to trigger Core functions"""

    def __init__(self):
        pass

    def set_core(self, core_to_use):
        """Set backend logic

        Args:
            core_to_use (Core): backend logic, e.g. database access information, filter
            criteria, central data table, filtering functions
        """
        self.core = core_to_use

    def trigger_clear_filter_criteria(self):
        """Clear all filter criteria"""
        self.core.data_table.clear_filter()

    def trigger_update_filter_criteria(self, filter_criteria):
        """Filter for sessions meeting criteria"""
        self.core.data_table.update_filter(filter_criteria)

    def trigger_select_dataframe_rows(self, row_inds):
        """Select rows of dataframe containing selected sessions"""
        self.core.data_table.select_rows(row_inds)

    def trigger_undo_row_selection(self):
        """Remove direct selection of rows"""
        self.core.data_table.undo_row_selection()
