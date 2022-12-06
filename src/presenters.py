"""Prepare data for visualization
"""
from dash import dcc, dash_table
import plotly.express as px


class DataTable:
    """Store data to display in a table"""

    def __init__(self, df, presenter):
        # Choose the correct presenter class and create a datatable of that class
        pass


class DashDataTable(DataTable):
    """Format dataframe for Dash dashboard"""

    def __init__(self, id, df):
        """Format a dataframe to be displayed by a Dash DataTable

        Args:
            df (Pandas dataframe): data to be shown in the table, with column names
            corresponding to the column names that should be in the table
        """
        self.id = id
        self.df = df
        self.data = df.to_dict("records")
        self.columns = [{"name": i, "id": i} for i in df.columns]

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
