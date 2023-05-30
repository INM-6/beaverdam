"""Class and functions to format core information in preparation for making UI objects"""

import uuid


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


class UIElementPresenter:
    """General class for all user interface objects"""

    def __init__(self):
        """General attributes for all output objects"""
        # Set ID for UI element
        self.id = str(uuid.uuid4())
