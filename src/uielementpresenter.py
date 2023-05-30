"""Class and functions to create all objects that are visualized in a user interface"""

import uuid


class UIElementPresenter:
    """General class for all user interface objects"""

    def __init__(self):
        """General attributes for all output objects"""
        # Set ID for UI element
        self.id = str(uuid.uuid4())


def remove_unselected_rows(data_table):
    """Remove rows of a dataframe that aren't contained in the selection-state column

    Args:
        data_table (DataTable): DataTable with data_table.df containing the dataframe to
        be filtered and data_table.selection_state_column_name giving the name of the
        column of the dataframe containing the selection state of each row.
    Returns:
        pretty_df (dataframe):  dataframe WITHOUT (1) the selection-state column and
        (2) any unselected rows
    """

    if data_table.selection_state_column_name in data_table.df.columns:
        # Drop any unselected rows.  Use the default of inplace=False so that df.drop
        # returns a new dataframe rather than modifying the original dataframe.
        pretty_df = data_table.df.drop(
            data_table.df[
                data_table.df[data_table.selection_state_column_name] == False
            ].index
        )
        # Remove column denoting selection state.  Use inplace=True so that df.drop
        # modifies the dataframe it's called on, rather than returning a new dataframe.
        pretty_df.drop([data_table.selection_state_column_name], axis=1, inplace=True)
    else:
        pretty_df = data_table.df.copy(deep=True)
    return pretty_df


def rename_df_columns(df, col_name_dict):
    """Rename the columns of a dataframe

    Args:
        df (dataframe): dataframe whose columns should be renamed
        col_name_dict (dict): dictionary containing keys=new names, vals=old names
    Returns:
        renamed_df (dataframe): dataframe with renamed columns
    """
    # Reverse the dict so keys=old names, vals=new names
    col_name_dict_reversed = {y: x for x, y in col_name_dict.items()}
    renamed_df = df.rename(columns=col_name_dict_reversed)
    return renamed_df
