"""A table containing data and indicating the selection status of each row"""

import pandas as pd


class DataTableCore(pd.DataFrame):
    """Store data and filter criteria, and indicates which data meets the current filter
    criteria"""

    def __init__(self, df):
        selection_state_column_name = "selectionState"
        super(DataTableCore, self).__init__()
        # Store name of column indicating selection state of rows
        self.selection_state_column_name = selection_state_column_name
        # Check whether there is already a column for specifying whether the row is
        # selected.  If not, add one.
        if self.selection_state_column_name not in df.columns:
            df[selection_state_column_name] = True
        # Store dataframe
        self.df = df
        # Initialize place to store filter criteria -- will be a dict with key=column
        # name, val=allowable values
        self.filter_criteria = {}

    def set_filter(self, filter_criteria):
        """Set filter criteria as specified, and filter dataframe.  Overwrites previous
        filter criteria.

        Args:
            filter_criteria (dict): dict of criteria, with key=column name,
            val=allowable values.
        """

        self.filter_criteria = filter_criteria

        # Update selection status of rows
        self.apply_filter()

    def update_filter(self, new_filter_criteria):
        """Update filter criteria and filter dataframe.

        Args:
            new_filter_criteria (dict): dict of criteria, with key=column name,
            val=allowable values.  If a provided key already exists in the list of
            filter criteria, its value will be overwritten with the provided value.  If
            an existing key is not provided in new_filter_criteria, it will retain its
            original value.
        """

        # Find keys of new criteria
        new_filter_criteria_keys = list(new_filter_criteria.keys())
        # Check for existing filter criteria with the same key
        # existing_filter_criteria_keys = list(self.filter_criteria.keys())
        # Go through new criteria and update existing criteria.
        # NOTE:  This assumes that the vals in new_filter_criteria represent ALL the
        # allowable values for that key.
        for ikey in new_filter_criteria_keys:
            self.filter_criteria[ikey] = new_filter_criteria[ikey]

        # Update selection status of rows
        self.apply_filter()

    def clear_filter(self):
        """Remove all filter criteria and reset dataframe selection status."""

        self.filter_criteria = {}

        # Update selection status of rows
        self.apply_filter()

    def apply_filter(self):
        """Determine which rows of a DataTable meet filter criteria placed on columns."""

        # If there are no filter criteria, assume all rows are selected
        if all(ele == [] for ele in list(self.filter_criteria.values())):
            self.df[self.selection_state_column_name] = True
        else:
            # Initialize list containing one list for each filter criterion
            is_row_selected = [[] for _ in range(len(self.df))]

            # For each criterion, find out if each row meets the criterion or not and
            # add this information as additional elements to each list inside the
            # selected_rows list.
            # NOTE: Replace isin by e.g. > == etc. to do more complicated comparisons
            for iCriteria, iVal in self.filter_criteria.items():
                if len(iVal) > 0:
                    is_row_selected = [
                        x + [y]
                        for x, y in zip(is_row_selected, self.df[iCriteria].isin(iVal))
                    ]
                else:
                    # Sometimes there might be an criteria with no values listed; in
                    # that case, don't do anything
                    pass

            # Only accept rows where all criteria are met
            is_row_selected = [all(x) for x in is_row_selected]
            # Replace the column in the dataframe that denotes whether a row is selected
            # or not
            self.df[self.selection_state_column_name] = is_row_selected

    def select_rows(self, row_inds):
        """Select rows of dataframe based on row indices

        Args:
            row_inds (list): list of row indices as integers
        """
        # I also tried .loc but got an error.  A good description of the differences
        # between .loc and .iloc (which might be relevant in future if we label the rows
        # of the dataframe) is here: https://stackoverflow.com/a/55884102
        # self.df = self.df.iloc[row_inds]

        # Initialize selection status for all rows of dataframe to False
        is_row_selected = [False for _ in range(len(self.df))]
        # Set selection status to True for rows corresponding to selected points
        for idx in row_inds:
            is_row_selected[idx] = True
        # Replace the column in the dataframe that denotes whether a row is selected or
        # not
        self.df[self.selection_state_column_name] = is_row_selected

    def get_selected_rows(self):
        """Remove dataframe rows not contained in the selection-state column

        Returns:
            filtered_df (dataframe):  dataframe (1) without the selection-state column
            and (2) with only selected rows
        """

        # Drop any unselected rows.  Use the default of inplace=False so that df.drop
        # returns a new dataframe rather than modifying the original dataframe.
        filtered_df = self.df.drop(
            self.df[self.df[self.selection_state_column_name] == False].index
        )
        # Remove column denoting selection state.  Use inplace=True so that df.drop
        # modifies the dataframe it's called on, rather than returning a new dataframe.
        filtered_df.drop([self.selection_state_column_name], axis=1, inplace=True)
        return filtered_df
