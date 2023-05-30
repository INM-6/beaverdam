"""Dash data tables"""    

import datatable as datatable
from dash import dash_table

def df_to_dict(df):
    """Convert dataframe to the data format that Dash wants for a DataTable

    Args:
        df (dataframe): data to be shown in DataTable
    """
    return df.to_dict("records")

class DashDataTable(datatable.DataTable):

    def __init__(self, datatable_presenter_object):
        """Get and store data table options and other properties

        Args:
            datatable_presenter_object (DataTablePresenter): formatted data for the
            table
        """
        super().__init__(datatable_presenter_object)

    def build(self):
        """Build table for user interface

        Returns:
            dash_table.DataTable: Dash DataTable
        """
        return dash_table.DataTable(
            id=self.id,
            data=df_to_dict(self.df),
        )


