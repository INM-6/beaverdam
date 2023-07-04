"""Information to create plots and figures in a user interface"""

import uielementpresenter as uiobj


class DataFigurePresenter(uiobj.UIElementPresenter):
    """Store information to generate figures"""

    def __init__(self, data_table, field=[], col_labels={}, title=[]):
        """Store information to plot a figure from data

        Args:
            data_table (DataTableCore): object with data_table.df containing the
            dataframe with data to plot, and data_table.selection_state_column_names
            giving the name of the column indicating the selection state of each row
            field (string or list of strings matching dataframe column labels):
            which columns of the dataframe contain data to plot
            col_labels (dict, optional): labels to use for each column of data, if you
            don't want to use the existing dataframe column labels. keys = new names to
            display, vals = column names in df. Defaults to {}.
            title (str): title of resulting figure.  Defaults to [].
        Returns:
            self.graph_type (str):  type of graph to plot
            self.df (dataframe):  dataframe containing data to plot and columns named
            with display names
            self.title (str):  title of plot
        """
        super().__init__()

        self.graph_type = "undefined"

        # Make sure the columns to plot are given as a list, even if only a single
        # string is given.  If you subset a column from a dataframe with a string, it
        # returns a series rather than a dataframe, and this screws up future
        # operations.
        if isinstance(field, str):
            field = [field]
        self.field = field

        # Filter dataframe
        self.df = data_table.get_selected_rows()

        # Extract the specified columns; if none are specified, keep the whole dataframe
        if len(field) > 0:
            # Make sure the column(s) are given as a list
            if isinstance(field, list) is not True:
                field = [field]
            # Extract the columns
            self.df = self.df[field].copy()
        else:
            pass

        # Rename columns
        self.col_labels = col_labels
        self.df = uiobj.rename_df_columns(self.df, self.col_labels)

        # Set title
        self.title = title

    def update(self, data_table):
        """Update figure to reflect the current selection state of backend data

        Args:
            data_table (DataTableCore): backend data table containing all rows and
            columns and their selection states
        """
        # Filter dataframe
        self.df = data_table.get_selected_rows()

        # Extract the specified columns; if none are specified, keep the whole dataframe
        if len(self.field) > 0:
            self.df = self.df[self.field].copy()
        else:
            pass

        # Rename columns
        self.df = uiobj.rename_df_columns(self.df, self.col_labels)


class PieChartPresenter(DataFigurePresenter):
    """Store information to generate pie charts"""

    def __init__(self, data_table, field=[], col_labels={}, title=[]):
        """Get information for pie chart
        Optionally include information for custom title, labels, etc.

        Args:
            data_table (DataTableCore): backend data table containing data to plot
            field (list, optional): which columns in the data table to plot.
            Defaults to [].
            col_labels (dict, optional): which labels to display for each plotted
            column. Defaults to {}.
            title (list, optional): title for the figure. Defaults to [].
        """
        super().__init__(data_table, field, col_labels, title)
        self.graph_type = "pie"


class BarGraphPresenter(DataFigurePresenter):
    """Store information to generate bar graphs"""

    def __init__(self, data_table, field=[], col_labels={}, title=[]):
        """Get information for bar graph
        Optionally include information for custom title, labels, etc.

        Args:
            data_table (DataTableCore): backend data table containing data to plot
            field (list, optional): which columns in the data table to plot.
            Defaults to [].
            col_labels (dict, optional): which labels to display for each plotted
            column. Defaults to {}.
            title (list, optional): title for the figure. Defaults to [].
        """
        super().__init__(data_table, field, col_labels, title)
        self.graph_type = "bar"


class ScatterPlotPresenter(DataFigurePresenter):
    """Store information to generate scatter plots"""

    def __init__(self, data_table, field=[], col_labels={}, title=[]):
        """Get information for scatter plot
        Optionally include information for custom title, labels, etc.

        Args:
            data_table (DataTableCore): backend data table containing data to plot
            field (list, optional): which columns in the data table to plot.
            Defaults to [].
            col_labels (dict, optional): which labels to display for each plotted
            column. Defaults to {}.
            title (list, optional): title for the figure. Defaults to [].
        """
        super().__init__(data_table, field, col_labels, title)
        self.graph_type = "scatter"
        # Reset title
        self.title = " vs. ".join(self.title)
