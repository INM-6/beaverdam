"""A table containing data and indicating the selection status of each row."""

import pandas as pd


def _is_value_in_criteria(x, criteria):
    """Find if a value is contained in a list of criteria.

    Args:
        x (anything): the value you want to check
        criteria (list):  the list of criteria, of which x
        should meet at least one to be accepted

    Returns:
        bool: whether or not x meets any of the criteria

    """
    if isinstance(x, list):
        is_contained = any([True for i in x if i in criteria])
    elif x is None:
        is_contained = False
    else:
        is_contained = x in criteria
    return is_contained


class DataTableCore(pd.DataFrame):
    """Store data and filter criteria; indicates which data meets current filter criteria."""

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
        """Set filter criteria and filter dataframe.  Overwrites previous filter criteria.

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
        # If there are no filter criteria, accept all rows
        if all(ele == [] for ele in list(self.filter_criteria.values())):
            is_row_selected = [True for _ in range(len(self.df))]

        # If there are filter criteria, accept only rows which meet all criteria
        else:
            # Initialize list containing one list for each filter criterion
            is_row_selected = [[] for _ in range(len(self.df))]

            # For each criterion, find out if each row meets the criterion or not and
            # add this information as additional elements to each list inside the
            # selected_rows list.
            for iCriteria, iVal in self.filter_criteria.items():
                if len(iVal) > 0:
                    if iCriteria == "row_index":
                        # Initialize selection status for all rows of dataframe to False
                        is_criterion_met = [False for _ in range(len(self.df))]
                        # Set selection status to True for rows corresponding to
                        # selected points
                        df_row_indices = list(self.df.index)
                        for row_num, idx in enumerate(df_row_indices):
                            if idx in self.filter_criteria["row_index"]:
                                is_criterion_met[row_num] = True
                    else:
                        is_criterion_met = self.df[iCriteria].apply(
                            _is_value_in_criteria, args=[iVal]
                        )

                    is_row_selected = [
                        x + [y] for x, y in zip(is_row_selected, is_criterion_met)
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
        """Select rows of dataframe based on row indices.

        Args:
            row_inds (list): list of row indices, as set in the target dataframe

        """
        self.update_filter({"row_index": row_inds})
        # Update selection status of rows
        self.apply_filter()

    def undo_row_selection(self):
        """Remove the filter criteria which selects rows based on row indices."""
        if "row_index" in list(self.filter_criteria.keys()):
            del self.filter_criteria["row_index"]

        # Update selection status of rows
        self.apply_filter()

    def get_selected_rows(self):
        """Remove dataframe rows not contained in the selection-state column.

        Returns
            filtered_df (dataframe):  dataframe (1) without the selection-state column
            and (2) with only selected rows

        """
        # Drop any unselected rows.  Use the default of inplace=False so that df.drop
        # returns a new dataframe rather than modifying the original dataframe.
        filtered_df = self.df.drop(
            self.df[self.df[self.selection_state_column_name] == False].index  # noqa: E712
        )
        # Remove column denoting selection state.  Use inplace=True so that df.drop
        # modifies the dataframe it's called on, rather than returning a new dataframe.
        filtered_df.drop([self.selection_state_column_name], axis=1, inplace=True)
        return filtered_df

    def get_filter_criteria(self):
        """Get filter criteria.

        Returns
            filter_criteria (dict): dict of criteria, with key=column name,
            val=allowable values

        """
        return self.filter_criteria

    def get_filter_criteria_values(self):
        """Get all the values for applied filter criteria.

        Returns
            filter_criteria_values (list): specified values for all filter criteria

        """
        filter_criteria_values = [
            item for sublist in self.filter_criteria.values() for item in sublist
        ]
        return filter_criteria_values
