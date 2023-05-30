"""Information to create data tables in a user interface"""

import uielementpresenter as uiobj


class DataTablePresenter(uiobj.UIElementPresenter):
    """Store data to display in a table"""

    def __init__(self, data_table, new_column_names={}):
        """Format a dataframe for display

        Args:
            data_table (DataTableCore): data_table.df is a dataframe containing data to
            be shown in the table; data_table.selection_state_column_name gives the name
            of the column indicating the selections state of each row
            new_column_names (opt; dict):  keys = new column names to display, vals =
            column names in df.  If a column name is not specified in the dict, the
            original column name will be retained.
        Returns:
            self.df (dataframe):  data to be shown in the table; column names are the
            same as column headers to display
        """
        super().__init__()

        self.build(data_table, new_column_names)

    def build(self, data_table, new_column_names={}):
        """Create frontend data table

        Args:
            data_table (DataTableCore): backend data table containing all rows and
            columns new_column_names (dict, optional): dictionary containing keys=new
            column names, vals=original column names. Defaults to {}, which preserves
            original column names.
        """
        # Remove rows that won't be shown in data table
        self.df = uiobj.remove_unselected_rows(data_table)
        # Rename columns to human-readable names
        self.df = uiobj.rename_df_columns(self.df, new_column_names)

    def update(self, data_table, new_column_names={}):
        """Update frontend table to reflect current selection state of backend data

        Args:
            data_table (DataTableCore): backend data table containing all rows and
            columns and their selection states
            new_column_names (dict, optional): dictionary containing keys=new column
            names, vals=original column names. Defaults to {}, which preserves original
            column names.
        """
        # Remove rows that won't be shown in data table
        self.df = uiobj.remove_unselected_rows(data_table)
        # Rename columns to human-readable names
        self.df = uiobj.rename_df_columns(self.df, new_column_names)
