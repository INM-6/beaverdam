"""Prepare data for visualization
"""

from dash import dcc

# import plotly.express as px
import pandas as pd


class DataTable:
    """Store data to display in a table"""

    def __init__(self, id, df, new_column_names={}):
        """Format a dataframe for display

        Args:
            id (str):  id of the resulting table element, e.g. in a dashboard
            df (Pandas dataframe): data to be shown in the table
            new_column_names (opt; dict):  keys = new column names to display, vals =
            column names in df.  If a column name is not specified in the dict, the
            original column name will be retained.
        Returns:
            self.id (str):  id, e.g. to use for the resulting table in a dashboard
            self.df (dataframe):  data to be shown in the table; column names are the
            same as column headers to display
            self.columns (list):  column names (same as the column names in self.df)
        """
        filter_col_name = "selectionState"
        self.id = id

        # Remove column denoting selection state
        if filter_col_name in df.columns:
            self.df = df.drop([filter_col_name], axis=1)
        else:
            self.df = df

        # Rename columns
        # Reverse the dict so keys=old names, vals=new names
        new_column_names = {y: x for x, y in new_column_names.items()}
        self.df.rename(columns=new_column_names, inplace=True)


class DataFigure:
    """Store information to generate figures"""

    def __init__(self, id, df, col_to_plot=[], col_labels={}):
        """Store information to plot a figure from data

        Args:
            id (str): id of the resulting figure element, e.g. in a dashboard
            df (dataframe): dataframe containing data to plot
            col_to_plot (list of strings matching dataframe column labels): which
            columns of the dataframe contain data to plot
            col_labels (dict, optional): labels to use for each column of data, if you
            don't want to use the existing dataframe column labels. keys = new names to
            display, vals = column names in df. Defaults to {}.
        Returns:
            self.id (str):  id of the resulting figure element
            self.graph_type (str):  type of graph to plot
            self.df (dataframe):  dataframe containing data to plot and columns named with display names
        """
        self.id = id
        self.graph_type = "undefined"
        # Extract the specified columns; if none are specified, keep the whole dataframe
        if len(col_to_plot) > 0:
            self.df = df[
                [col_to_plot]
            ].copy()  # df.loc[:, col_to_plot] # df.get(col_to_plot)
        else:
            self.df = df
        # Rename columns
        if len(col_labels) > 0:
            # Switch keys and vals so that keys=current col names, vals=new names
            col_labels = {y: x for x, y in col_labels.items()}
            # Rename columns
            self.df.rename(columns=col_labels, inplace=True)


class PieChart(DataFigure):
    """Store information to generate pie charts"""

    def __init__(self, id, df, col_to_plot=[], col_labels={}):
        super().__init__(id, df, col_to_plot, col_labels)
        self.graph_type = "pie"
        # TODO: Manipulate dataframe so that there is one column for categories and one for counts
        # Example:
        #   df:
        #           colName
        #       1   val1
        #       2   val1
        #       3   val2
        #   manipulated df:
        #       colName
        #       val1    2
        #       val2    1
        # self.df = pd.DataFrame(self.df.value_counts()).reset_index()


class FilterChecklist:
    """Information for lists of checkboxes to filter data"""

    def __init__(self, id, metadata_source, field_location, checklist_title=[]):
        """Set checklist properties and find options

        Args:
            id (str):  the id to assign to the corresponding Dash UI element
            metadata_source (MetadataSource):  information about where to find metadata
            field_location (str):  which metadata attribute the checklist represents, in a format
            which the MetadataSource accepts as a query.  E.g. for a MongoDbDatabase
            MetadataSource, use the path to the attribute in MongoDB.
            checklist_title (str):  title for the checklist (optional; if not given, field_location will be used)
        """
        self.id = id

        # Find options for the checklist
        # TODO:  improve query method so you don't have to put the self.field: 1 here
        self.checklist_options = metadata_source.query({}, {field_location: 1})
        self.checklist_options = (
            self.checklist_options[field_location].drop_duplicates().to_list()
        )

        # Set title for the checklist.  Default to field_location if checklist_title
        # isn't provided
        if len(checklist_title) > 0:
            self.title = checklist_title
        else:
            self.title = field_location
