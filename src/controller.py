class Controller:
    def __init__(self):
        pass

    def set_core(self, core_to_use):
        self.core = core_to_use

    def trigger_update_filter_criteria(self, filter_criteria):

        # Filter for sessions meeting criteria
        self.core.data_table.update_filter(filter_criteria)
