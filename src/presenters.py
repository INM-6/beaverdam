"""Prepare data for visualization
"""
from dash import dcc, dash_table
import plotly.express as px


class DataTable:
    """Store data to display in a table"""

    def __init__(self, id, df, presenter=""):
        filter_col_name = "selectionState"
        self.id = id
        # Remove column denoting selection state
        if filter_col_name in df.columns:
            self.df = df.drop([filter_col_name], axis=1)
        else:
            self.df = df
        # TODO:  Choose the correct presenter class and create a datatable of that class


class DashDataTable(DataTable):
    """Format dataframe for Dash dashboard"""

    def __init__(self, id, df, new_column_names={}):
        """Format a dataframe to be displayed by a Dash DataTable

        Args:
            id (str):  id of the resulting table element in the dashboard
            df (Pandas dataframe): data to be shown in the table, with column names
            corresponding to the column names that should be in the table
            new_column_names (opt; dict):  keys = column names in df, vals = new column
            names to display.  If a column name is not specified in the dict, the
            original column name will be retained.
        """
        super().__init__(id, df)
        self.data = self.df.to_dict("records")
        # Rename columns to use short human-readable names
        # TODO:  consider adding this to the DataTable __init__ instead
        if len(new_column_names) > 0:
            # For each column of the dataframe, check whether the column name is in the
            # list of new column names and replace it if needed; if it isn't in the
            # list, retain the original column name.  TODO:  add check for dict rather
            # than list
            self.columns = []
            for icol in self.df.columns:
                tmp_dict = {}
                tmp_dict["id"] = icol
                if icol in list(new_column_names.keys()):
                    tmp_dict["name"] = new_column_names[icol]
                else:
                    tmp_dict["name"] = icol
                self.columns.append(tmp_dict)

    def build(self):
        return dash_table.DataTable(
            id=self.id,
            data=self.data,
            columns=self.columns,
        )


class DataFigure:
    """Store information to generate figures"""

    def __init__(self, id, df):
        # Store the data to graph
        self.id = id
        self.df = df
        self.graph_type = ""
        self.presenter = ""


class PieChart(DataFigure):
    """Store information to generate pie charts"""

    def __init__(self, id, df):
        super().__init__(id, df)
        self.graph_type = "pie"


class DashPieChart(PieChart):
    """Information to generate a pie chart in Dash

    Args:
        graph_type (string) = 'pie'
        df (dataframe): dataframe with column containing the data to plot
        col_name (string): name of the column to plot
    """

    def __init__(self, id, df, col_name):
        super().__init__(id, df)
        self.presenter = "dash"
        self.col_name = col_name

    def build(self):
        return dcc.Graph(id=self.id, figure=px.pie(self.df, names=self.col_name))


class FilterChecklist:
    """Information for lists of checkboxes to filter data"""

    def __init__(self, id):
        # Choose the correct presenter subclass
        self.id = id


class DashFilterChecklist(FilterChecklist):
    """Information to generate a checklist in Dash"""

    def __init__(self, id, db_info, field):
        super().__init__(id)
        """Store the list of checkbox options

        Args:
            items (dict): checkbox items with keys = projection, vals = allowable values
            id (str):  the id to assign to the corresponding Dash UI element
            db_info (MongoDbDatabase):  information about where to find the database
            field (str):  the path to the database field which the checklist represents
        """
        self.db_info = db_info
        self.field = field

    def build(self):
        checklist_options = self.db_info.query({}, {self.field: 1})
        checklist_options = checklist_options[self.field].drop_duplicates().to_list()
        return dcc.Checklist(
            options=checklist_options, id=self.id, labelStyle={"display": "block"}
        )
