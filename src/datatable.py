"""General class for data tables"""

import uielement as uielement

class DataTable(uielement.UiElement):
    """Class for data tables"""

    def __init__(self, datatable_presenter_object):
        """Get and store data table options and other properties

        Args:
            datatable_presenter_object (DataTablePresenter): formatted data for the
            table
        """
        super().__init__(datatable_presenter_object)

        # Set type of UI element
        self.id["type"] = "DataTable"

        # Duplicate fields from datatable_presenter_object
        self.df = datatable_presenter_object.df

    def build(self):
        pass